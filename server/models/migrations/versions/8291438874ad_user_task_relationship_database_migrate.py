"""user-task relationship database migrate

Revision ID: 8291438874ad
Revises: d502cfd729d6
Create Date: 2017-03-21 01:01:42.158287

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8291438874ad'
down_revision = 'd502cfd729d6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'tasks', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'user_id')
    # ### end Alembic commands ###
