"""Extend unique constraints on keyword/aggregator/company to include is_tour

Revision ID: b3c4d5e6f7a8
Revises: a2b3c4d5e6f7
Create Date: 2026-05-16 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b3c4d5e6f7a8"
down_revision: Union[str, tuple, None] = "a2b3c4d5e6f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("uq_owner_keyword_name", "keyword", type_="unique")
    op.create_unique_constraint("uq_owner_keyword_name", "keyword", ["owner_id", "name", "is_tour"])

    op.drop_constraint("uq_owner_aggregator_name", "aggregator", type_="unique")
    op.create_unique_constraint("uq_owner_aggregator_name", "aggregator", ["owner_id", "name", "is_tour"])

    op.drop_constraint("uq_owner_company_name", "company", type_="unique")
    op.create_unique_constraint("uq_owner_company_name", "company", ["owner_id", "name", "is_tour"])


def downgrade() -> None:
    op.drop_constraint("uq_owner_company_name", "company", type_="unique")
    op.create_unique_constraint("uq_owner_company_name", "company", ["owner_id", "name"])

    op.drop_constraint("uq_owner_aggregator_name", "aggregator", type_="unique")
    op.create_unique_constraint("uq_owner_aggregator_name", "aggregator", ["owner_id", "name"])

    op.drop_constraint("uq_owner_keyword_name", "keyword", type_="unique")
    op.create_unique_constraint("uq_owner_keyword_name", "keyword", ["owner_id", "name"])
