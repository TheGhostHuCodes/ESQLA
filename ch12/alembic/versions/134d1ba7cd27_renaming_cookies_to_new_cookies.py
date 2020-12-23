"""Renaming cookies to new_cookies

Revision ID: 134d1ba7cd27
Revises: 1c95c9036ddf
Create Date: 2020-12-22 19:42:35.198593

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "134d1ba7cd27"
down_revision = "1c95c9036ddf"
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table("cookies", "new_cookies")  # pylint: disable=no-member


def downgrade():
    op.rename_table("new_cookies", "cookies")  # pylint: disable=no-member
