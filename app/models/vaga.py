from sqlalchemy import Column, BigInteger, Text
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import declarative_base
from sqlalchemy import Text
from sqlalchemy import DateTime
from datetime import datetime

Base = declarative_base()


class Vaga(Base):
    __tablename__ = "vagas"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    informacoes_basicas_data_requicisao = Column(Text)
    informacoes_basicas_limite_esperado_para_contratacao = Column(Text)
    informacoes_basicas_titulo_vaga = Column(Text)
    informacoes_basicas_vaga_sap = Column(Text)
    informacoes_basicas_cliente = Column(Text)
    informacoes_basicas_solicitante_cliente = Column(Text)
    informacoes_basicas_empresa_divisao = Column(Text)
    informacoes_basicas_requisitante = Column(Text)
    informacoes_basicas_analista_responsavel = Column(Text)
    informacoes_basicas_tipo_contratacao = Column(Text)
    informacoes_basicas_prazo_contratacao = Column(Text)
    informacoes_basicas_objetivo_vaga = Column(Text)
    informacoes_basicas_prioridade_vaga = Column(Text)
    informacoes_basicas_origem_vaga = Column(Text)
    informacoes_basicas_superior_imediato = Column(Text)
    informacoes_basicas_nome = Column(Text)
    informacoes_basicas_telefone = Column(Text)
    perfil_vaga_pais = Column(Text)
    perfil_vaga_estado = Column(Text)
    perfil_vaga_cidade = Column(Text)
    perfil_vaga_bairro = Column(Text)
    perfil_vaga_regiao = Column(Text)
    perfil_vaga_local_trabalho = Column(Text)
    perfil_vaga_vaga_especifica_para_pcd = Column(Text)
    perfil_vaga_faixa_etaria = Column(Text)
    perfil_vaga_horario_trabalho = Column(Text)
    perfil_vaga_nivel_profissional = Column(Text)
    perfil_vaga_nivel_academico = Column(Text)
    perfil_vaga_nivel_ingles = Column(Text)
    perfil_vaga_nivel_espanhol = Column(Text)
    perfil_vaga_outro_idioma = Column(Text)
    perfil_vaga_areas_atuacao = Column(Text)
    perfil_vaga_principais_atividades = Column(Text)
    perfil_vaga_competencia_tecnicas_e_comportamentais = Column(Text)
    perfil_vaga_demais_observacoes = Column(Text)
    perfil_vaga_viagens_requeridas = Column(Text)
    perfil_vaga_equipamentos_necessarios = Column(Text)
    beneficios_valor_venda = Column(Text)
    beneficios_valor_compra_1 = Column(Text)
    beneficios_valor_compra_2 = Column(Text)
    informacoes_basicas_data_inicial = Column(Text)
    informacoes_basicas_data_final = Column(Text)
    perfil_vaga_habilidades_comportamentais_necessarias = Column(Text)
    informacoes_basicas_nome_substituto = Column(Text)
    vaga_texto_semantico = Column(Text)
    vaga_embedding = Column(BYTEA)
    vaga_embedding_vector = Column(Text)  # Use Text as a placeholder for VECTOR
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
