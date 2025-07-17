"""AI classify route — uses AIClassifier with gemini-3.1-flash-lite."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ...ai_classifier import AIClassifier
from ...config import ConfigManager
from ..models import ClassifyRequest, ClassifyResponse, FileClassification
from .scan import _scan_results, _scan_status

router = APIRouter(tags=["ai"])

_config = ConfigManager()
_classifier = AIClassifier()


@router.post("/classify", response_model=ClassifyResponse)
async def classify_files(request: ClassifyRequest) -> ClassifyResponse:
    """
    Run AI classification on a completed scan result.
    Uses the user's taxonomy definitions + gemini-3.1-flash-lite.
    Falls back to extension-map categories if no API key is configured.
    """
    if request.scan_id not in _scan_status:
        raise HTTPException(status_code=404, detail="Scan ID not found")
    if _scan_status[request.scan_id] != "completed":
        raise HTTPException(status_code=400, detail="Scan is not yet completed")

    cfg = _config.load_config()
    scan_result = _scan_results[request.scan_id]

    taxonomy = cfg.taxonomy or []
    if request.taxonomy_ids:
        taxonomy = [t for t in taxonomy if t.id in request.taxonomy_ids]

    result = await _classifier.classify(
        scan_result=scan_result,
        taxonomy=taxonomy,
        api_key=cfg.gemini_api_key,
    )

    classifications = [
        FileClassification(
            name=c["name"],
            path=c["path"],
            category=c["category"],
            confidence=c["confidence"],
            reasoning=c["reasoning"],
            ai_classified=c["ai_classified"],
        )
        for c in result["classifications"]
    ]

    return ClassifyResponse(
        scan_id=request.scan_id,
        classifications=classifications,
        ai_calls_made=result["ai_calls_made"],
        cached_results=result["cached_results"],
    )
