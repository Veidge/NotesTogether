"""add default tags

Revision ID: c37a623d51e4
Revises: 12d9ce543481
Create Date: 2026-11-14 14:42:04.569828

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c37a623d51e4'
down_revision: Union[str, Sequence[str], None] = '12d9ce543481'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        INSERT INTO tags (name, default_tag, user_id)
        VALUES
            ('Учёба', TRUE, NULL),       
            ('Работа', TRUE, NULL),       
            ('Спорт', TRUE, NULL),       
            ('Отдых', TRUE, NULL),       
            ('Идеи', TRUE, NULL),       
            ('Важное', TRUE, NULL),       
            ('Личное', TRUE, NULL)
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        DELETE FROM tags
        WHERE default_tag = TRUE
            AND name IN ('Учёба', 'Работа', 'Спорт', 'Отдых', 'Идеи', 'Важное', 'Личное')
            AND user_id IS NULL;
    """)
