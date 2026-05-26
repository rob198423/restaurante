import math
import shutil
import statistics
import subprocess
import tempfile
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np

from app.core.config import get_settings

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
MODE_INTERVALS = {
    "Ionian": [0, 2, 4, 5, 7, 9, 11],
    "Dorian": [0, 2, 3, 5, 7, 9, 10],
    "Phrygian": [0, 1, 3, 5, 7, 8, 10],
    "Lydian": [0, 2, 4, 6, 7, 9, 11],
    "Mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "Aeolian": [0, 2, 3, 5, 7, 8, 10],
    "Locrian": [0, 1, 3, 5, 6, 8, 10],
}
GUITAR_STRINGS = [("E", 40), ("A", 45), ("D", 50), ("G", 55), ("B", 59), ("e", 64)]


@dataclass
class AudioData:
    samples: np.ndarray
    sample_rate: int
    duration: float


def _run_ffmpeg_to_wav(path: Path) -> Path:
    settings = get_settings()
    if not shutil.which(settings.ffmpeg_bin):
        return path
    temp = Path(tempfile.mkdtemp(prefix="tonemind_audio_")) / "audio.wav"
    command = [settings.ffmpeg_bin, "-y", "-i", str(path), "-vn", "-ac", "1", "-ar", "22050", str(temp)]
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return temp


def _read_wave(path: Path) -> AudioData:
    wav_path = path if path.suffix.lower() == ".wav" else _run_ffmpeg_to_wav(path)
    with wave.open(str(wav_path), "rb") as handle:
        channels = handle.getnchannels()
        sample_rate = handle.getframerate()
        frames = handle.getnframes()
        raw = handle.readframes(frames)
        width = handle.getsampwidth()
    dtype = np.int16 if width == 2 else np.uint8
    data = np.frombuffer(raw, dtype=dtype).astype(np.float32)
    if width == 2:
        data /= 32768.0
    else:
        data = (data - 128.0) / 128.0
    if channels > 1:
        data = data.reshape(-1, channels).mean(axis=1)
    duration = float(len(data) / sample_rate) if sample_rate else 0.0
    return AudioData(samples=data, sample_rate=sample_rate, duration=duration)


def load_audio(path: str | Path) -> AudioData:
    source = Path(path)
    try:
        import librosa

        y, sr = librosa.load(str(source), sr=22050, mono=True)
        return AudioData(samples=np.asarray(y, dtype=np.float32), sample_rate=int(sr), duration=float(librosa.get_duration(y=y, sr=sr)))
    except Exception:
        return _read_wave(source)


