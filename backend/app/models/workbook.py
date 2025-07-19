from sqlalchemy import Column, String, BigInteger, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class Workbook(Base):
    __tablename__ = "workbook"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vaga_id = Column(BigInteger, nullable=False)
    criado_em = Column(DateTime, server_default=func.now())
    fechado_em = Column(DateTime, nullable=True)
    status = Column(Text, default='aberto')
    criado_por = Column(Text, nullable=True)
    
    # Relationships
    match_prospects = relationship("MatchProspect", back_populates="workbook")
