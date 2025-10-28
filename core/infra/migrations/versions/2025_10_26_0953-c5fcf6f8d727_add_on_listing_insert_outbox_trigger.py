"""add_on_listing_insert_outbox_trigger

Revision ID: c5fcf6f8d727
Revises: 9e03fd58b153
Create Date: 2025-10-26 09:53:57.263929

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c5fcf6f8d727"
down_revision: Union[str, Sequence[str], None] = "9e03fd58b153"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE OR REPLACE FUNCTION trg_listings_outbox()
        RETURNS trigger AS $$
        BEGIN
        INSERT INTO outbox_messages(message_type, aggregate_type, aggregate_id, payload, processing_attempts)
        VALUES ('listing.created', 'listing', NEW.id,
                jsonb_build_object('listing_id', NEW.id, 'title', NEW.title, 'source_id', NEW.source_id), 0);
        RETURN NEW;
        END; $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER listings_to_outbox
            AFTER INSERT ON listings
            FOR EACH ROW EXECUTE FUNCTION trg_listings_outbox();
        """
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS listings_to_outbox ON listings;")
    op.execute("DROP FUNCTION IF EXISTS trg_listings_outbox();")
    pass
