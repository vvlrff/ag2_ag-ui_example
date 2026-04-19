import sqlalchemy as sa

from ag2_example.domain.entities import Note
from ag2_example.models.base import mapper_registry

notes_table = sa.Table(
    "notes",
    mapper_registry.metadata,
    sa.Column(
        "id",
        sa.Uuid,
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    ),
    sa.Column("title", sa.String(512), nullable=False),
    sa.Column("body", sa.Text, nullable=False, server_default=sa.text("''")),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    ),
)

mapper_registry.map_imperatively(Note, notes_table)
