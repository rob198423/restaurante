import mimetypes
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import get_settings

AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".avi"}


def classify_media(filename: str, content_type: str | None = None) -> str:
    suffix = Path(filename).suffix.lower()
    mime = content_type or mimetypes.guess_type(filename)[0] or ""
    if suffix in AUDIO_EXTENSIONS or mime.startswith("audio/"):
        return "audio"
    if suffix in VIDEO_EXTENSIONS or mime.startswith("video/"):
        return "video"
    raise ValueError("Only audio and video files are supported")


def safe_filename(filename: str) -> str:
    name = Path(filename).name.replace(" ", "_")
    return "".join(ch for ch in name if ch.isalnum() or ch in {".", "_", "-"}) or "upload.bin"


def save_upload(upload: UploadFile, owner_id: str) -> tuple[str, str, str]:
    settings = get_settings()
    media_type = classify_media(upload.filename or "media", upload.content_type)
    folder = settings.upload_dir / owner_id
    folder.mkdir(parents=True, exist_ok=True)
    original = safe_filename(upload.filename or f"media.{media_type}")
    destination = folder / f"{uuid4()}_{original}"
    with destination.open("wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)
    return str(destination), original, media_type
