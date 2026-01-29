
"""autogen:20260128173310 - initial schema

Revision ID: 2e3418fca3f1
Revises: 
Create Date: 2026-01-28 17:33:11.150334

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2e3418fca3f1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create core tables from SQLAlchemy models
    op.create_table(
        'sessions',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('persona', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'conversation_state',
        sa.Column('session_id', sa.String(), primary_key=True),
        sa.Column('turn_count', sa.Integer(), nullable=True),
        sa.Column('last_agent_reply', sa.Text(), nullable=True),
        sa.Column('messages_json', sa.Text(), nullable=True),
        sa.Column('slots_json', sa.Text(), nullable=True),
        sa.Column('human_override', sa.Boolean(), nullable=True),
    )

    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('sender', sa.String(), nullable=True),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('raw', sa.Text(), nullable=True),
    )

    op.create_table(
        'extractions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('value', sa.String(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
    )

    op.create_table(
        'outgoing_messages',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    # Create indexes used by the application
    op.create_index('ix_messages_session_id', 'messages', ['session_id'])
    op.create_index('ix_extractions_session_id', 'extractions', ['session_id'])
    op.create_index('ix_outgoing_messages_session_id', 'outgoing_messages', ['session_id'])


def downgrade():
    # Drop indexes and tables in reverse order
    try:
        op.drop_index('ix_outgoing_messages_session_id', table_name='outgoing_messages')
    except Exception:
        pass
    try:
        op.drop_index('ix_extractions_session_id', table_name='extractions')
    except Exception:
        pass
    try:
        op.drop_index('ix_messages_session_id', table_name='messages')
    except Exception:
        pass

    op.drop_table('outgoing_messages')
    op.drop_table('extractions')
    op.drop_table('messages')
    op.drop_table('conversation_state')
    op.drop_table('sessions')