def _estimate_tempo(audio: AudioData) -> float:
    try:
        import librosa

        tempo = librosa.feature.tempo(y=audio.samples, sr=audio.sample_rate)
        value = float(np.atleast_1d(tempo)[0])
        return round(value, 2) if math.isfinite(value) and value > 0 else 120.0
    except Exception:
        envelope = np.abs(audio.samples)
        if len(envelope) < audio.sample_rate:
            return 120.0
        frame = max(1, audio.sample_rate // 20)
        energy = np.array([envelope[i : i + frame].mean() for i in range(0, len(envelope), frame)])
        peaks = np.where(energy > energy.mean() + energy.std())[0]
        if len(peaks) < 2:
            return 120.0
        gaps = np.diff(peaks) / 20.0
        gaps = gaps[(gaps > 0.25) & (gaps < 2.0)]
        if len(gaps) == 0:
            return 120.0
        return round(float(60.0 / statistics.median(gaps)), 2)


def _chromagram(audio: AudioData) -> np.ndarray:
    try:
        import librosa

        chroma = librosa.feature.chroma_cqt(y=audio.samples, sr=audio.sample_rate)
        return np.asarray(chroma)
    except Exception:
        n = len(audio.samples)
        if n == 0:
            return np.zeros((12, 1))
        window_size = min(max(2048, audio.sample_rate // 2), n)
        hop = max(1, window_size // 2)
        frames = []
        for start in range(0, max(1, n - window_size), hop):
            segment = audio.samples[start : start + window_size] * np.hanning(min(window_size, n - start))
            spectrum = np.abs(np.fft.rfft(segment))
            freqs = np.fft.rfftfreq(len(segment), 1.0 / audio.sample_rate)
            chroma = np.zeros(12)
            for freq, magnitude in zip(freqs, spectrum):
                if 40.0 <= freq <= 5000.0 and magnitude > 0:
                    midi = int(round(69 + 12 * math.log2(freq / 440.0)))
                    chroma[midi % 12] += magnitude
            frames.append(chroma / (np.linalg.norm(chroma) + 1e-9))
        return np.asarray(frames or [np.zeros(12)]).T


def _detect_key(chroma: np.ndarray) -> tuple[str, float, str]:
    average = chroma.mean(axis=1)
    if np.linalg.norm(average) == 0:
        return "C major", 0.0, "Ionian"
    scores = []
    for root in range(12):
        major = np.corrcoef(average, np.roll(MAJOR_PROFILE, root))[0, 1]
        minor = np.corrcoef(average, np.roll(MINOR_PROFILE, root))[0, 1]
        scores.append((float(major), root, "major", "Ionian"))
        scores.append((float(minor), root, "minor", "Aeolian"))
    confidence, root, quality, mode = max(scores, key=lambda item: item[0])
    confidence = max(0.0, min(1.0, (confidence + 1.0) / 2.0))
    return f"{NOTE_NAMES[root]} {quality}", round(confidence, 3), mode


def _chord_name(chroma_vector: np.ndarray) -> str:
    templates: list[tuple[str, np.ndarray]] = []
    for root in range(12):
        major = np.zeros(12); major[[root, (root + 4) % 12, (root + 7) % 12]] = 1
        minor = np.zeros(12); minor[[root, (root + 3) % 12, (root + 7) % 12]] = 1
        diminished = np.zeros(12); diminished[[root, (root + 3) % 12, (root + 6) % 12]] = 1
        seventh = np.zeros(12); seventh[[root, (root + 4) % 12, (root + 7) % 12, (root + 10) % 12]] = 1
        templates.extend([
            (NOTE_NAMES[root], major),
            (f"{NOTE_NAMES[root]}m", minor),
            (f"{NOTE_NAMES[root]}dim", diminished),
            (f"{NOTE_NAMES[root]}7", seventh),
        ])
    vector = chroma_vector / (np.linalg.norm(chroma_vector) + 1e-9)
    name, score = "N.C.", -1.0
    for candidate, template in templates:
        template = template / np.linalg.norm(template)
        value = float(np.dot(vector, template))
        if value > score:
            name, score = candidate, value
    return name if score > 0.35 else "N.C."


def _detect_chords(chroma: np.ndarray, duration: float) -> list[dict]:
    frames = chroma.shape[1]
    if frames == 0:
        return []
    segment_count = max(1, min(96, int(math.ceil(max(duration, 1.0) / 2.0))))
    chords = []
    for i in range(segment_count):
        start_frame = int(i * frames / segment_count)
        end_frame = max(start_frame + 1, int((i + 1) * frames / segment_count))
        vector = chroma[:, start_frame:end_frame].mean(axis=1)
        chords.append({
            "start": round(i * duration / segment_count, 2),
            "end": round((i + 1) * duration / segment_count, 2),
            "chord": _chord_name(vector),
            "confidence": round(float(np.linalg.norm(vector) / (np.linalg.norm(chroma.mean(axis=1)) + 1e-9)), 3),
        })
    compressed: list[dict] = []
    for chord in chords:
        if compressed and compressed[-1]["chord"] == chord["chord"]:
            compressed[-1]["end"] = chord["end"]
            compressed[-1]["confidence"] = round((compressed[-1]["confidence"] + chord["confidence"]) / 2, 3)
        else:
            compressed.append(chord)
    return compressed


def _scale_payload(key: str) -> tuple[list[dict], list[dict]]:
    root_name = key.split()[0]
    root = NOTE_NAMES.index(root_name)
    scales = []
    modes = []
    for mode, intervals in MODE_INTERVALS.items():
        notes = [NOTE_NAMES[(root + interval) % 12] for interval in intervals]
        modes.append({"name": mode, "root": root_name, "notes": notes})
        if mode in {"Ionian", "Aeolian", "Dorian", "Mixolydian"}:
            scales.append({"name": f"{root_name} {mode}", "notes": notes})
    return scales, modes


def _tab_for_note(midi: int) -> dict:
    options = []
    for string_name, open_midi in GUITAR_STRINGS:
        fret = midi - open_midi
        if 0 <= fret <= 22:
            options.append((fret, string_name))
    if not options:
        return {"string": "E", "fret": 0}
    fret, string_name = min(options, key=lambda item: (item[0] > 12, item[0]))
    return {"string": string_name, "fret": int(fret)}


def _generate_tablature(chords: Iterable[dict], key: str) -> dict:
    root = NOTE_NAMES.index(key.split()[0])
    lines = []
    for index, chord in enumerate(list(chords)[:64]):
        base_midi = 52 + root + (index % 2) * 12
        notes = [_tab_for_note(base_midi + interval) for interval in (0, 4, 7, 12)]
        lines.append({"start": chord["start"], "end": chord["end"], "chord": chord["chord"], "notes": notes})
    return {"tuning": [name for name, _ in GUITAR_STRINGS], "capo": 0, "lines": lines}


def _regions(audio: AudioData) -> tuple[list[dict], list[dict]]:
    if len(audio.samples) == 0:
        return [], []
    frame = max(512, audio.sample_rate // 4)
    hop = max(1, frame // 2)
    energies = []
    brightness = []
    for start in range(0, max(1, len(audio.samples) - frame), hop):
        segment = audio.samples[start : start + frame]
        spectrum = np.abs(np.fft.rfft(segment))
        freqs = np.fft.rfftfreq(len(segment), 1.0 / audio.sample_rate)
        energies.append(float(np.mean(segment**2)))
        brightness.append(float(np.sum(freqs * spectrum) / (np.sum(spectrum) + 1e-9)))
    if not energies:
        return [], []
    energy_threshold = float(np.percentile(energies, 75))
    bright_threshold = float(np.percentile(brightness, 70))
    solo = []
    arpeggio = []
    for i, (energy, bright) in enumerate(zip(energies, brightness)):
        start = round(i * hop / audio.sample_rate, 2)
        end = round(min(audio.duration, start + frame / audio.sample_rate), 2)
        if energy >= energy_threshold and bright >= bright_threshold:
            solo.append({"start": start, "end": end, "confidence": round(min(1.0, energy / (energy_threshold + 1e-9)), 3)})
        elif energy >= float(np.percentile(energies, 55)):
            arpeggio.append({"start": start, "end": end, "confidence": round(min(1.0, energy / (energy_threshold + 1e-9)), 3)})
    return _merge_regions(solo), _merge_regions(arpeggio)


def _merge_regions(regions: list[dict]) -> list[dict]:
    merged: list[dict] = []
    for region in regions:
        if merged and region["start"] <= merged[-1]["end"] + 0.35:
            merged[-1]["end"] = region["end"]
            merged[-1]["confidence"] = round(max(merged[-1]["confidence"], region["confidence"]), 3)
        else:
            merged.append(region)
    return merged[:12]


def analyze_music(path: str | Path) -> dict:
    audio = load_audio(path)
    chroma = _chromagram(audio)
    key, confidence, primary_mode = _detect_key(chroma)
    bpm = _estimate_tempo(audio)
    chords = _detect_chords(chroma, audio.duration)
    scales, modes = _scale_payload(key)
    solo_regions, arpeggio_regions = _regions(audio)
    summary = {
        "key": key,
        "bpm": bpm,
        "time_signature": "4/4",
        "duration_seconds": round(audio.duration, 2),
        "confidence": confidence,
        "tuning_reference_hz": 440.0,
        "detected_scale": scales[0]["name"] if scales else key,
        "primary_mode": primary_mode,
        "solo_regions": solo_regions,
        "arpeggio_regions": arpeggio_regions,
    }
    return {
        "summary": summary,
        "chords": chords,
        "scales": scales,
        "modes": modes,
        "tablature": _generate_tablature(chords, key),
        "stems": {},
    }


def tuner_from_frequency(frequency_hz: float) -> dict:
    midi = 69 + 12 * math.log2(frequency_hz / 440.0)
    nearest = int(round(midi))
    target = 440.0 * (2 ** ((nearest - 69) / 12))
    cents = 1200 * math.log2(frequency_hz / target)
    return {
        "note": NOTE_NAMES[nearest % 12],
        "octave": nearest // 12 - 1,
        "cents": round(cents, 2),
        "target_hz": round(target, 3),
        "in_tune": abs(cents) <= 5.0,
    }


def metronome_pattern(bpm: int, bars: int, beats_per_bar: int) -> dict:
    interval = 60.0 / bpm
    beats = []
    for beat in range(bars * beats_per_bar):
        beats.append({
            "index": beat + 1,
            "time_seconds": round(beat * interval, 3),
            "accent": beat % beats_per_bar == 0,
        })
    return {"bpm": bpm, "beats": beats}
