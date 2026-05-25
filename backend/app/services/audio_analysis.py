from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np

from app.schemas.analysis import AudioAnalysisResult, TablatureNote


PITCH_CLASSES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])


class AudioAnalyzer:
    """Audio intelligence facade used by API routes.

    The MVP uses Librosa when it is available. The deterministic fallback keeps
    local development and CI useful even before heavy audio dependencies are
    installed on every machine.
    """

    def analyze_key_and_bpm(self, audio_path: Path) -> AudioAnalysisResult:
        try:
            return self._analyze_with_librosa(audio_path)
        except Exception:
            return self._fallback_analysis(audio_path)

    def _analyze_with_librosa(self, audio_path: Path) -> AudioAnalysisResult:
        import librosa

        y, sr = librosa.load(audio_path, mono=True, duration=180)
        if y.size == 0:
            raise ValueError("Empty audio file")

        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        chroma_vector = np.mean(chroma, axis=1)
        detected_key, mode, confidence = self._estimate_key(chroma_vector)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        bpm = float(np.atleast_1d(tempo)[0])

        return AudioAnalysisResult(
            detected_key=f"{detected_key} {mode}",
            bpm=round(bpm, 2),
            compatible_scales=self._compatible_scales(detected_key, mode),
            chords=self._diatonic_chords(detected_key, mode),
            tablature=self._simple_tablature(detected_key),
            confidence=round(confidence, 3),
            engine="librosa",
        )

    def _estimate_key(self, chroma_vector: np.ndarray) -> tuple[str, str, float]:
        if np.linalg.norm(chroma_vector) == 0:
            raise ValueError("Cannot estimate key from silence")

        normalized = chroma_vector / np.linalg.norm(chroma_vector)
        best_score = -1.0
        best_key = "C"
        best_mode = "major"

        for root_index, pitch in enumerate(PITCH_CLASSES):
            major_score = float(np.dot(normalized, np.roll(MAJOR_PROFILE, root_index)))
            minor_score = float(np.dot(normalized, np.roll(MINOR_PROFILE, root_index)))
            if major_score > best_score:
                best_score = major_score
                best_key = pitch
                best_mode = "major"
            if minor_score > best_score:
                best_score = minor_score
                best_key = pitch
                best_mode = "minor"

        confidence = min(best_score / 20.0, 0.99)
        return best_key, best_mode, confidence

    def _fallback_analysis(self, audio_path: Path) -> AudioAnalysisResult:
        digest = hashlib.sha256(audio_path.read_bytes()).digest()
        key = PITCH_CLASSES[digest[0] % len(PITCH_CLASSES)]
        mode = "major" if digest[1] % 2 == 0 else "minor"
        bpm = 80 + digest[2] % 81

        return AudioAnalysisResult(
            detected_key=f"{key} {mode}",
            bpm=float(bpm),
            compatible_scales=self._compatible_scales(key, mode),
            chords=self._diatonic_chords(key, mode),
            tablature=self._simple_tablature(key),
            confidence=0.25,
            engine="deterministic-fallback",
        )

    def _compatible_scales(self, key: str, mode: str) -> list[str]:
        if mode == "minor":
            return [f"{key} natural minor", f"{key} pentatonic minor", f"{key} aeolian"]
        return [f"{key} major", f"{key} pentatonic major", f"{key} ionian"]

    def _diatonic_chords(self, key: str, mode: str) -> list[str]:
        root = PITCH_CLASSES.index(key)
        major_steps = [0, 2, 4, 5, 7, 9, 11]
        minor_steps = [0, 2, 3, 5, 7, 8, 10]
        qualities = ["", "m", "m", "", "", "m", "dim"] if mode == "major" else ["m", "dim", "", "m", "m", "", ""]
        steps = major_steps if mode == "major" else minor_steps
        return [f"{PITCH_CLASSES[(root + step) % 12]}{quality}" for step, quality in zip(steps, qualities)]

    def _simple_tablature(self, key: str) -> list[TablatureNote]:
        root = PITCH_CLASSES.index(key)
        open_string_notes = {"E": 0, "A": 5, "D": 10, "G": 3, "B": 7, "e": 0}
        tab: list[TablatureNote] = []
        for index, (string_name, note_value) in enumerate(open_string_notes.items(), start=1):
            fret = (root - note_value) % 12
            tab.append(
                TablatureNote(
                    time_seconds=round((index - 1) * 0.5, 2),
                    string=index,
                    fret=fret,
                    note=key if string_name != "e" else f"{key} octave",
                )
            )
        return tab
