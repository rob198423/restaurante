# ToneMind AI

ToneMind AI is an Android-first music intelligence MVP built with Flutter, FastAPI, PostgreSQL, FFmpeg, and Python audio analysis tooling.

## MVP features

- JWT login and registration.
- MP3 upload from the Android app.
- FastAPI endpoint for key, BPM, chord, scale, and simple tablature analysis.
- PostgreSQL persistence for users and analysis jobs.
- Dark Flutter UI with login, upload, player, and results screens.
- Extensible AI layer prepared for Librosa, Demucs, Basic Pitch, Essentia, and PyTorch.

## Project structure

```text
backend/
  app/
    api/
    core/
    db/
    models/
    schemas/
    services/
  tests/
frontend/
  lib/
    core/
    models/
    screens/
    widgets/
ai/
database/
storage/
```

## Run on Cursor/Linux

1. Start PostgreSQL:
   `docker compose -f database/docker-compose.yml up -d`
2. Create and activate the backend environment:
   `cd backend && python3 -m venv .venv && source .venv/bin/activate`
3. Install backend dependencies:
   `pip install -r requirements.txt`
4. Run the API:
   `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
5. Run the Flutter app:
   `cd frontend && flutter pub get && flutter run`

The backend API is available at `http://localhost:8000`, with OpenAPI docs at `http://localhost:8000/docs`.

## Run on Windows

1. Install Flutter SDK, Python 3.11+, Docker Desktop, FFmpeg, and Android Studio.
2. Start PostgreSQL in PowerShell:
   `docker compose -f database/docker-compose.yml up -d`
3. Create the backend virtual environment:
   `cd backend; py -3.11 -m venv .venv; .\.venv\Scripts\Activate.ps1`
4. Install dependencies:
   `pip install -r requirements.txt`
5. Run the API:
   `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
6. Run Android:
   `cd frontend; flutter pub get; flutter run`

For Android emulators, the app uses `http://10.0.2.2:8000` by default. For a physical phone, set `--dart-define=API_BASE_URL=http://YOUR_PC_IP:8000`.
