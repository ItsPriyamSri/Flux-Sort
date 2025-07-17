"""Browse route — directory listing for the frontend folder picker."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from ..models import BrowseResponse, DirectoryItem

router = APIRouter(tags=["browse"])


@router.get("/directory/browse", response_model=BrowseResponse)
async def browse_directory(path: str = Query(default="")) -> BrowseResponse:
    """
    Return the contents of a directory.
    If path is empty, returns the user's home directory.
    """
    target = Path(path).expanduser() if path else Path.home()

    if not target.exists():
        raise HTTPException(status_code=404, detail=f"Path not found: {target}")
    if not target.is_dir():
        raise HTTPException(status_code=400, detail=f"Not a directory: {target}")

    items: list[DirectoryItem] = []
    try:
        for entry in sorted(target.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower())):
            if entry.name.startswith("."):
                continue  # skip hidden by default
            size = None
            if entry.is_file():
                try:
                    size = entry.stat().st_size
                except OSError:
                    pass
            items.append(
                DirectoryItem(
                    name=entry.name,
                    path=str(entry),
                    is_dir=entry.is_dir(),
                    size_bytes=size,
                )
            )
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")

    parent = str(target.parent) if target != target.parent else None

    return BrowseResponse(path=str(target), parent=parent, items=items)


@router.get("/directory/defaults")
async def default_directories() -> dict:
    """Return common well-known directories for quick-select."""
    home = Path.home()
    dirs = {}
    for label, candidate in [
        ("Downloads", home / "Downloads"),
        ("Desktop", home / "Desktop"),
        ("Documents", home / "Documents"),
        ("Home", home),
    ]:
        if candidate.exists():
            dirs[label] = str(candidate)
    return {"directories": dirs}
