"""initial migration

Revision ID: 94dbf0569ee3
Revises: 
Create Date: 2025-05-29 21:50:31.082396
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from routers.auth import get_password_hash

revision: str = '94dbf0569ee3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, index=True),
        sa.Column('role', sa.String(50)),
        sa.Column('email', sa.String(255), unique=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('username', sa.String(50), unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('disabled', sa.Boolean(), default=False)
    )
    
    password_hash = get_password_hash("admin123")
    
    op.execute(
        f"""
        INSERT INTO "user" (role, email, username, password_hash, disabled, created_at)
        VALUES ('admin', 'admin@example.com', 'admin123', '{password_hash}', false, NOW())
        """
    )

    op.create_table(
        'client',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, index=True),
        sa.Column('firstname', sa.String(50)),
        sa.Column('surename', sa.String(50)),
        sa.Column('middlename', sa.String(50)),
        sa.Column('gender', sa.String(10), default='unknown'),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id')),
        sa.UniqueConstraint('firstname', 'surename', name='fullname_constraint')
    )

    op.create_table(
        'service',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, index=True),
        sa.Column('name', sa.String(100), unique=True),
        sa.Column('description', sa.Text()),
        sa.Column('room', sa.Integer()),
        sa.Column('avg_minute', sa.Integer()),
        sa.Column('image_url', sa.Text()),
        sa.Column('from_time', sa.Time()),
        sa.Column('to_time', sa.Time()),
        sa.Column('available_days', sa.Text()),
        sa.Column('disabled', sa.Boolean(), default=False)
    )

    op.create_table(
        'queue',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, index=True),
        sa.Column('client_id', sa.Integer(), sa.ForeignKey('user.id')),
        sa.Column('service_id', sa.Integer(), sa.ForeignKey('service.id')),
        sa.Column('number', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('time', sa.Time(), nullable=False),
        sa.Column('step', sa.Integer(), default=1),
        sa.Column('in_room', sa.Boolean(), default=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('comment', sa.String(255), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('queue')
    op.drop_table('service')
    op.drop_table('client')
    op.drop_table('user')
