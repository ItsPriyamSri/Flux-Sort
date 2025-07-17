"""
AI classifier using gemini-3.1-flash-lite.

Design contract:
- Known extensions (handled by extension map) are NOT sent to Gemini.
- Files are batched into a single API call per classification session.
- Results are cached by (name, size, mtime) hash for 30 days.
- If api_key is absent or the call fails, falls back to extension-map results silently.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import ConfigManager
from .file_detector import FileCategory
from .file_scanner import ScanResult

# Gemini model string — confirmed GA May 2026
_GEMINI_MODEL = "gemini-3.1-flash-lite"
_CACHE_TTL_DAYS = 30
_CONFIDENCE_KNOWN = 0.97   # Confidence assigned to extension-map results
_CONFIDENCE_THRESHOLD = 0.70  # Below this → flagged for manual review in UI

_config_manager = ConfigManager()
_CACHE_FILE = _config_manager._get_default_config_dir() / "ai_cache.json"


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------

def _file_hash(name: str, size: int, mtime: float) -> str:
    raw = f"{name}|{size}|{mtime:.0f}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _load_cache() -> dict[str, Any]:
    if not _CACHE_FILE.exists():
        return {}
    try:
        with open(_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_cache(cache: dict[str, Any]) -> None:
    _CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    cutoff = time.time() - _CACHE_TTL_DAYS * 86400
    pruned = {k: v for k, v in cache.items() if v.get("cached_at", 0) > cutoff}
    try:
        with open(_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(pruned, f, indent=2)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# AIClassifier
# ---------------------------------------------------------------------------

class AIClassifier:
    """Classifies files using gemini-3.1-flash-lite with extension-map fallback."""

    async def classify(
        self,
        scan_result: ScanResult,
        taxonomy: list[Any],   # list[TaxonomyCategory]
        api_key: str,
    ) -> dict[str, Any]:
        """
        Classify all files in scan_result against the given taxonomy.

        Returns:
            {
                "classifications": [...],
                "ai_calls_made": int,
                "cached_results": int,
            }
        """
        cache = _load_cache()
        classifications: list[dict[str, Any]] = []
        to_classify: list[dict[str, Any]] = []
        ai_calls = 0
        cached = 0

        # Build a flat list of all files with their extension-map category
        all_files: list[tuple[str, str, int, float, str]] = []
        for category, file_list in scan_result.files_by_category.items():
            for fi in file_list:
                try:
                    mtime = fi.path.stat().st_mtime
                except OSError:
                    mtime = 0.0
                all_files.append((
                    fi.name, str(fi.path), fi.size, mtime, category.value
                ))

        # If no taxonomy defined, just return extension-map results
        if not taxonomy:
            return {
                "classifications": [
                    {
                        "name": name,
                        "path": path,
                        "category": ext_cat,
                        "confidence": _CONFIDENCE_KNOWN,
                        "reasoning": "Extension-map classification (no taxonomy defined)",
                        "ai_classified": False,
                    }
                    for name, path, _, _, ext_cat in all_files
                ],
                "ai_calls_made": 0,
                "cached_results": 0,
            }

        # Check cache; queue anything that misses
        for name, path, size, mtime, ext_cat in all_files:
            key = _file_hash(name, size, mtime)
            hit = cache.get(key)
            if hit:
                cached += 1
                classifications.append({
                    "name": name,
                    "path": path,
                    "category": hit["category"],
                    "confidence": hit["confidence"],
                    "reasoning": hit["reasoning"] + " (cached)",
                    "ai_classified": True,
                })
            else:
                to_classify.append({
                    "name": name,
                    "path": path,
                    "size_kb": round(size / 1024, 1),
                    "extension": Path(name).suffix.lower(),
                    "ext_category": ext_cat,
                    "hash": key,
                })

        # Call Gemini for uncached files
        if to_classify and api_key:
            ai_results = await self._call_gemini(to_classify, taxonomy, api_key)
            ai_calls = 1

            for item, ai in zip(to_classify, ai_results):
                cache[item["hash"]] = {
                    "category": ai["category"],
                    "confidence": ai["confidence"],
                    "reasoning": ai["reasoning"],
                    "cached_at": time.time(),
                }
                classifications.append({
                    "name": item["name"],
                    "path": item["path"],
                    "category": ai["category"],
                    "confidence": ai["confidence"],
                    "reasoning": ai["reasoning"],
                    "ai_classified": True,
                })
            _save_cache(cache)
        elif to_classify:
            # No API key — fall back to extension-map for uncached files
            for item in to_classify:
                classifications.append({
                    "name": item["name"],
                    "path": item["path"],
                    "category": item["ext_category"],
                    "confidence": _CONFIDENCE_KNOWN,
                    "reasoning": "Extension-map (no API key configured)",
                    "ai_classified": False,
                })

        return {
            "classifications": classifications,
            "ai_calls_made": ai_calls,
            "cached_results": cached,
        }

    async def _call_gemini(
        self,
        files: list[dict[str, Any]],
        taxonomy: list[Any],
        api_key: str,
    ) -> list[dict[str, Any]]:
        """Single batch Gemini call. Returns one result per file in the same order."""
        try:
            import google.generativeai as genai  # noqa: PLC0415
        except ImportError:
            return self._fallback_results(files, taxonomy)

        taxonomy_text = "\n".join(
            f'- {t.name}: "{t.description}"' for t in taxonomy
        )
        category_names = [t.name for t in taxonomy]

        file_list_json = json.dumps(
            [
                {
                    "name": f["name"],
                    "size_kb": f["size_kb"],
                    "extension": f["extension"],
                }
                for f in files
            ],
            ensure_ascii=False,
        )

        prompt = f"""You are a file organization assistant.
