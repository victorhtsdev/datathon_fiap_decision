from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import uuid

class WorkbookBase(BaseModel):
    vaga_id: int = Field(..., gt=0, description="ID da vaga deve ser positivo")
    criado_por: Optional[str] = Field(None, max_length=255, description="Email ou nome do criador")
    
    @validator('criado_por')
    def validate_criado_por(cls, v):
        if v and len(v.strip()) == 0:
            raise ValueError('criado_por não pode ser string vazia')
        return v

class WorkbookCreate(WorkbookBase):
    pass

class WorkbookUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(aberto|fechado|em_andamento)$")
    fechado_em: Optional[datetime] = None
    criado_por: Optional[str] = Field(None, max_length=255)
    
    @validator('fechado_em')
    def validate_fechado_em(cls, v, values):
        if v and values.get('status') != 'fechado':
            raise ValueError('fechado_em só pode ser definido quando status=fechado')
        return v

class WorkbookResponse(WorkbookBase):
    id: uuid.UUID
    criado_em: Optional[datetime] = None
    fechado_em: Optional[datetime] = None
    status: Optional[str] = None
    vaga_titulo: Optional[str] = None  # Título da vaga associada
    
    class Config:
        from_attributes = True
