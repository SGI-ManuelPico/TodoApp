"""add estado column to todo table

Revision ID: a5ba606fb030
Revises: f250bf9ea547
Create Date: 2025-03-31 09:22:06.188842

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a5ba606fb030'
down_revision: Union[str, None] = 'f250bf9ea547'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('todo', sa.Column('estado', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('todo', 'estado')
    # ### end Alembic commands ###
