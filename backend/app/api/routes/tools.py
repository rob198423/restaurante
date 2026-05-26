from fastapi import APIRouter

from app.schemas import MetronomeRequest, MetronomeResponse, TunerRequest, TunerResponse
from app.services.music_analysis import metronome_pattern, tuner_from_frequency

router = APIRouter(prefix="/tools", tags=["tools"])


@router.post("/tuner", response_model=TunerResponse)
def tuner(payload: TunerRequest) -> TunerResponse:
    return TunerResponse(**tuner_from_frequency(payload.frequency_hz))


@router.post("/metronome", response_model=MetronomeResponse)
def metronome(payload: MetronomeRequest) -> MetronomeResponse:
    return MetronomeResponse(**metronome_pattern(payload.bpm, payload.bars, payload.beats_per_bar))
