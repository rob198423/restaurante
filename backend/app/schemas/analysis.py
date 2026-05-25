from typing import Any

from pydantic import BaseModel


class TablatureNote(BaseModel):
    time_seconds: float
    string: int
    fret: int
    note: str


class AnalysisRead(BaseModel):
    id: int
    filename: str
    detected_key: str
    bpm: float
    compatible_scales: list[str]
    chords: list[str]
    tablature: list[dict[str, Any]]

    model_config = {"from_attributes": True}


class AudioAnalysisResult(BaseModel):
    detected_key: str
    bpm: float
    compatible_scales: list[str]
    chords: list[str]
    tablature: list[TablatureNote]
    confidence: float
    engine: str
