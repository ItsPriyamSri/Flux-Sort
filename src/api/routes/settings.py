"""Settings route — API key, scheduler, and general preferences."""

from __future__ import annotations

from fastapi import APIRouter

from ...config import ConfigManager
from ..models import SettingsIn, SettingsOut

router = APIRouter(tags=["settings"])
_config = ConfigManager()

_KEY_MASKED = "••••••••"


@router.get("/settings", response_model=SettingsOut)
async def get_settings() -> SettingsOut:
    cfg = _config.load_config()
    return SettingsOut(
        # Never return the actual key — just indicate if one is set
        gemini_api_key=_KEY_MASKED if cfg.gemini_api_key else "",
        scheduler_enabled=cfg.scheduler_enabled,
        scheduler_day=cfg.scheduler_day,
        scheduler_time=cfg.scheduler_time,
        scheduler_watch_paths=cfg.scheduler_watch_paths,
        conflicts_strategy=cfg.conflicts_strategy,
        include_hidden_files=cfg.include_hidden_files,
    )


@router.put("/settings", response_model=SettingsOut)
async def update_settings(body: SettingsIn) -> SettingsOut:
    cfg = _config.load_config()

    # Only update the key if caller sent a real value (not the mask placeholder)
    if body.gemini_api_key and body.gemini_api_key != _KEY_MASKED:
        cfg.gemini_api_key = body.gemini_api_key

    cfg.scheduler_enabled = body.scheduler_enabled
    cfg.scheduler_day = body.scheduler_day
    cfg.scheduler_time = body.scheduler_time
    cfg.scheduler_watch_paths = body.scheduler_watch_paths
    cfg.conflicts_strategy = body.conflicts_strategy
    cfg.include_hidden_files = body.include_hidden_files

    _config.save_config(cfg)

    return SettingsOut(
        gemini_api_key=_KEY_MASKED if cfg.gemini_api_key else "",
        scheduler_enabled=cfg.scheduler_enabled,
        scheduler_day=cfg.scheduler_day,
        scheduler_time=cfg.scheduler_time,
        scheduler_watch_paths=cfg.scheduler_watch_paths,
        conflicts_strategy=cfg.conflicts_strategy,
        include_hidden_files=cfg.include_hidden_files,
    )


@router.delete("/settings/api-key", status_code=204)
async def clear_api_key() -> None:
    """Remove the stored Gemini API key."""
    cfg = _config.load_config()
    cfg.gemini_api_key = ""
    _config.save_config(cfg)
