from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import AnalysisResult, Track, User
from app.schemas import AnalysisRead, TrackRead
from app.services.separation import separate_instruments

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/{track_id}/separate", response_model=AnalysisRead)
def separate_track(track_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> AnalysisRead:
    track = db.get(Track, track_id)
    if not track or track.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Track not found")
    stems = separate_instruments(track.storage_path, track.id)
    if track.analysis:
        track.analysis.stems = stems
    else:
        track.analysis = AnalysisResult(track_id=track.id, summary={}, chords=[], scales=[], modes=[], tablature={}, stems=stems)
    track.status = "separated"
    db.commit()
    db.refresh(track)
    result = track.analysis
    return AnalysisRead(
        track=TrackRead.model_validate(track),
        summary=result.summary,
        chords=result.chords,
        scales=result.scales,
        modes=result.modes,
        tablature=result.tablature,
        stems=result.stems,
    )
