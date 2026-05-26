from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analysis, auth, exports, tools, tracks
from app.core.config import get_settings
from app.core.database import init_db

settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


app.include_router(auth.router, prefix="/api")
app.include_router(tracks.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(exports.router, prefix="/api")
app.include_router(tools.router, prefix="/api")
