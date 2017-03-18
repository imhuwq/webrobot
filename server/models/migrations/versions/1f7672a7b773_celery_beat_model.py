"""celery beat model

Revision ID: 1f7672a7b773
Revises: d3a02055a1de
Create Date: 2017-03-18 14:27:30.758683

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1f7672a7b773'
down_revision = 'd3a02055a1de'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('crontab',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('minute', sa.String(), nullable=False),
    sa.Column('hour', sa.String(), nullable=False),
    sa.Column('day_of_week', sa.String(), nullable=False),
    sa.Column('day_of_month', sa.String(), nullable=False),
    sa.Column('month_of_year', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('interval',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('every', sa.Integer(), nullable=False),
    sa.Column('period', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('periodic_task',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('task', sa.String(), nullable=False),
    sa.Column('_args', sa.Text(), nullable=True),
    sa.Column('_kwargs', sa.Text(), nullable=True),
    sa.Column('queue', sa.String(), nullable=True),
    sa.Column('exchange', sa.String(), nullable=True),
    sa.Column('routing_key', sa.String(), nullable=True),
    sa.Column('soft_time_limit', sa.Integer(), nullable=True),
    sa.Column('expires', sa.DateTime(), nullable=True),
    sa.Column('start_after', sa.DateTime(), nullable=True),
    sa.Column('enabled', sa.Boolean(), nullable=True),
    sa.Column('last_run_at', sa.DateTime(), nullable=True),
    sa.Column('_total_run_count', sa.Integer(), nullable=True),
    sa.Column('_max_run_count', sa.Integer(), nullable=True),
    sa.Column('date_changed', sa.DateTime(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('run_immediately', sa.Boolean(), nullable=True),
    sa.Column('interval_id', sa.Integer(), nullable=True),
    sa.Column('crontab_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['crontab_id'], ['crontab.id'], ),
    sa.ForeignKeyConstraint(['interval_id'], ['interval.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('periodic_task')
    op.drop_table('interval')
    op.drop_table('crontab')
    # ### end Alembic commands ###