"""empty message

Revision ID: 2b67b3592374
Revises: beae7758e660
Create Date: 2025-03-21 21:22:18.795890

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b67b3592374'
down_revision: Union[str, None] = 'beae7758e660'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Events', 'Description',
               existing_type=sa.TEXT(),
               type_=sa.String(length=500),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Events', 'Description',
               existing_type=sa.String(length=500),
               type_=sa.TEXT(),
               existing_nullable=True)
    # ### end Alembic commands ###
