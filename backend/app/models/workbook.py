from sqlalchemy import Column, String, BigInteger, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Workbook(Base):
    """
    Model representing a workbook for job recruitment processes.
    
    A workbook serves as a container for managing the recruitment process of a specific job position,
    tracking its lifecycle from creation to closure and storing related candidate matches.
    """
    __tablename__ = "workbook"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Job reference and workflow fields
    vaga_id = Column(BigInteger, nullable=False)  # Reference to the job position
    criado_em = Column(DateTime, server_default=func.now())  # Creation timestamp
    fechado_em = Column(DateTime, nullable=True)  # Closing timestamp
    status = Column(Text, default='aberto')  # Workbook status (open/closed)
    criado_por = Column(Text, nullable=True)  # User who created the workbook
    
    # Relationships
    match_prospects = relationship("MatchProspect", back_populates="workbook")
