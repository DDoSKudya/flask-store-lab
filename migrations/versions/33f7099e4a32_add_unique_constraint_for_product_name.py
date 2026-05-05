"""add unique constraint for product name

Revision ID: 33f7099e4a32
Revises: 10e42b13e595
Create Date: 2026-05-05 17:45:11.263797

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '33f7099e4a32'
down_revision: Union[str, Sequence[str], None] = '10e42b13e595'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("products") as batch_op:
        batch_op.create_unique_constraint(
            "uq_products_name",
            ["name"],
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("products") as batch_op:
        batch_op.drop_constraint(
            "uq_products_name",
            type_="unique",
        )
