"""Scan route — start a directory scan and stream progress via WebSocket."""

from __future__ import annotations

import asyncio
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from ...file_detector import FileTypeDetector
from ...file_scanner import FileScanner, ScanResult
from ..models import (
    CategorySummary,
    FileSummary,
    ScanRequest,
    ScanResultResponse,
    ScanStartResponse,
)

router = APIRouter(tags=["scan"])

# ── In-memory session state ─────────────────────────────────────────────────
_scan_results: dict[str, ScanResult] = {}
_scan_status: dict[str, str] = {}           # "scanning" | "completed" | "error"
_progress_queues: dict[str, asyncio.Queue[dict[str, Any]]] = {}


# ── Helper ───────────────────────────────────────────────────────────────────

def _build_scan_response(scan_id: str, result: ScanResult) -> ScanResultResponse:
    categories: list[CategorySummary] = []
    for category, files in result.files_by_category.items():
        file_summaries = [
            FileSummary(
                name=f.name,
                path=str(f.path),
                size_bytes=f.size,
                size_mb=f.size_mb,
                extension=f.extension,
                category=category.value,
            )
            for f in files
        ]
        categories.append(
            CategorySummary(
                category=category.value,
                file_count=len(files),
                total_size_mb=round(sum(f.size for f in files) / (1024 * 1024), 2),
                files=file_summaries,
            )
        )
    return ScanResultResponse(
        scan_id=scan_id,
        status=_scan_status.get(scan_id, "completed"),
        directory=str(result.scanned_path),
        total_files=result.total_files,
        total_size_mb=result.total_size_mb,
        categories=categories,
        scan_duration_s=round(result.scan_duration, 3),
        errors=result.errors,
    )


# ── Routes ───────────────────────────────────────────────────────────────────

@router.post("/scan", response_model=ScanStartResponse)
async def start_scan(request: ScanRequest) -> ScanStartResponse:
    """Start a directory scan. Returns a scan_id; connect to WS for progress."""
    target = Path(request.directory).expanduser()
    if not target.exists():
        raise HTTPException(status_code=404, detail=f"Directory not found: {target}")
    if not target.is_dir():
        raise HTTPException(status_code=400, detail=f"Not a directory: {target}")

    scan_id = str(uuid.uuid4())
    queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=2000)
    _progress_queues[scan_id] = queue
    _scan_status[scan_id] = "scanning"

    loop = asyncio.get_running_loop()

    def _progress_cb(current: int, total: int) -> None:
        event: dict[str, Any] = {
            "type": "progress",
            "current": current,
            "total": total,
            "percent": round(current / total * 100 if total > 0 else 0, 1),
        }
        loop.call_soon_threadsafe(queue.put_nowait, event)

    def _run_scan() -> None:
        try:
            scanner = FileScanner(FileTypeDetector())
            scanner.set_progress_callback(_progress_cb)
            result = scanner.scan_directory(
                target,
                include_hidden=request.include_hidden,
                max_depth=0,
            )
            _scan_results[scan_id] = result
            _scan_status[scan_id] = "completed"
            loop.call_soon_threadsafe(
                queue.put_nowait, {"type": "done", "status": "completed"}
            )
        except Exception as exc:
            _scan_status[scan_id] = "error"
            loop.call_soon_threadsafe(
                queue.put_nowait, {"type": "error", "message": str(exc)}
            )

    asyncio.create_task(loop.run_in_executor(None, _run_scan))

    return ScanStartResponse(scan_id=scan_id, status="scanning")


@router.get("/scan/{scan_id}", response_model=ScanResultResponse)
async def get_scan_result(scan_id: str) -> ScanResultResponse:
    """Return the full scan result once the scan is complete."""
    if scan_id not in _scan_status:
        raise HTTPException(status_code=404, detail="Scan ID not found")
    if _scan_status[scan_id] == "scanning":
        raise HTTPException(status_code=202, detail="Scan still in progress")
    if _scan_status[scan_id] == "error":
        raise HTTPException(status_code=500, detail="Scan encountered an error")

    result = _scan_results[scan_id]
    return _build_scan_response(scan_id, result)


@router.websocket("/ws/progress/{scan_id}")
async def scan_progress_ws(websocket: WebSocket, scan_id: str) -> None:
    """WebSocket endpoint — streams scan progress events until done."""
    await websocket.accept()

    # Wait briefly for the queue to be registered (handles race where WS connects first)
    for _ in range(20):
        if scan_id in _progress_queues:
            break
        await asyncio.sleep(0.05)

    queue = _progress_queues.get(scan_id)
    if not queue:
        await websocket.send_json({"type": "error", "message": "Unknown scan ID"})
        await websocket.close()
        return

    try:
        while True:
            event = await asyncio.wait_for(queue.get(), timeout=60.0)
            await websocket.send_json(event)
            if event.get("type") in ("done", "error"):
                break
    except asyncio.TimeoutError:
        await websocket.send_json({"type": "error", "message": "Scan timeout"})
    except WebSocketDisconnect:
        pass
    finally:
        await websocket.close()
