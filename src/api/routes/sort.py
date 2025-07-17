"""Sort route — preview and execute file organisation operations."""

from __future__ import annotations

import shutil
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException

from ...file_sorter import FileSorter, SortOperation
from ..models import (
    MoveOperation,
    SortExecuteRequest,
    SortExecuteResponse,
    SortPreviewResponse,
)
from .scan import _scan_results, _scan_status

router = APIRouter(tags=["sort"])


@router.get("/sort/preview/{scan_id}", response_model=SortPreviewResponse)
async def preview_sort(scan_id: str) -> SortPreviewResponse:
    """
    Return a proposed sort plan for a completed scan using the standard
    extension-map categories. The AI route (/api/classify) returns a richer
    version with custom taxonomy categories.
    """
    if scan_id not in _scan_status:
        raise HTTPException(status_code=404, detail="Scan ID not found")
    if _scan_status[scan_id] != "completed":
        raise HTTPException(status_code=400, detail="Scan is not yet completed")

    result = _scan_results[scan_id]
    sorter = FileSorter(result.scanned_path)
    raw_preview = sorter.preview_sort_operation(result)

    moves_by_category: dict[str, list[MoveOperation]] = {}
    total = 0
    for category, pairs in raw_preview.items():
        if not pairs:
            continue
        ops = [
            MoveOperation(
                source=str(src),
                destination=str(dst),
                category=category.value,
            )
            for src, dst in pairs
        ]
        moves_by_category[category.value] = ops
        total += len(ops)

    return SortPreviewResponse(
        scan_id=scan_id,
        total_moves=total,
        moves_by_category=moves_by_category,
    )


@router.post("/sort/execute", response_model=SortExecuteResponse)
async def execute_sort(request: SortExecuteRequest) -> SortExecuteResponse:
    """
    Execute a list of approved move operations.
    Accepts explicit (source, destination, category) triples so both
    standard and AI-custom-taxonomy sorts use the same code path.
    The operation is logged to .fluxsort_history.json for undo.
    """
    if request.scan_id not in _scan_status:
        raise HTTPException(status_code=404, detail="Scan ID not found")

    scan_result = _scan_results.get(request.scan_id)
    if scan_result is None:
        raise HTTPException(status_code=404, detail="Scan result not available")

    # Reuse FileSorter's history persistence — instantiate against the scanned dir
    sorter = FileSorter(scan_result.scanned_path)
    operation_id = str(uuid.uuid4())
    timestamp = datetime.now()

    operations: list[SortOperation] = []
    errors: list[str] = []
    successful = 0
    failed = 0
    total_bytes = 0

    start = datetime.now()

    for move in request.moves:
        src = Path(move.source)
        dst = Path(move.destination)
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists():
                # Apply rename strategy (matching FileSorter default)
                stem, suffix = dst.stem, dst.suffix
                counter = 1
                while dst.exists():
                    dst = dst.parent / f"{stem} ({counter}){suffix}"
                    counter += 1

            size = src.stat().st_size if src.exists() else 0
            shutil.move(str(src), str(dst))

            operations.append(
                SortOperation(
                    source_path=src,
                    destination_path=dst,
                    category=move.category,  # type: ignore[arg-type]
                    operation_id=operation_id,
                    timestamp=timestamp,
                )
            )
            successful += 1
            total_bytes += size
        except Exception as exc:
            failed += 1
            errors.append(f"Failed to move {src.name}: {exc}")

    # Persist history so undo works
    if operations:
        sorter._save_operation_history(operations)  # noqa: SLF001

    duration = (datetime.now() - start).total_seconds()

    return SortExecuteResponse(
        operation_id=operation_id,
        successful_moves=successful,
        failed_moves=failed,
        total_size_moved_mb=round(total_bytes / (1024 * 1024), 2),
        duration_s=round(duration, 3),
        errors=errors,
    )
