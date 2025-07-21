from sqlalchemy import Column, UUID, BigInteger, Text, DateTime, Integer, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class FilterHistory(Base):
    """
    Model representing the history of filters applied to candidate selection processes.
    
    This table tracks all filtering operations performed during candidate selection,
    storing the criteria used and the impact on candidate counts for audit and analysis purposes.
    """
    __tablename__ = "filter_history"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Filter identification and sequencing fields
    workbook_id = Column(UUID(as_uuid=True), nullable=False)  # Reference to the workbook
    filter_step = Column(Integer, nullable=False)  # Filter sequence number (1, 2, 3...)
    
    # Filter criteria and processing fields
    filter_criteria_original = Column(Text, nullable=False)  # Original user criteria
    filter_criteria_extracted = Column(JSON, nullable=True)  # LLM-extracted criteria
    
    # Impact tracking fields
    candidates_before_count = Column(Integer, nullable=False)  # Candidate count before filter
    candidates_after_count = Column(Integer, nullable=False)  # Candidate count after filter
    
    # Filter type and status fields
    filter_type = Column(Text, default='incremental')  # Filter type: 'incremental', 'reset', 'expand'
    created_at = Column(DateTime, default=func.now())  # Creation timestamp
    is_active = Column(Boolean, default=True)  # Whether this filter is currently active
    
    def __repr__(self):
        """String representation for debugging and logging purposes."""
        return f"<FilterHistory(workbook_id={self.workbook_id}, step={self.filter_step}, criteria='{self.filter_criteria_original[:50]}...')>"
