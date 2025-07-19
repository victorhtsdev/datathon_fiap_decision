from typing import Optional
from pydantic import BaseModel
from enum import Enum

class StatusVaga(str, Enum):
    nao_iniciada = "nao_iniciada"
    aberta = "aberta"
    em_andamento = "em_andamento"
    em_analise = "em_analise"
    pausada = "pausada"
    finalizada = "finalizada"
    cancelada = "cancelada"

class VagaBase(BaseModel):
    id: Optional[int] = None
    informacoes_basicas_data_requicisao: Optional[str] = None
    informacoes_basicas_limite_esperado_para_contratacao: Optional[str] = None
    informacoes_basicas_titulo_vaga: Optional[str] = None
    informacoes_basicas_vaga_sap: Optional[str] = None
    informacoes_basicas_cliente: Optional[str] = None
    informacoes_basicas_solicitante_cliente: Optional[str] = None
    informacoes_basicas_empresa_divisao: Optional[str] = None
    informacoes_basicas_requisitante: Optional[str] = None
    informacoes_basicas_analista_responsavel: Optional[str] = None
    informacoes_basicas_tipo_contratacao: Optional[str] = None
    informacoes_basicas_prazo_contratacao: Optional[str] = None
    informacoes_basicas_objetivo_vaga: Optional[str] = None
    informacoes_basicas_prioridade_vaga: Optional[str] = None
    informacoes_basicas_origem_vaga: Optional[str] = None
    informacoes_basicas_superior_imediato: Optional[str] = None
    informacoes_basicas_nome: Optional[str] = None
    informacoes_basicas_telefone: Optional[str] = None
    perfil_vaga_pais: Optional[str] = None
    perfil_vaga_estado: Optional[str] = None
    perfil_vaga_cidade: Optional[str] = None
    perfil_vaga_bairro: Optional[str] = None
    perfil_vaga_regiao: Optional[str] = None
    perfil_vaga_local_trabalho: Optional[str] = None
    perfil_vaga_vaga_especifica_para_pcd: Optional[str] = None
    perfil_vaga_faixa_etaria: Optional[str] = None
    perfil_vaga_horario_trabalho: Optional[str] = None
    perfil_vaga_nivel_profissional: Optional[str] = None
    perfil_vaga_nivel_academico: Optional[str] = None
    perfil_vaga_nivel_ingles: Optional[str] = None
    perfil_vaga_nivel_espanhol: Optional[str] = None
    perfil_vaga_outro_idioma: Optional[str] = None
    perfil_vaga_areas_atuacao: Optional[str] = None
    perfil_vaga_principais_atividades: Optional[str] = None
    perfil_vaga_competencia_tecnicas_e_comportamentais: Optional[str] = None
    perfil_vaga_demais_observacoes: Optional[str] = None
    perfil_vaga_viagens_requeridas: Optional[str] = None
    perfil_vaga_equipamentos_necessarios: Optional[str] = None
    beneficios_valor_venda: Optional[str] = None
    beneficios_valor_compra_1: Optional[str] = None
    beneficios_valor_compra_2: Optional[str] = None
    informacoes_basicas_data_inicial: Optional[str] = None
    informacoes_basicas_data_final: Optional[str] = None
    perfil_vaga_habilidades_comportamentais_necessarias: Optional[str] = None
    informacoes_basicas_nome_substituto: Optional[str] = None
    status_vaga: Optional[StatusVaga] = StatusVaga.aberta

class VagaCreate(VagaBase):
    pass

class VagaUpdate(VagaBase):
    pass

class VagaInDB(VagaBase):
    id: Optional[int] = None
    vaga_texto_semantico: Optional[str] = None
    vaga_embedding: Optional[bytes] = None
    vaga_embedding_vector: Optional[list] = None
    status_vaga: Optional[StatusVaga] = None

    class Config:
        from_attributes = True
