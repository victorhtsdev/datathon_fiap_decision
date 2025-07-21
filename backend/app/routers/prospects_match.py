from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from app.schemas.prospects_match import (
    ApplicantProspectResponse, 
    ProspectMatchByWorkbookResponse, 
    ProspectMatchByVagaResponse
)
from app.services.prospects_match_service import ProspectsMatchService
from app.core.database import SessionLocal
from app.core.logging import log_info, log_error

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_prospects_match_service(db: Session = Depends(get_db)):
    return ProspectsMatchService(db)

@router.get("/prospects-match/by-workbook/{workbook_id}", response_model=ProspectMatchByWorkbookResponse)
def get_prospects_by_workbook(
    workbook_id: str,
    service: ProspectsMatchService = Depends(get_prospects_match_service)
):
    """
    Busca prospects (processed_applicants) por ID do workbook.
    Retorna candidatos da tabela processed_applicants que estão associados 
    ao workbook através da tabela match_prospects.
    """
    try:
        # Validar se é um UUID válido
        uuid.UUID(workbook_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Workbook ID deve ser um UUID válido")
    
    result = service.get_prospects_by_workbook_id(workbook_id)
    
    if not result:
        raise HTTPException(status_code=404, detail=f"No prospects found for workbook {workbook_id}")
    
    return result

@router.get("/prospects-match/by-vaga/{vaga_id}", response_model=ProspectMatchByVagaResponse)
def get_prospects_by_vaga(
    vaga_id: int,
    service: ProspectsMatchService = Depends(get_prospects_match_service)
):
    """
    Busca prospects (processed_applicants) por ID da vaga.
    Retorna candidatos de todos os workbooks associados à vaga,
    buscando na tabela processed_applicants através de match_prospects.
    """
    if vaga_id <= 0:
        raise HTTPException(status_code=400, detail="Vaga ID deve ser um número positivo")
    
    result = service.get_prospects_by_vaga_id(vaga_id)
    
    if not result:
        raise HTTPException(status_code=404, detail=f"No prospects found for job {vaga_id}")
    
    return result

@router.get("/prospects-match/search/by-name", response_model=List[ApplicantProspectResponse])
def search_prospects_by_name(
    name: str = Query(..., min_length=2, description="Candidate name for search (minimum 2 characters)"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results"),
    service: ProspectsMatchService = Depends(get_prospects_match_service)
):
    """
    Busca prospects por nome do candidato (processed_applicants.nome).
    Permite encontrar candidatos cujo nome contenha o termo pesquisado,
    retornando dados combinados de match_prospects e processed_applicants.
    """
    results = service.search_prospects_by_name(name, limit)
    
    if not results:
        raise HTTPException(status_code=404, detail=f"Nenhum prospect encontrado com nome contendo '{name}'")
    
    return results

@router.get("/prospects-match/workbooks/summary")
def get_workbooks_with_prospects_summary(
    service: ProspectsMatchService = Depends(get_prospects_match_service)
):
    """
    Returns a summary of all workbooks that have prospects.
    Useful to discover which workbooks have match_prospects data available.
    """
    results = service.get_workbooks_with_prospects_summary()
    
    if not results:
        raise HTTPException(status_code=404, detail="No workbooks with prospects found")
    
    return {
        "total_workbooks": len(results),
        "workbooks": results
    }
