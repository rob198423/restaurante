from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class TrackRead(BaseModel):
    id: str
    title: str
    media_type: str
    source_filename: str
    status: str
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MusicalSummary(BaseModel):
    key: str
    bpm: float
    time_signature: str
    duration_seconds: float
    confidence: float
    tuning_reference_hz: float = 440.0
    detected_scale: str
    primary_mode: str
    solo_regions: list[dict[str, float]]
    arpeggio_regions: list[dict[str, float]]


class AnalysisRead(BaseModel):
    track: TrackRead
    summary: dict[str, Any]
    chords: list[dict[str, Any]]
    scales: list[dict[str, Any]]
    modes: list[dict[str, Any]]
    tablature: dict[str, Any]
    stems: dict[str, Any]


class ExportRequest(BaseModel):
    format: Literal["midi", "pdf", "guitarpro"]


class TunerRequest(BaseModel):
    frequency_hz: float = Field(gt=15.0, lt=5000.0)


class TunerResponse(BaseModel):
    note: str
    octave: int
    cents: float
    target_hz: float
    in_tune: bool


class MetronomeRequest(BaseModel):
    bpm: int = Field(ge=30, le=260)
    bars: int = Field(default=4, ge=1, le=64)
    beats_per_bar: int = Field(default=4, ge=1, le=12)


class MetronomeResponse(BaseModel):
    bpm: int
    beats: list[dict[str, float | int | bool]]
