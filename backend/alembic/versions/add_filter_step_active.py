"""Add filter step and active status to match_prospects

Revision ID: add_filter_step_active
Revises: 
Create Date: 2025-07-19 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_filter_step_active'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Adiciona as colunas se não existirem
    try:
        op.add_column('match_prospects', sa.Column('filter_step_added', sa.Integer(), nullable=True, default=1))
    except Exception:
        pass  # Coluna já existe
    
    try:
        op.add_column('match_prospects', sa.Column('is_active', sa.Boolean(), nullable=True, default=True))
    except Exception:
        pass  # Coluna já existe
    
    # Atualiza valores padrão para registros existentes
    op.execute("UPDATE match_prospects SET filter_step_added = 1 WHERE filter_step_added IS NULL")
    op.execute("UPDATE match_prospects SET is_active = true WHERE is_active IS NULL")


def downgrade():
    # Remove as colunas
    try:
        op.drop_column('match_prospects', 'is_active')
        op.drop_column('match_prospects', 'filter_step_added')
    except Exception:
        pass  # Colunas não existem
