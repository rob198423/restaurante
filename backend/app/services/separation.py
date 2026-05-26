import shutil
import subprocess
from pathlib import Path

from app.core.config import get_settings


def separate_instruments(source: str | Path, track_id: str) -> dict:
    settings = get_settings()
    source_path = Path(source)
    output_root = settings.export_dir / track_id / "stems"
    output_root.mkdir(parents=True, exist_ok=True)
    if shutil.which("demucs"):
        subprocess.run(["demucs", "--two-stems", "vocals", "-o", str(output_root), str(source_path)], check=True)
        stem_files = {path.stem: str(path) for path in output_root.rglob("*.wav")}
        if stem_files:
            return {"engine": "demucs", "files": stem_files}
    return _ffmpeg_fallback(source_path, output_root)


def _ffmpeg_fallback(source: Path, output_root: Path) -> dict:
    settings = get_settings()
    files = {}
    filters = {
        "low_band": "lowpass=f=250",
        "mid_band": "highpass=f=250,lowpass=f=3500",
        "high_band": "highpass=f=3500",
    }
    if not shutil.which(settings.ffmpeg_bin):
        return {"engine": "frequency_split", "files": files, "message": "ffmpeg is required for local stem rendering"}
    for name, audio_filter in filters.items():
        target = output_root / f"{name}.wav"
        subprocess.run(
            [settings.ffmpeg_bin, "-y", "-i", str(source), "-vn", "-af", audio_filter, str(target)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        files[name] = str(target)
    return {"engine": "frequency_split", "files": files}
