from pydantic import BaseModel
from typing import Optional

class ApplicantIn(BaseModel):
    id: int
    data_aceite: Optional[str]
    nome: str
    cpf: str
    fonte_indicacao: Optional[str]
    email: str
    email_secundario: Optional[str]
    data_nascimento: Optional[str]
    telefone_celular: Optional[str]
    telefone_recado: Optional[str]
    sexo: Optional[str]
    estado_civil: Optional[str]
    pcd: Optional[bool]
    endereco: Optional[str]
    skype: Optional[str]
    url_linkedin: Optional[str]
    facebook: Optional[str]
    download_cv: Optional[str]
    cv_pt: str
