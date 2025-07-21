from pydantic import BaseModel
from typing import Optional


class ApplicantIn(BaseModel):
    """
    Input schema for applicant data submission.
    
    This schema defines the structure for applicant information
    when creating or updating candidate records in the system.
    """
    id: int  # Unique applicant identifier
    data_aceite: Optional[str]  # Application acceptance date
    nome: str  # Full name
    cpf: str  # Brazilian tax ID
    fonte_indicacao: Optional[str]  # Referral source
    email: str  # Primary email address
    email_secundario: Optional[str]  # Secondary email address
    data_nascimento: Optional[str]  # Birth date
    telefone_celular: Optional[str]  # Mobile phone number
    telefone_recado: Optional[str]  # Message phone number
    sexo: Optional[str]  # Gender
    estado_civil: Optional[str]  # Marital status
    pcd: Optional[bool]  # Disability status
    endereco: Optional[str]  # Address
    skype: Optional[str]  # Skype username
    url_linkedin: Optional[str]  # LinkedIn profile URL
    facebook: Optional[str]  # Facebook profile
    download_cv: Optional[str]  # CV download link
    cv_pt: str  # CV content in Portuguese
