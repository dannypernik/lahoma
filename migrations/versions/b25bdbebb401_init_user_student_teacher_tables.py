"""init user, client, teacher tables

Revision ID: b25bdbebb401
Revises: 
Create Date: 2022-04-22 22:46:36.770634

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b25bdbebb401'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('teacher',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=64), nullable=True),
    sa.Column('last_name', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.Column('timezone', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=24), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('teacher', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_teacher_email'), ['email'], unique=False)
        batch_op.create_index(batch_op.f('ix_teacher_first_name'), ['first_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_teacher_status'), ['status'], unique=False)

    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=32), nullable=True),
    sa.Column('last_name', sa.String(length=32), nullable=True),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.Column('phone', sa.String(length=32), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('about_me', sa.String(length=500), nullable=True),
    sa.Column('last_viewed', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_email'), ['email'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_first_name'), ['first_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_last_name'), ['last_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_phone'), ['phone'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_username'), ['username'], unique=True)

    op.create_table('client',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=64), nullable=True),
    sa.Column('last_name', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.Column('timezone', sa.Integer(), nullable=True),
    sa.Column('location', sa.String(length=128), nullable=True),
    sa.Column('status', sa.String(length=24), nullable=True),
    sa.Column('teacher_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['teacher_id'], ['teacher.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_email'), ['email'], unique=False)
        batch_op.create_index(batch_op.f('ix_client_first_name'), ['first_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_client_status'), ['status'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_client_status'))
        batch_op.drop_index(batch_op.f('ix_client_first_name'))
        batch_op.drop_index(batch_op.f('ix_email'))

    op.drop_table('client')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_username'))
        batch_op.drop_index(batch_op.f('ix_user_phone'))
        batch_op.drop_index(batch_op.f('ix_user_last_name'))
        batch_op.drop_index(batch_op.f('ix_user_first_name'))
        batch_op.drop_index(batch_op.f('ix_user_email'))

    op.drop_table('user')
    with op.batch_alter_table('teacher', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_teacher_status'))
        batch_op.drop_index(batch_op.f('ix_teacher_first_name'))
        batch_op.drop_index(batch_op.f('ix_teacher_email'))

    op.drop_table('teacher')
    # ### end Alembic commands ###