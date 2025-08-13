
from __future__ import annotations
from alembic import op
import sqlalchemy as sa

revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    op.create_table('calendars',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('timezone', sa.String(length=64), nullable=False),
        sa.Column('business_hours', sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column('holidays', sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table('slas',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1000)),
        sa.Column('service', sa.String(length=255), nullable=False),
        sa.Column('metric_type', sa.String(length=128), nullable=False),
        sa.Column('comparator', sa.Enum('>', '>=', '<', '<=', name='comparator'), nullable=False),
        sa.Column('threshold', sa.Float(), nullable=False),
        sa.Column('window_minutes', sa.Integer(), nullable=False, server_default=sa.text('5')),
        sa.Column('grace_period_seconds', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('severity', sa.Enum('low', 'medium', 'high', 'critical', name='severity'), nullable=False, server_default=sa.text("'medium'")),
        sa.Column('owner_team', sa.String(length=255)),
        sa.Column('notification_rules', sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column('calendar_id', sa.Integer(), sa.ForeignKey('calendars.id')),
        sa.Column('suppression_seconds', sa.Integer(), nullable=False, server_default=sa.text('300')),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table('events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('service', sa.String(length=255), nullable=False),
        sa.Column('metric_type', sa.String(length=128), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('event_ts', sa.DateTime(timezone=True), nullable=False),
        sa.Column('idempotency_key', sa.String(length=255)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('idx_events_service_metric_ts', 'events', ['service', 'metric_type', 'event_ts'])
    op.create_unique_constraint('uq_events_idempotency_key', 'events', ['idempotency_key'])

    op.create_table('sla_statuses',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('sla_id', sa.Integer(), sa.ForeignKey('slas.id'), nullable=False),
        sa.Column('state', sa.Enum('normal', 'at_risk', 'breached', 'recovered', name='slastatusstate'), nullable=False, server_default=sa.text("'normal'")),
        sa.Column('last_value', sa.Float()),
        sa.Column('suppression_until_ts', sa.Integer()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table('incidents',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('sla_id', sa.Integer(), sa.ForeignKey('slas.id'), nullable=False),
        sa.Column('status', sa.Enum('open', 'acknowledged', 'resolved', name='incidentstatus'), nullable=False, server_default=sa.text("'open'")),
        sa.Column('severity', sa.String(length=32), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True)),
        sa.Column('acknowledged_by', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('resolved_at', sa.DateTime(timezone=True)),
        sa.Column('owner', sa.String(length=255)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table('alerts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('incident_id', sa.Integer(), sa.ForeignKey('incidents.id')),
        sa.Column('sla_id', sa.Integer(), sa.ForeignKey('slas.id'), nullable=False),
        sa.Column('state', sa.Enum('at_risk', 'breached', 'recovered', name='alertstate'), nullable=False),
        sa.Column('message', sa.String(length=1000), nullable=False),
        sa.Column('severity', sa.String(length=32), nullable=False),
        sa.Column('routing', sa.JSON()),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table('delivery_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('alert_id', sa.Integer(), sa.ForeignKey('alerts.id'), nullable=False),
        sa.Column('provider', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('error_message', sa.String(length=1000)),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('next_retry_at', sa.DateTime(timezone=True)),
        sa.Column('meta', sa.JSON()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('table_name', sa.String(length=128), nullable=False),
        sa.Column('row_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=32), nullable=False),
        sa.Column('actor_email', sa.String(length=255)),
        sa.Column('changes', sa.JSON()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('delivery_logs')
    op.drop_table('alerts')
    op.drop_table('incidents')
    op.drop_table('sla_statuses')
    op.drop_index('idx_events_service_metric_ts', table_name='events')
    op.drop_constraint('uq_events_idempotency_key', 'events', type_='unique')
    op.drop_table('events')
    op.drop_table('slas')
    op.drop_table('calendars')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
