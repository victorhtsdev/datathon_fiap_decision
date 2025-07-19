from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.match_prospect import MatchProspectResponse
from app.schemas.workbook import WorkbookCreate, WorkbookResponse, WorkbookUpdate
from app.services.workbook_service import WorkbookService
from app.dependencies import get_db, get_workbook_service
from typing import List
import uuid

router = APIRouter()

@router.get("/workbook")
def listar_workbooks(service: WorkbookService = Depends(get_workbook_service)):
    """Lista todos os workbooks com título da vaga"""
    return service.repository.get_all()

@router.post("/workbook", response_model=WorkbookResponse)
def criar_workbook(
    workbook_data: WorkbookCreate,
    service: WorkbookService = Depends(get_workbook_service)
):
    """Cria um novo workbook"""
    return service.create_workbook(workbook_data)

@router.get("/workbook/{workbook_id}", response_model=WorkbookResponse)
def get_workbook(
    workbook_id: uuid.UUID,
    service: WorkbookService = Depends(get_workbook_service)
):
    """Busca um workbook específico"""
    return service.get_workbook(workbook_id)

@router.put("/workbook/{workbook_id}", response_model=WorkbookResponse)
def update_workbook(
    workbook_id: uuid.UUID,
    workbook_data: WorkbookUpdate,
    service: WorkbookService = Depends(get_workbook_service)
):
    """Atualiza um workbook"""
    return service.update_workbook(workbook_id, workbook_data)

@router.post("/workbook/{workbook_id}/match-prospects")
def update_match_prospects(
    workbook_id: uuid.UUID,
    prospects_data: dict,  # Simplificado por enquanto
    service: WorkbookService = Depends(get_workbook_service)
):
    """Atualiza match prospects de um workbook"""
    prospects = [prospect for prospect in prospects_data.get("prospects", [])]
    result = service.update_match_prospects(workbook_id, prospects)
    
    return {
        "message": f"Successfully updated {len(result)} match prospects for workbook {workbook_id}",
        "workbook_id": str(workbook_id),
        "prospects_count": len(result)
    }

@router.get("/workbook/{workbook_id}/match-prospects", response_model=List[MatchProspectResponse])
def get_match_prospects(
    workbook_id: uuid.UUID,
    service: WorkbookService = Depends(get_workbook_service)
):
    """Busca match prospects de um workbook"""
    return service.get_match_prospects(workbook_id)

@router.delete("/workbook/{workbook_id}")
def deletar_workbook(
    workbook_id: uuid.UUID,
    service: WorkbookService = Depends(get_workbook_service)
):
    """Deleta um workbook"""
    return service.delete_workbook(workbook_id)
