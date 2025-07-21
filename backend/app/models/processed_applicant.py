from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, LargeBinary
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base


class ProcessedApplicant(Base):
    """
    Model representing processed applicant data with semantic analysis.
    
    This table stores comprehensive applicant information including personal data,
    CV processing results, and semantic embeddings for candidate matching.
    """
    __tablename__ = "processed_applicants"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Personal information fields
    data_aceite = Column(DateTime)  # Acceptance date
    nome = Column(String)  # Full name
    cpf = Column(String)  # Brazilian tax ID
    fonte_indicacao = Column(String)  # Referral source
    email = Column(String)  # Primary email
    email_secundario = Column(String)  # Secondary email
    data_nascimento = Column(String)  # Birth date
    telefone_celular = Column(String)  # Mobile phone
    telefone_recado = Column(String)  # Message phone
    sexo = Column(String)  # Gender
    estado_civil = Column(String)  # Marital status
    pcd = Column(Boolean)  # Disability status
    endereco = Column(String)  # Address
    
    # Social media and professional profiles
    skype = Column(String)  # Skype username
    url_linkedin = Column(String)  # LinkedIn profile URL
    facebook = Column(String)  # Facebook profile
    
    # CV and document processing fields
    download_cv = Column(String)  # CV download link or path
    cv_pt_json = Column(JSONB)  # CV data in JSON format
    cv_texto_semantico = Column(Text)  # Semantic text representation of CV
    cv_embedding = Column(LargeBinary)  # Binary embedding data
    nivel_maximo_formacao = Column(String)  # Maximum education level
    cv_embedding_vector = Column(Text)  # Vector embedding as text placeholder
    
    # Metadata fields
    updated_at = Column(DateTime)  # Last update timestamp
