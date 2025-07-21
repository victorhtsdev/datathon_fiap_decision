from sqlalchemy import Column, UUID, BigInteger, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class MatchProspect(Base):
    """
    Model representing the relationship between workbooks and prospects/applicants with their matching scores.
    
    This table stores the results of semantic matching between job positions (workbooks) and candidates,
    including their compatibility scores and selection status.
    """
    __tablename__ = "match_prospects"
    
    # Primary key composite fields
    workbook_id = Column(UUID(as_uuid=True), ForeignKey('workbook.id'), primary_key=True)
    applicant_id = Column(BigInteger, primary_key=True)
    
    # Matching and scoring fields
    score_semantico = Column(Float)  # Semantic similarity score between job and candidate
    origem = Column(Text)  # Source or origin of the match
    selecionado = Column(Boolean, default=False)  # Whether the candidate has been selected
    data_entrada = Column(DateTime, default=func.now())  # Entry timestamp
    observacoes = Column(Text)  # Additional observations or notes
    
    # Relationships
    workbook = relationship("Workbook", back_populates="match_prospects")