Classify each file into EXACTLY ONE of the user's personal categories.
Be conservative — use best-guess based on filename, size, and extension.
If genuinely unknown, pick the closest match or use the last category as a fallback.

User's categories:
{taxonomy_text}

Files to classify (JSON array):
{file_list_json}

Respond with a JSON object in this exact structure — one entry per file, same order:
{{
  "results": [
    {{
      "category": "<one of: {', '.join(category_names)}>",
      "confidence": <float 0.0-1.0>,
      "reasoning": "<one short sentence>"
    }}
  ]
}}"""

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(_GEMINI_MODEL)
            response = await asyncio.get_running_loop().run_in_executor(
                None,
                lambda: model.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json"},
                ),
            )
            data = json.loads(response.text)
            raw = data.get("results", [])

            # Align lengths — Gemini might return fewer items on very large batches
            out: list[dict[str, Any]] = []
            for i, f in enumerate(files):
                if i < len(raw):
                    entry = raw[i]
                    cat = entry.get("category", category_names[-1])
                    if cat not in category_names:
                        cat = category_names[-1]
                    out.append({
                        "category": cat,
                        "confidence": float(entry.get("confidence", 0.6)),
                        "reasoning": str(entry.get("reasoning", "AI classified")),
                    })
                else:
                    out.append({
                        "category": category_names[-1],
                        "confidence": 0.4,
                        "reasoning": "AI response truncated — assigned to last category",
                    })
            return out

        except Exception as exc:
            # Any failure → graceful fallback
            return self._fallback_results(files, taxonomy, error=str(exc))

    def _fallback_results(
        self,
        files: list[dict[str, Any]],
        taxonomy: list[Any],
        error: str = "",
    ) -> list[dict[str, Any]]:
        """Return extension-based fallback when Gemini is unavailable."""
        last = taxonomy[-1].name if taxonomy else "Miscellaneous"
        note = f" (Gemini error: {error[:80]})" if error else ""
        return [
            {
                "category": f.get("ext_category", last),
                "confidence": 0.5,
                "reasoning": f"Extension-map fallback{note}",
            }
            for f in files
        ]
