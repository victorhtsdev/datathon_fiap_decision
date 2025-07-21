from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime


class TopPositionStats(BaseModel):
    """Estatísticas para uma posição específica no ranking"""
    quantidade: int
    percentual: float


class MetricasGerais(BaseModel):
    """Métricas gerais da performance semântica"""
    total_aprovados: int
    media_posicao: float
    mediana_posicao: float
    desvio_padrao: float
    vagas_analisadas: int
    vagas_com_ranking_semantico: int


class HistogramPoint(BaseModel):
    """Ponto de dados para o histograma"""
    posicao: int
    quantidade: int


class StatusDistribution(BaseModel):
    """Distribuição por status dos candidatos"""
    status: str
    quantidade: int


class PgVectorInfo(BaseModel):
    """Informações sobre o operador pgvector utilizado"""
    operador_usado: str
    tipo_distancia: str
    interpretacao: str
    range_tipico: str
    ordenacao: str


class InterpretacaoEstruturada(BaseModel):
    """Interpretação estruturada dos resultados"""
    titulo: str
    visao_geral: Dict[str, Any]
    metricas_precisao: List[Dict[str, Any]]
    analise_detalhada: List[Dict[str, Any]]
    conclusao: Dict[str, Any]


class SemanticPerformanceResponse(BaseModel):
    """Resposta completa da análise de performance semântica"""
    metricas_gerais: MetricasGerais
    distribuicao_top_positions: Dict[str, TopPositionStats]
    histogram_data: List[HistogramPoint]
    status_distribution: List[StatusDistribution]
    pgvector_info: PgVectorInfo
    mensagem_interpretacao: str
    interpretacao_estruturada: InterpretacaoEstruturada
    generated_at: str
    
    class Config:
        from_attributes = True


class CacheClearResponse(BaseModel):
    """Resposta da operação de limpeza de cache"""
    success: bool
    message: str
