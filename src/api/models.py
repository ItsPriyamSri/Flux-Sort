"""All Pydantic v2 request/response models for the FluxSort API."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Directory / Browse
# ---------------------------------------------------------------------------

class DirectoryItem(BaseModel):
    name: str
    path: str
    is_dir: bool
    size_bytes: int | None = None


class BrowseResponse(BaseModel):
    path: str
    parent: str | None
    items: list[DirectoryItem]


# ---------------------------------------------------------------------------
# Scan
# ---------------------------------------------------------------------------

class ScanRequest(BaseModel):
    directory: str
    include_hidden: bool = False

    @field_validator("directory")
    @classmethod
    def directory_must_be_nonempty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("directory must not be empty")
        return v.strip()


class ScanStartResponse(BaseModel):
    scan_id: str
    status: str = "scanning"


class FileSummary(BaseModel):
    name: str
    path: str
    size_bytes: int
    size_mb: float
    extension: str
    category: str


class CategorySummary(BaseModel):
    category: str
    file_count: int
    total_size_mb: float
    files: list[FileSummary]


class ScanResultResponse(BaseModel):
    scan_id: str
    status: str          # "scanning" | "completed" | "error"
    directory: str
    total_files: int
    total_size_mb: float
    categories: list[CategorySummary]
    scan_duration_s: float
    errors: list[str]


# ---------------------------------------------------------------------------
# Taxonomy
# ---------------------------------------------------------------------------

class TaxonomyCategoryIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    description: str = Field(..., min_length=1, max_length=512)
    color: str = Field(default="#3B82F6", pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: str = Field(default="📁", max_length=4)
    folder_name: str = Field(..., min_length=1, max_length=128)


class TaxonomyCategoryOut(TaxonomyCategoryIn):
    id: str


class TaxonomyListResponse(BaseModel):
    taxonomy: list[TaxonomyCategoryOut]


# ---------------------------------------------------------------------------
# AI Classification
# ---------------------------------------------------------------------------

class ClassifyRequest(BaseModel):
    scan_id: str
    taxonomy_ids: list[str] = Field(
        default_factory=list,
        description="Subset of taxonomy IDs to use. Empty = use all."
    )


class FileClassification(BaseModel):
    name: str
    path: str
    category: str           # taxonomy category name
    confidence: float       # 0.0 – 1.0
    reasoning: str
    ai_classified: bool     # False = extension-map result


class ClassifyResponse(BaseModel):
    scan_id: str
    classifications: list[FileClassification]
    ai_calls_made: int
    cached_results: int


# ---------------------------------------------------------------------------
# Sort
# ---------------------------------------------------------------------------

class MoveOperation(BaseModel):
    source: str
    destination: str
    category: str


class SortPreviewResponse(BaseModel):
    scan_id: str
    total_moves: int
    moves_by_category: dict[str, list[MoveOperation]]


class SortExecuteRequest(BaseModel):
    scan_id: str
    moves: list[MoveOperation]


class SortExecuteResponse(BaseModel):
    operation_id: str
    successful_moves: int
    failed_moves: int
    total_size_moved_mb: float
    duration_s: float
    errors: list[str]


# ---------------------------------------------------------------------------
# History / Undo
# ---------------------------------------------------------------------------

class HistoryEntry(BaseModel):
    operation_id: str
    timestamp: str
    source_dir: str
    destination_dir: str
    category: str
    file_name: str


class HistoryResponse(BaseModel):
    operations: list[HistoryEntry]


class UndoResponse(BaseModel):
    operation_id: str
    successful_undos: int
    failed_undos: int
    errors: list[str]


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

class SettingsIn(BaseModel):
    gemini_api_key: str = ""
    scheduler_enabled: bool = False
    scheduler_day: str = "sunday"
    scheduler_time: str = "09:00"
    scheduler_watch_paths: list[str] = Field(default_factory=list)
    conflicts_strategy: str = "rename"
    include_hidden_files: bool = False


class SettingsOut(SettingsIn):
    gemini_api_key: str = ""  # masked on read — never expose the actual key in response

    class Config:
        # Mask the key when serialising
        pass


# ---------------------------------------------------------------------------
# Generic
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str
    version: str


class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None
