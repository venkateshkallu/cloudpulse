"""Initial schema creation

Revision ID: 001
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create logs table
    op.create_table('logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('level', sa.String(length=20), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('service_name', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_timestamp_desc', 'logs', [sa.text('timestamp DESC')], unique=False)
    op.create_index('idx_service_level', 'logs', ['service_name', 'level'], unique=False)
    op.create_index('idx_service_timestamp', 'logs', ['service_name', sa.text('timestamp DESC')], unique=False)
    op.create_index(op.f('ix_logs_id'), 'logs', ['id'], unique=False)
    op.create_index(op.f('ix_logs_level'), 'logs', ['level'], unique=False)
    op.create_index(op.f('ix_logs_service_name'), 'logs', ['service_name'], unique=False)

    # Create services table
    op.create_table('services',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('uptime', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('last_checked', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_status', 'services', ['status'], unique=False)
    op.create_index('idx_last_checked', 'services', [sa.text('last_checked DESC')], unique=False)
    op.create_index(op.f('ix_services_id'), 'services', ['id'], unique=False)

    # Create metrics table
    op.create_table('metrics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('metric_name', sa.String(length=50), nullable=False),
        sa.Column('value', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('unit', sa.String(length=20), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_metric_timestamp', 'metrics', ['metric_name', sa.text('timestamp DESC')], unique=False)
    op.create_index('idx_timestamp_desc', 'metrics', [sa.text('timestamp DESC')], unique=False)
    op.create_index(op.f('ix_metrics_id'), 'metrics', ['id'], unique=False)
    op.create_index(op.f('ix_metrics_metric_name'), 'metrics', ['metric_name'], unique=False)


def downgrade() -> None:
    # Drop metrics table
    op.drop_index(op.f('ix_metrics_metric_name'), table_name='metrics')
    op.drop_index(op.f('ix_metrics_id'), table_name='metrics')
    op.drop_index('idx_timestamp_desc', table_name='metrics')
    op.drop_index('idx_metric_timestamp', table_name='metrics')
    op.drop_table('metrics')

    # Drop services table
    op.drop_index(op.f('ix_services_id'), table_name='services')
    op.drop_index('idx_last_checked', table_name='services')
    op.drop_index('idx_status', table_name='services')
    op.drop_table('services')

    # Drop logs table
    op.drop_index(op.f('ix_logs_service_name'), table_name='logs')
    op.drop_index(op.f('ix_logs_level'), table_name='logs')
    op.drop_index(op.f('ix_logs_id'), table_name='logs')
    op.drop_index('idx_service_timestamp', table_name='logs')
    op.drop_index('idx_service_level', table_name='logs')
    op.drop_index('idx_timestamp_desc', table_name='logs')
    op.drop_table('logs')