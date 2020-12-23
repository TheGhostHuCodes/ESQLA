"""Add cookie model

Revision ID: 1c95c9036ddf
Revises: b05a0df0eda3
Create Date: 2020-12-22 18:24:42.826899

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1c95c9036ddf"
down_revision = "b05a0df0eda3"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(  # pylint: disable=no-member
        "cookies",
        sa.Column("cookie_id", sa.Integer(), nullable=False),
        sa.Column("cookie_name", sa.String(length=50), nullable=True),
        sa.Column("cookie_recipe_url", sa.String(length=255), nullable=True),
        sa.Column("cookie_sku", sa.String(length=55), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=True),
        sa.Column("unit_cost", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.PrimaryKeyConstraint("cookie_id"),
    )
    op.create_index(  # pylint: disable=no-member
        op.f("ix_cookies_cookie_name"),  # pylint: disable=no-member
        "cookies",
        ["cookie_name"],
        unique=False,
    )


def downgrade():
    op.drop_index(  # pylint: disable=no-member
        op.f("ix_cookies_cookie_name"),  # pylint: disable=no-member
        table_name="cookies",
    )
    op.drop_table("cookies")  # pylint: disable=no-member
