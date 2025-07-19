from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, LargeBinary
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base

class ProcessedApplicant(Base):
    __tablename__ = "processed_applicants"
    id = Column(Integer, primary_key=True, index=True)
    data_aceite = Column(DateTime)  # acceptance_date
    nome = Column(String)  # name
    cpf = Column(String)
    fonte_indicacao = Column(String)  # referral_source
    email = Column(String)
    email_secundario = Column(String)  # secondary_email
    data_nascimento = Column(String)  # birth_date
    telefone_celular = Column(String)  # mobile_phone
    telefone_recado = Column(String)  # message_phone
    sexo = Column(String)  # gender
    estado_civil = Column(String)  # marital_status
    pcd = Column(Boolean)
    endereco = Column(String)  # address
    skype = Column(String)
    url_linkedin = Column(String)
    facebook = Column(String)
    download_cv = Column(String)
    cv_pt_json = Column(JSONB)
    cv_texto_semantico = Column(Text)
    cv_embedding = Column(LargeBinary)
    nivel_maximo_formacao = Column(String)  # max_education_level
    cv_embedding_vector = Column(Text)  # Use Text as a placeholder for VECTOR
    updated_at = Column(DateTime)
