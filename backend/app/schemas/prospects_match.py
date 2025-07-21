from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class ApplicantProspectResponse(BaseModel):
    # Dados do match_prospect
    workbook_id: str
    applicant_id: int
    score_semantico: Optional[float] = None
    origin: Optional[str] = None
    selecionado: Optional[bool] = False
    data_entrada: Optional[datetime] = None
    observacoes: Optional[str] = None
    
    # Dados do processed_applicant
    nome: Optional[str] = None
    email: Optional[str] = None
    cpf: Optional[str] = None
    telefone_celular: Optional[str] = None
    nivel_maximo_formacao: Optional[str] = None
    cv_pt: Optional[Dict[str, Any]] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ProspectMatchByWorkbookResponse(BaseModel):
    workbook_id: str
    vaga_id: int
    vaga_titulo: Optional[str] = None
    prospects: List[ApplicantProspectResponse]
    total_prospects: int

class ProspectMatchByVagaResponse(BaseModel):
    vaga_id: int
    vaga_titulo: Optional[str] = None
    workbooks: List[ProspectMatchByWorkbookResponse]
    total_prospects: int
