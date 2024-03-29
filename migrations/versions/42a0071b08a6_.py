"""empty message

Revision ID: 42a0071b08a6
Revises: 248ffefb1c46
Create Date: 2019-03-22 14:18:56.412593

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '42a0071b08a6'
down_revision = '248ffefb1c46'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('prediction', 'customer_count')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('prediction', sa.Column('customer_count', sa.INTEGER(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
