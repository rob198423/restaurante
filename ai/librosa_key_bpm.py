from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

from app.services.audio_analysis import AudioAnalyzer


def analyze_file(path: str) -> dict:
    """Small CLI-friendly helper around the backend analyzer."""

    return AudioAnalyzer().analyze_key_and_bpm(Path(path)).model_dump()
