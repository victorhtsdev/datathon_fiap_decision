from sqlalchemy import Column, UUID, BigInteger, Text, DateTime, Integer, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class FilterHistory(Base):
    __tablename__ = "filter_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workbook_id = Column(UUID(as_uuid=True), nullable=False)
    filter_step = Column(Integer, nullable=False)  # Sequência dos filtros (1, 2, 3...)
    filter_criteria_original = Column(Text, nullable=False)  # Critério original do usuário
    filter_criteria_extracted = Column(JSON, nullable=True)  # Critérios extraídos pelo LLM
    candidates_before_count = Column(Integer, nullable=False)  # Quantos candidatos antes do filtro
    candidates_after_count = Column(Integer, nullable=False)  # Quantos candidatos após o filtro
    filter_type = Column(Text, default='incremental')  # 'incremental', 'reset', 'expand'
    created_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)  # Se este filtro está ativo
    
    # Para facilitar queries
    def __repr__(self):
        return f"<FilterHistory(workbook_id={self.workbook_id}, step={self.filter_step}, criteria='{self.filter_criteria_original[:50]}...')>"
