"""phase13_reports_and_exports

Revision ID: be474161a1a0
Revises: fb2e85ecc260
Create Date: 2024-12-13 08:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'be474161a1a0'
down_revision: Union[str, None] = 'fb2e85ecc260'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create reports table
    op.create_table('reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('report_type', sa.String(50), nullable=False),
        sa.Column('fields', postgresql.JSON(), nullable=False),
        sa.Column('filters', postgresql.JSON()),
        sa.Column('grouping', postgresql.JSON()),
        sa.Column('aggregations', postgresql.JSON()),
        sa.Column('sorting', postgresql.JSON()),
        sa.Column('is_template', sa.Boolean(), default=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_by_admin_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.ForeignKeyConstraint(['template_id'], ['reports.id']),
        sa.ForeignKeyConstraint(['created_by_admin_id'], ['admin_users.id'])
    )

    # Create indexes for reports
    op.create_index('ix_reports_report_type', 'reports', ['report_type'])
    op.create_index('ix_reports_is_template', 'reports', ['is_template'])
    op.create_index('ix_reports_created_by_admin_id', 'reports', ['created_by_admin_id'])
    op.create_index('ix_reports_created_at', 'reports', ['created_at'])

    # Create report_schedules table
    op.create_table('report_schedules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('report_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('frequency', sa.String(20), nullable=False),
        sa.Column('cron_expression', sa.String(100)),
        sa.Column('day_of_week', sa.Integer()),
        sa.Column('day_of_month', sa.Integer()),
        sa.Column('time_of_day', sa.String(5)),
        sa.Column('delivery_method', sa.String(20), default='email'),
        sa.Column('recipients', postgresql.JSON(), nullable=False),
        sa.Column('export_format', sa.String(10), default='pdf'),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('last_run', sa.DateTime()),
        sa.Column('next_run', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['report_id'], ['reports.id'], ondelete='CASCADE')
    )

    # Create indexes for report_schedules
    op.create_index('ix_report_schedules_report_id', 'report_schedules', ['report_id'])
    op.create_index('ix_report_schedules_frequency', 'report_schedules', ['frequency'])
    op.create_index('ix_report_schedules_is_active', 'report_schedules', ['is_active'])
    op.create_index('ix_report_schedules_next_run', 'report_schedules', ['next_run'])

    # Create report_exports table
    op.create_table('report_exports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('report_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('export_format', sa.String(10), nullable=False),
        sa.Column('file_path', sa.String(500)),
        sa.Column('file_size', sa.Integer()),
        sa.Column('generated_by_admin_id', postgresql.UUID(as_uuid=True)),
        sa.Column('generated_at', sa.DateTime(), nullable=False),
        sa.Column('record_count', sa.Integer()),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('error_message', sa.Text()),
        sa.ForeignKeyConstraint(['report_id'], ['reports.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['generated_by_admin_id'], ['admin_users.id'])
    )

    # Create indexes for report_exports
    op.create_index('ix_report_exports_report_id', 'report_exports', ['report_id'])
    op.create_index('ix_report_exports_generated_at', 'report_exports', ['generated_at'])
    op.create_index('ix_report_exports_status', 'report_exports', ['status'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_report_exports_status', table_name='report_exports')
    op.drop_index('ix_report_exports_generated_at', table_name='report_exports')
    op.drop_index('ix_report_exports_report_id', table_name='report_exports')
    op.drop_table('report_exports')

    op.drop_index('ix_report_schedules_next_run', table_name='report_schedules')
    op.drop_index('ix_report_schedules_is_active', table_name='report_schedules')
    op.drop_index('ix_report_schedules_frequency', table_name='report_schedules')
    op.drop_index('ix_report_schedules_report_id', table_name='report_schedules')
    op.drop_table('report_schedules')

    op.drop_index('ix_reports_created_at', table_name='reports')
    op.drop_index('ix_reports_created_by_admin_id', table_name='reports')
    op.drop_index('ix_reports_is_template', table_name='reports')
    op.drop_index('ix_reports_report_type', table_name='reports')
    op.drop_table('reports')
