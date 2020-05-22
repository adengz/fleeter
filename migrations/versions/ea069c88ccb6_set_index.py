"""set index

Revision ID: ea069c88ccb6
Revises: 8221f350c23e
Create Date: 2020-05-21 23:24:36.921733

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea069c88ccb6'
down_revision = '8221f350c23e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_fleets_created_at'), 'fleets', ['created_at'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.drop_constraint('users_username_key', 'users', type_='unique')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('users_username_key', 'users', ['username'])
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_fleets_created_at'), table_name='fleets')
    # ### end Alembic commands ###
