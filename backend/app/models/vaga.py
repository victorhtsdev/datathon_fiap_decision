from sqlalchemy import Column, BigInteger, Text, DateTime, Boolean, Enum
from sqlalchemy.dialects.postgresql import BYTEA
from app.core.database import Base
from datetime import datetime
import enum


class StatusVaga(enum.Enum):
    """Enumeration for job position status values."""
    nao_iniciada = "nao_iniciada"  # Not started
    aberta = "aberta"  # Open
    em_andamento = "em_andamento"  # In progress
    fechada = "fechada"  # Closed


class Vaga(Base):
    """
    Model representing a job position with all its requirements and specifications.
    
    This table stores comprehensive job information including basic details, profile requirements,
    benefits, and semantic processing data for candidate matching.
    """
    __tablename__ = "vagas"
    
    # Primary key
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Basic job information fields
    informacoes_basicas_data_requicisao = Column(Text)  # Request date
    informacoes_basicas_limite_esperado_para_contratacao = Column(Text)  # Expected hiring deadline
    informacoes_basicas_titulo_vaga = Column(Text)  # Job title
    informacoes_basicas_vaga_sap = Column(Text)  # SAP job ID
    informacoes_basicas_cliente = Column(Text)  # Client
    informacoes_basicas_solicitante_cliente = Column(Text)  # Client requester
    informacoes_basicas_empresa_divisao = Column(Text)  # Company division
    informacoes_basicas_requisitante = Column(Text)  # Requester
    informacoes_basicas_analista_responsavel = Column(Text)  # Responsible analyst
    informacoes_basicas_tipo_contratacao = Column(Text)  # Contract type
    informacoes_basicas_prazo_contratacao = Column(Text)  # Contract duration
    informacoes_basicas_objetivo_vaga = Column(Text)  # Job objective
    informacoes_basicas_prioridade_vaga = Column(Text)  # Job priority
    informacoes_basicas_origem_vaga = Column(Text)  # Job origin
    informacoes_basicas_superior_imediato = Column(Text)  # Immediate supervisor
    informacoes_basicas_nome = Column(Text)  # Name
    informacoes_basicas_telefone = Column(Text)  # Phone
    
    # Job profile and location fields
    perfil_vaga_pais = Column(Text)  # Country
    perfil_vaga_estado = Column(Text)  # State
    perfil_vaga_cidade = Column(Text)  # City
    perfil_vaga_bairro = Column(Text)  # Neighborhood
    perfil_vaga_regiao = Column(Text)  # Region
    perfil_vaga_local_trabalho = Column(Text)  # Work location
    perfil_vaga_vaga_especifica_para_pcd = Column(Text)  # PCD specific position
    perfil_vaga_faixa_etaria = Column(Text)  # Age range
    perfil_vaga_horario_trabalho = Column(Text)  # Work schedule
    perfil_vaga_nivel_profissional = Column(Text)  # Professional level
    perfil_vaga_nivel_academico = Column(Text)  # Academic level
    perfil_vaga_nivel_ingles = Column(Text)  # English level
    perfil_vaga_nivel_espanhol = Column(Text)  # Spanish level
    perfil_vaga_outro_idioma = Column(Text)  # Other languages
    perfil_vaga_areas_atuacao = Column(Text)  # Areas of expertise
    perfil_vaga_principais_atividades = Column(Text)  # Main activities
    perfil_vaga_competencia_tecnicas_e_comportamentais = Column(Text)  # Technical and behavioral competencies
    perfil_vaga_demais_observacoes = Column(Text)  # Additional observations
    perfil_vaga_viagens_requeridas = Column(Text)  # Required travel
    perfil_vaga_equipamentos_necessarios = Column(Text)  # Required equipment
    
    # Benefits and compensation fields
    beneficios_valor_venda = Column(Text)  # Sales value
    beneficios_valor_compra_1 = Column(Text)  # Purchase value 1
    beneficios_valor_compra_2 = Column(Text)  # Purchase value 2
    
    # Additional basic information fields
    informacoes_basicas_data_inicial = Column(Text)  # Start date
    informacoes_basicas_data_final = Column(Text)  # End date
    perfil_vaga_habilidades_comportamentais_necessarias = Column(Text)  # Required behavioral skills
    informacoes_basicas_nome_substituto = Column(Text)  # Substitute name
    
    # Semantic processing and search fields
    vaga_texto_semantico = Column(Text)  # Semantic text representation
    vaga_embedding = Column(BYTEA)  # Binary embedding data
    vaga_embedding_vector = Column(Text)  # Vector embedding as text placeholder
    
    # Metadata fields
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Last update timestamp
    status_vaga = Column(Enum(StatusVaga), default=StatusVaga.nao_iniciada)  # Job status
