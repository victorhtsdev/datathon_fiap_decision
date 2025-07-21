from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.semantic_performance_service import SemanticPerformanceService
from app.schemas.semantic_performance import SemanticPerformanceResponse, CacheClearResponse
from app.core.logging import log_info, log_error

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


def get_db():
    """Dependency para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_semantic_performance_service(db: Session = Depends(get_db)) -> SemanticPerformanceService:
    """Dependency para obter o serviço de performance semântica"""
    return SemanticPerformanceService(db)


@router.get("/semantic-performance", response_model=SemanticPerformanceResponse)
def get_semantic_performance_analysis(
    service: SemanticPerformanceService = Depends(get_semantic_performance_service)
):
    """
    Retorna análise de performance da busca semântica.
    
    Esta API analisa a eficácia do algoritmo de busca semântica comparando
    as posições dos candidatos aprovados no ranking gerado pela similaridade
    de vetores (pgvector <=> operador de distância de cosseno).
    
    **Funcionamento:**
    - Busca vagas que tiveram candidatos aprovados
    - Para cada vaga, calcula o ranking dos candidatos baseado na similaridade semântica
    - Analisa em que posições estavam os candidatos que foram efetivamente aprovados
    - Gera métricas agregadas e distribuições
    
    **Cache:**
    - Os dados são calculados uma vez por dia e armazenados em cache
    - Se os dados foram calculados hoje, retorna do cache para performance
    - Para forçar recálculo, use o endpoint de clear cache
    
    **Métricas retornadas:**
    - Total de candidatos aprovados analisados
    - Média e mediana da posição no ranking
    - Distribuição por top positions (Top 1, 3, 5, 10, 20)
    - Histograma das posições
    - Distribuição por status de aprovação
    - Informações técnicas sobre o pgvector
    """
    try:
        log_info("Iniciando análise de performance semântica")
        result = service.get_performance_analysis()
        log_info("Análise de performance semântica concluída")
        return result
    except Exception as e:
        log_error(f"Erro na análise de performance semântica: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Erro interno ao calcular análise de performance"
        )


@router.delete("/semantic-performance/cache", response_model=CacheClearResponse)
def clear_semantic_performance_cache(
    service: SemanticPerformanceService = Depends(get_semantic_performance_service)
):
    """
    Remove o cache da análise de performance semântica.
    
    Use este endpoint para forçar o recálculo dos dados na próxima
    chamada da API de análise de performance.
    
    **Quando usar:**
    - Quando novos dados foram adicionados e você quer ver a análise atualizada
    - Para debugging ou testes
    - Se suspeitar que o cache está corrompido
    """
    try:
        success = service.clear_cache()
        if success:
            return CacheClearResponse(
                success=True,
                message="Cache removido com sucesso. Próxima consulta recalculará os dados."
            )
        else:
            return CacheClearResponse(
                success=False,
                message="Nenhum cache encontrado para remover."
            )
    except Exception as e:
        log_error(f"Erro ao remover cache: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao remover cache"
        )


@router.get("/semantic-performance/info")
def get_semantic_performance_info():
    """
    Retorna informações sobre a análise de performance semântica.
    
    Endpoint informativo que explica como funciona a análise,
    sem executar cálculos pesados.
    """
    return {
        "titulo": "Análise de Performance da Busca Semântica",
        "descricao": "Esta análise mede a eficácia do algoritmo de matching semântico",
        "metodologia": {
            "step_1": "Identifica vagas com candidatos aprovados",
            "step_2": "Para cada vaga, ranqueia candidatos por similaridade semântica (pgvector)",
            "step_3": "Verifica posições dos candidatos que foram efetivamente aprovados",
            "step_4": "Calcula métricas agregadas de performance"
        },
        "metricas_principais": [
            "Média de posição dos aprovados no ranking",
            "Percentual de aprovados no Top 1, 3, 5, 10",
            "Distribuição das posições (histograma)",
            "Total de candidatos e vagas analisadas"
        ],
        "tecnologia": {
            "operador": "pgvector <=> (distância de cosseno)",
            "interpretacao": "Menor distância = maior similaridade semântica",
            "base_dados": "Tabelas: vagas, processed_applicants, prospects"
        },
        "cache": {
            "duracao": "1 dia (até meia-noite)",
            "objetivo": "Otimizar performance das consultas",
            "localizacao": "temp_cache/semantic_performance_cache.json"
        }
    }
