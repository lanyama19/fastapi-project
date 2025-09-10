"""add content column to posts table

Revision ID: c3175020dacd
Revises: dbd518c78a6d
Create Date: 2025-09-09 16:38:31.598369

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3175020dacd'
down_revision: Union[str, Sequence[str], None] = 'dbd518c78a6d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
