from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

class MatchProspectBase(BaseModel):
    applicant_id: int
    score_semantico: Optional[float] = None
    origin: Optional[str] = None
    selecionado: Optional[bool] = False
    observacoes: Optional[str] = None

class MatchProspectCreate(MatchProspectBase):
    pass

class MatchProspectResponse(MatchProspectBase):
    workbook_id: uuid.UUID
    data_entrada: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class MatchProspectsUpdate(BaseModel):
    workbook_id: uuid.UUID
    prospects: List[MatchProspectCreate]
