from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import Track, User
from app.schemas import ExportRequest
from app.services.exporters import export_analysis

router = APIRouter(prefix="/exports", tags=["exports"])

MEDIA_TYPES = {
    "midi": "audio/midi",
    "pdf": "application/pdf",
    "guitarpro": "application/gpif+xml",
}


@router.post("/{track_id}")
def export_track(
    track_id: str,
    payload: ExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    track = db.get(Track, track_id)
    if not track or track.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Track not found")
    if not track.analysis:
        raise HTTPException(status_code=409, detail="Analyze the track before exporting")
    analysis = {
        "summary": track.analysis.summary,
        "chords": track.analysis.chords,
        "scales": track.analysis.scales,
        "modes": track.analysis.modes,
        "tablature": track.analysis.tablature,
    }
    path = export_analysis(track.id, track.title, analysis, payload.format)
    return FileResponse(path, media_type=MEDIA_TYPES[payload.format], filename=path.name)
