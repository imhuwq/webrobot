"""init migration

Revision ID: c8e10588b7d8
Revises: 
Create Date: 2017-03-19 16:32:20.440481

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8e10588b7d8'
down_revision = None
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
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('password', sa.String(), nullable=True),
    sa.Column('auth_token', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('name'),
    sa.UniqueConstraint('uuid')
    )
    op.create_table('periodic_task',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('role', sa.String(), nullable=True),
    sa.Column('enabled', sa.Boolean(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('task', sa.String(), nullable=False),
    sa.Column('args', sa.Text(), nullable=True),
    sa.Column('kwargs', sa.Text(), nullable=True),
    sa.Column('options', sa.Text(), nullable=True),
    sa.Column('initializer_task_id', sa.Integer(), nullable=True),
    sa.Column('header_task_id', sa.Integer(), nullable=True),
    sa.Column('interval_id', sa.Integer(), nullable=True),
    sa.Column('crontab_id', sa.Integer(), nullable=True),
    sa.Column('last_run_at', sa.DateTime(), nullable=True),
    sa.Column('total_run_count', sa.Integer(), nullable=True),
    sa.Column('max_run_count', sa.Integer(), nullable=True),
    sa.Column('expires', sa.DateTime(), nullable=True),
    sa.Column('start_after', sa.DateTime(), nullable=True),
    sa.Column('run_immediately', sa.Boolean(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('date_changed', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['crontab_id'], ['crontab.id'], ),
    sa.ForeignKeyConstraint(['header_task_id'], ['periodic_task.id'], ),
    sa.ForeignKeyConstraint(['initializer_task_id'], ['periodic_task.id'], ),
    sa.ForeignKeyConstraint(['interval_id'], ['interval.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('periodic_task')
    op.drop_table('users')
    op.drop_table('interval')
    op.drop_table('crontab')
    # ### end Alembic commands ###
