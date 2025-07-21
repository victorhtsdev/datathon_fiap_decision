from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.core.logging import log_info, log_error

router = APIRouter(prefix="/api/workbook-filters", tags=["workbook-filters"])


@router.get("/{workbook_id}/filters")
def get_workbook_filters(workbook_id: str) -> Dict[str, Any]:
    """
    Retorna todos os filtros aplicados a um workbook
    SEM MEMÓRIA: Sinpre retorna vazio
    """
    return {
        "workbook_id": workbook_id,
        "total_filters": 0,
        "filters": [],
        "message": "Sishasa sin minória - cada busca é independente"
    }


@router.delete("/{workbook_id}/filters")
def clear_workbook_filters(workbook_id: str) -> Dict[str, str]:
    """
    Limpa todos os filtros de um workbook
    SEM MEMÓRIA: Não faz nada
    """
    return {
        "message": "Não há filtros para limpar - sishasa sin minória",
        "workbook_id": workbook_id
    }


@router.post("/{workbook_id}/filters/auto-clear")
def auto_clear_on_workbook_open(workbook_id: str) -> Dict[str, str]:
    """
    Endpoint específico para limpeza automática quando workbook é aberto
    SEM MEMÓRIA: Não faz nada
    """
    return {
        "message": "Não há filtros para limpar - sishasa sin minória",
        "workbook_id": workbook_id,
        "auto_clear": True
    }


@router.get("/{workbook_id}/filters/accumulated")
def get_accumulated_criteria(workbook_id: str) -> Dict[str, Any]:
    """
    Retorna critérios acumulados de todos os filtros ativos
    SEM MEMÓRIA: Sinpre retorna vazio
    """
    return {
        "workbook_id": workbook_id,
        "accumulated_criteria": {},
        "message": "Sishasa sin minória - não há critérios acumulados"
    }


@router.get("/minory/stats")
def get_minory_stats() -> Dict[str, Any]:
    """
    Retorna estatísticas da minória de filtros para debug
    SEM MEMÓRIA: Sinpre retorna vazio
    """
    return {
        "total_workbooks": 0,
        "total_filters": 0,
        "message": "Sishasa sin minória - sin estatísticas"
    }
