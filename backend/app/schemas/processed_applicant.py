from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class ProcessedApplicantBase(BaseModel):
    nome: Optional[str] = None
    cpf: Optional[str] = None
    fonte_indicacao: Optional[str] = None
    email: Optional[str] = None
    email_secundario: Optional[str] = None
    data_nascimento: Optional[str] = None
    telefone_celular: Optional[str] = None
    telefone_recado: Optional[str] = None
    sexo: Optional[str] = None
    estado_civil: Optional[str] = None
    pcd: Optional[bool] = None
    endereco: Optional[str] = None
    skype: Optional[str] = None
    url_linkedin: Optional[str] = None
    facebook: Optional[str] = None
    download_cv: Optional[str] = None

class ProcessedApplicantCreate(ProcessedApplicantBase):
    data_aceite: Optional[datetime] = None
    cv_pt_json: Optional[Dict[str, Any]] = None
    cv_texto_semantico: Optional[str] = None
    nivel_maximo_formacao: Optional[str] = None

class ProcessedApplicantUpdate(BaseModel):
    nome: Optional[str] = None
    cpf: Optional[str] = None
    fonte_indicacao: Optional[str] = None
    email: Optional[str] = None
    email_secundario: Optional[str] = None
    data_nascimento: Optional[str] = None
    telefone_celular: Optional[str] = None
    telefone_recado: Optional[str] = None
    sexo: Optional[str] = None
    estado_civil: Optional[str] = None
    pcd: Optional[bool] = None
    endereco: Optional[str] = None
    skype: Optional[str] = None
    url_linkedin: Optional[str] = None
    facebook: Optional[str] = None
    download_cv: Optional[str] = None
    cv_pt_json: Optional[Dict[str, Any]] = None
    cv_texto_semantico: Optional[str] = None
    nivel_maximo_formacao: Optional[str] = None

class ProcessedApplicantResponse(ProcessedApplicantBase):
    id: int
    data_aceite: Optional[datetime] = None
    cv_pt_json: Optional[Dict[str, Any]] = None
    cv_texto_semantico: Optional[str] = None
    nivel_maximo_formacao: Optional[str] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schema for search/listing with minimal fields
class ProcessedApplicantSummary(BaseModel):
    id: int
    nome: Optional[str] = None
    email: Optional[str] = None
    nivel_maximo_formacao: Optional[str] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
