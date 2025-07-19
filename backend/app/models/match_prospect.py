from sqlalchemy import Column, UUID, BigInteger, Float, Text, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class MatchProspect(Base):
    __tablename__ = "match_prospects"
    
    workbook_id = Column(UUID(as_uuid=True), ForeignKey('workbook.id'), primary_key=True)
    applicant_id = Column(BigInteger, primary_key=True)
    score_semantico = Column(Float)
    origem = Column(Text)
    selecionado = Column(Boolean, default=False)
    data_entrada = Column(DateTime, default=func.now())
    observacoes = Column(Text)
    filter_step_added = Column(Integer, default=1)  # Em qual step do filtro foi adicionado
    is_active = Column(Boolean, default=True)  # Se está ativo na seleção atual
    
    # Relationships
    workbook = relationship("Workbook", back_populates="match_prospects")
