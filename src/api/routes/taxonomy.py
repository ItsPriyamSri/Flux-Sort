"""Taxonomy route — CRUD for user-defined semantic categories."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException

from ...config import ConfigManager, TaxonomyCategory
from ..models import TaxonomyCategoryIn, TaxonomyCategoryOut, TaxonomyListResponse

router = APIRouter(tags=["taxonomy"])
_config = ConfigManager()


def _load() -> list[TaxonomyCategory]:
    return _config.load_config().taxonomy or []


def _save(cats: list[TaxonomyCategory]) -> None:
    cfg = _config.load_config()
    cfg.taxonomy = cats
    _config.save_config(cfg)


@router.get("/taxonomy", response_model=TaxonomyListResponse)
async def list_taxonomy() -> TaxonomyListResponse:
    cats = _load()
    return TaxonomyListResponse(
        taxonomy=[
            TaxonomyCategoryOut(
                id=c.id,
                name=c.name,
                description=c.description,
                color=c.color,
                icon=c.icon,
                folder_name=c.folder_name,
            )
            for c in cats
        ]
    )


@router.post("/taxonomy", response_model=TaxonomyCategoryOut, status_code=201)
async def create_category(body: TaxonomyCategoryIn) -> TaxonomyCategoryOut:
    cats = _load()
    new_cat = TaxonomyCategory(
        id=str(uuid.uuid4()),
        name=body.name,
        description=body.description,
        color=body.color,
        icon=body.icon,
        folder_name=body.folder_name,
    )
    cats.append(new_cat)
    _save(cats)
    return TaxonomyCategoryOut(**new_cat.__dict__)


@router.put("/taxonomy/{cat_id}", response_model=TaxonomyCategoryOut)
async def update_category(cat_id: str, body: TaxonomyCategoryIn) -> TaxonomyCategoryOut:
    cats = _load()
    for i, c in enumerate(cats):
        if c.id == cat_id:
            updated = TaxonomyCategory(
                id=cat_id,
                name=body.name,
                description=body.description,
                color=body.color,
                icon=body.icon,
                folder_name=body.folder_name,
            )
            cats[i] = updated
            _save(cats)
            return TaxonomyCategoryOut(**updated.__dict__)
    raise HTTPException(status_code=404, detail=f"Category {cat_id!r} not found")


@router.delete("/taxonomy/{cat_id}", status_code=204)
async def delete_category(cat_id: str) -> None:
    cats = _load()
    filtered = [c for c in cats if c.id != cat_id]
    if len(filtered) == len(cats):
        raise HTTPException(status_code=404, detail=f"Category {cat_id!r} not found")
    _save(filtered)
