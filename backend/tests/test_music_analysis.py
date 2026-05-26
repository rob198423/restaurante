import math
import wave
from pathlib import Path

import numpy as np

from app.services.music_analysis import analyze_music, metronome_pattern, tuner_from_frequency


def _write_sine(path: Path, frequency: float = 440.0, seconds: float = 2.0, sr: int = 22050) -> None:
    t = np.linspace(0, seconds, int(sr * seconds), endpoint=False)
    samples = (0.4 * np.sin(2 * math.pi * frequency * t)).astype(np.float32)
    pcm = (samples * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sr)
        handle.writeframes(pcm.tobytes())


def test_analyze_music_returns_musical_payload(tmp_path):
    source = tmp_path / "tone.wav"
    _write_sine(source)
    result = analyze_music(source)
    assert result["summary"]["duration_seconds"] > 1.9
    assert result["summary"]["bpm"] > 0
    assert result["chords"]
    assert result["modes"]
    assert result["tablature"]["lines"]


def test_tuner_detects_a4():
    result = tuner_from_frequency(440.0)
    assert result["note"] == "A"
    assert result["octave"] == 4
    assert result["in_tune"] is True


def test_metronome_pattern_has_accents():
    pattern = metronome_pattern(120, 2, 4)
    assert len(pattern["beats"]) == 8
    assert pattern["beats"][0]["accent"] is True
    assert pattern["beats"][1]["accent"] is False
