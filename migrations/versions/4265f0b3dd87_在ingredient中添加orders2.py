"""在ingredient中添加orders2

Revision ID: 4265f0b3dd87
Revises: a6622e3507a8
Create Date: 2023-05-20 20:38:51.672286

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4265f0b3dd87'
down_revision = 'a6622e3507a8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('order_item',
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('ingredient_id', sa.String(length=200), nullable=True),
    sa.Column('quality', sa.String(length=200), nullable=True),
    sa.ForeignKeyConstraint(['ingredient_id'], ['ingredient.id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('order_item')
    # ### end Alembic commands ###
