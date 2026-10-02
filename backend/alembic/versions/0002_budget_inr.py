from alembic import op
import sqlalchemy as sa

revision = "0002_budget_inr"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    # Existing v1 seed data stored monetary values in lakh units.
    # Convert once to the canonical INR representation used by the application.
    op.execute(sa.text("UPDATE leads SET budget = budget * 100000"))
    op.execute(sa.text("UPDATE properties SET price = price * 100000"))


def downgrade():
    op.execute(sa.text("UPDATE leads SET budget = budget / 100000"))
    op.execute(sa.text("UPDATE properties SET price = price / 100000"))
