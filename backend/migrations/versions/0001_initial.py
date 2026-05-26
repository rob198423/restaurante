"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-26
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_table(
        "tracks",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("owner_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("media_type", sa.String(length=24), nullable=False),
        sa.Column("source_filename", sa.String(length=260), nullable=False),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_tracks_owner_created", "tracks", ["owner_id", "created_at"])
    op.create_table(
        "analysis_results",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("track_id", sa.String(length=36), sa.ForeignKey("tracks.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("summary", sa.JSON(), nullable=False),
        sa.Column("chords", sa.JSON(), nullable=False),
        sa.Column("scales", sa.JSON(), nullable=False),
        sa.Column("modes", sa.JSON(), nullable=False),
        sa.Column("tablature", sa.JSON(), nullable=False),
        sa.Column("stems", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("analysis_results")
    op.drop_index("ix_tracks_owner_created", table_name="tracks")
    op.drop_table("tracks")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
