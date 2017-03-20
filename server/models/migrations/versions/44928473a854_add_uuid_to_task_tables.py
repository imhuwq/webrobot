"""empty message

Revision ID: 44928473a854
Revises: c8e10588b7d8
Create Date: 2017-03-20 23:17:26.278821

"""
from alembic import op
import sqlalchemy as sa

from server.utils import gen_uuid

# revision identifiers, used by Alembic.
revision = '44928473a854'
down_revision = 'c8e10588b7d8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('crontab', sa.Column('uuid', sa.String()))
    op.create_unique_constraint(None, 'crontab', ['uuid'])
    op.add_column('interval', sa.Column('uuid', sa.String()))
    op.create_unique_constraint(None, 'interval', ['uuid'])
    op.add_column('periodic_task', sa.Column('uuid', sa.String()))
    op.create_unique_constraint(None, 'periodic_task', ['uuid'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'periodic_task', type_='unique')
    op.drop_column('periodic_task', 'uuid')
    op.drop_constraint(None, 'interval', type_='unique')
    op.drop_column('interval', 'uuid')
    op.drop_constraint(None, 'crontab', type_='unique')
    op.drop_column('crontab', 'uuid')
    # ### end Alembic commands ###
