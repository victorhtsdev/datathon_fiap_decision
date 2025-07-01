from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, LargeBinary
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base

class ProcessedApplicant(Base):
    __tablename__ = "processed_applicants"
    id = Column(Integer, primary_key=True, index=True)
    data_aceite = Column(DateTime)
    nome = Column(String)
    cpf = Column(String)
    fonte_indicacao = Column(String)
    email = Column(String)
    email_secundario = Column(String)
    data_nascimento = Column(String)
    telefone_celular = Column(String)
    telefone_recado = Column(String)
    sexo = Column(String)
    estado_civil = Column(String)
    pcd = Column(Boolean)
    endereco = Column(String)
    skype = Column(String)
    url_linkedin = Column(String)
    facebook = Column(String)
    download_cv = Column(String)
    cv_pt_json = Column(JSONB)
    cv_texto_semantico = Column(Text)
    cv_embedding = Column(LargeBinary)
    nivel_maximo_formacao = Column(String)
    cv_embedding_vector = Column(Text)  # Use Text as a placeholder for VECTOR
    updated_at = Column(DateTime)
