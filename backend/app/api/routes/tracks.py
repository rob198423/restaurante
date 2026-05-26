from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import AnalysisResult, Track, User
from app.schemas import AnalysisRead, TrackRead
from app.services.music_analysis import analyze_music
from app.services.storage import save_upload

router = APIRouter(prefix="/tracks", tags=["tracks"])


@router.post("", response_model=TrackRead, status_code=status.HTTP_201_CREATED)
def upload_track(
    title: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TrackRead:
    try:
        storage_path, original, media_type = save_upload(file, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    track = Track(
        owner_id=current_user.id,
        title=title.strip() or original,
        media_type=media_type,
        source_filename=original,
        storage_path=storage_path,
    )
    db.add(track)
    db.commit()
    db.refresh(track)
    return TrackRead.model_validate(track)


@router.get("", response_model=list[TrackRead])
def list_tracks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[TrackRead]:
    tracks = db.query(Track).filter(Track.owner_id == current_user.id).order_by(Track.created_at.desc()).all()
    return [TrackRead.model_validate(track) for track in tracks]


@router.get("/{track_id}", response_model=TrackRead)
def get_track(track_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> TrackRead:
    track = _track_for_user(db, track_id, current_user.id)
    return TrackRead.model_validate(track)


@router.post("/{track_id}/analyze", response_model=AnalysisRead)
def analyze_track(track_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> AnalysisRead:
    track = _track_for_user(db, track_id, current_user.id)
    track.status = "analyzing"
    track.error_message = None
    db.commit()
    try:
        payload = analyze_music(track.storage_path)
        existing = track.analysis
        if existing:
            existing.summary = payload["summary"]
            existing.chords = payload["chords"]
            existing.scales = payload["scales"]
            existing.modes = payload["modes"]
            existing.tablature = payload["tablature"]
            existing.stems = payload.get("stems", {})
        else:
            db.add(AnalysisResult(track_id=track.id, **payload))
        track.status = "analyzed"
        db.commit()
        db.refresh(track)
    except Exception as exc:
        track.status = "failed"
        track.error_message = str(exc)
        db.commit()
        raise HTTPException(status_code=500, detail="Analysis failed") from exc
    return _analysis_response(track)


@router.get("/{track_id}/analysis", response_model=AnalysisRead)
def get_analysis(track_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> AnalysisRead:
    track = _track_for_user(db, track_id, current_user.id)
    if not track.analysis:
        raise HTTPException(status_code=404, detail="Track has not been analyzed")
    return _analysis_response(track)


def _track_for_user(db: Session, track_id: str, owner_id: str) -> Track:
    track = db.get(Track, track_id)
    if not track or track.owner_id != owner_id:
        raise HTTPException(status_code=404, detail="Track not found")
    return track


def _analysis_response(track: Track) -> AnalysisRead:
    result = track.analysis
    if not result:
        raise HTTPException(status_code=404, detail="Track has not been analyzed")
    return AnalysisRead(
        track=TrackRead.model_validate(track),
        summary=result.summary,
        chords=result.chords,
        scales=result.scales,
        modes=result.modes,
        tablature=result.tablature,
        stems=result.stems,
    )
