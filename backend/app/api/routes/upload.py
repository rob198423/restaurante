from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.db.session import get_db
from app.models.analysis import Analysis
from app.models.user import User
from app.schemas.analysis import AnalysisRead, AudioAnalysisResult
from app.services.audio_analysis import AudioAnalyzer


router = APIRouter(prefix="/audio", tags=["audio"])


@router.post("/upload", response_model=AnalysisRead, status_code=status.HTTP_201_CREATED)
async def upload_audio(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Analysis:
    settings = get_settings()
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    extension = Path(file.filename).suffix.lower()
    if extension not in {".mp3", ".wav", ".m4a", ".aac", ".flac"}:
        raise HTTPException(status_code=400, detail="Unsupported audio format")

    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    target_path = settings.upload_dir / f"{uuid4().hex}{extension}"
    contents = await file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(status_code=413, detail="Audio file is too large")

    target_path.write_bytes(contents)
    result = AudioAnalyzer().analyze_key_and_bpm(target_path)
    analysis = _persist_analysis(db, current_user, file.filename, target_path, result)
    return analysis


@router.post("/detect-key", response_model=AudioAnalysisResult)
async def detect_key(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> AudioAnalysisResult:
    del current_user
    settings = get_settings()
    extension = Path(file.filename or "upload.mp3").suffix.lower() or ".mp3"
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    target_path = settings.upload_dir / f"detect-{uuid4().hex}{extension}"
    target_path.write_bytes(await file.read())
    return AudioAnalyzer().analyze_key_and_bpm(target_path)


def _persist_analysis(
    db: Session,
    user: User,
    filename: str,
    target_path: Path,
    result: AudioAnalysisResult,
) -> Analysis:
    analysis = Analysis(
        owner_id=user.id,
        filename=filename,
        file_path=str(target_path),
        detected_key=result.detected_key,
        bpm=result.bpm,
        compatible_scales=result.compatible_scales,
        chords=result.chords,
        tablature=[note.model_dump() for note in result.tablature],
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis
