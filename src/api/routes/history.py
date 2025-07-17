"""History and undo route."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from ...file_sorter import FileSorter
from ..models import HistoryEntry, HistoryResponse, UndoResponse
from .scan import _scan_results

router = APIRouter(tags=["history"])


def _get_sorter(directory: str | None) -> FileSorter:
    """Return a FileSorter pointing at the given directory (or cwd)."""
    base = Path(directory).expanduser() if directory else Path.cwd()
    return FileSorter(base)


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    directory: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
) -> HistoryResponse:
    """Return operation history for a directory (defaults to cwd)."""
    sorter = _get_sorter(directory)
    ops = sorter.get_operation_history(limit=limit)

    entries = [
        HistoryEntry(
            operation_id=op.operation_id,
            timestamp=op.timestamp.isoformat(),
            source_dir=str(op.source_path.parent),
            destination_dir=str(op.destination_path.parent),
            category=op.category.value if hasattr(op.category, "value") else str(op.category),
            file_name=op.source_path.name,
        )
        for op in ops
    ]
    return HistoryResponse(operations=entries)


@router.post("/history/undo/{operation_id}", response_model=UndoResponse)
async def undo_operation(
    operation_id: str,
    directory: str | None = Query(default=None),
) -> UndoResponse:
    """Undo all file moves associated with a specific operation ID."""
    sorter = _get_sorter(directory)
    ok, fail, errors = sorter.undo_operation(operation_id)

    if ok == 0 and fail == 0:
        raise HTTPException(
            status_code=404, detail=f"Operation {operation_id!r} not found"
        )

    return UndoResponse(
        operation_id=operation_id,
        successful_undos=ok,
        failed_undos=fail,
        errors=errors,
    )
