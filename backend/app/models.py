import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def uuid_str() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    tracks: Mapped[list["Track"]] = relationship(back_populates="owner", cascade="all, delete-orphan")


class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    media_type: Mapped[str] = mapped_column(String(24), nullable=False)
    source_filename: Mapped[str] = mapped_column(String(260), nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="uploaded", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    owner: Mapped[User] = relationship(back_populates="tracks")
    analysis: Mapped["AnalysisResult | None"] = relationship(back_populates="track", cascade="all, delete-orphan")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    track_id: Mapped[str] = mapped_column(ForeignKey("tracks.id", ondelete="CASCADE"), unique=True, nullable=False)
    summary: Mapped[dict] = mapped_column(JSON, nullable=False)
    chords: Mapped[list] = mapped_column(JSON, nullable=False)
    scales: Mapped[list] = mapped_column(JSON, nullable=False)
    modes: Mapped[list] = mapped_column(JSON, nullable=False)
    tablature: Mapped[dict] = mapped_column(JSON, nullable=False)
    stems: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    track: Mapped[Track] = relationship(back_populates="analysis")


Index("ix_tracks_owner_created", Track.owner_id, Track.created_at.desc())
