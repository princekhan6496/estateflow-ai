"""add lead AI analysis timestamp

Revision ID: 0003_ai_analyzed_at
Revises: 0002_budget_inr
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_ai_analyzed_at"
down_revision = "0002_budget_inr"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("leads", sa.Column("ai_analyzed_at", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("leads", "ai_analyzed_at")
