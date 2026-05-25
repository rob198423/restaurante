from pathlib import Path

from app.services.audio_analysis import AudioAnalyzer


def test_fallback_analysis_returns_music_fields(tmp_path: Path) -> None:
    audio_file = tmp_path / "sample.mp3"
    audio_file.write_bytes(b"not a real mp3 but deterministic for tests")

    result = AudioAnalyzer().analyze_key_and_bpm(audio_file)

    assert result.detected_key
    assert result.bpm > 0
    assert result.compatible_scales
    assert result.chords
    assert result.tablature
