# TONEMIND AI

Professional full-stack Android music analysis app built with Flutter, FastAPI, PostgreSQL, FFmpeg, librosa, Demucs, Basic Pitch, Essentia, and PyTorch.

## Features

- Login and registration with JWT.
- MP3/audio upload, video upload, and microphone recording.
- Key, BPM, chord, scale, Greek mode, solo, arpeggio, and tablature detection.
- Guitar fretboard visualization.
- Instrument separation using Demucs when installed, with FFmpeg spectral split fallback.
- MIDI, PDF, and Guitar Pro GPIF export.
- Tuner, metronome, history, dark responsive UI.

## Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Core-only development install:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-core.txt
uvicorn app.main:app --reload
```

## Docker

```bash
docker compose up --build
```

## Flutter Android

```bash
cd frontend
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

Release APK:

```bash
./scripts/build_apk.sh
```

The generated APK is copied to `artifacts/tonemind-ai-release.apk`.

## API

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/tracks?title=Song`
- `GET /api/tracks`
- `POST /api/tracks/{track_id}/analyze`
- `GET /api/tracks/{track_id}/analysis`
- `POST /api/analysis/{track_id}/separate`
- `POST /api/exports/{track_id}` with `midi`, `pdf`, or `guitarpro`
- `POST /api/tools/tuner`
- `POST /api/tools/metronome`
