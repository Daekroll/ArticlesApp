"""confirm link

Revision ID: 3e37037a26e3
Revises: 09c568dea267
Create Date: 2025-04-06 19:10:51.511345

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e37037a26e3'
down_revision: Union[str, None] = '09c568dea267'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
