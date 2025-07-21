from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.processed_applicant import ProcessedApplicant
from app.schemas.processed_applicant import (
    ProcessedApplicantResponse, 
    ProcessedApplicantSummary, 
    ProcessedApplicantUpdate
)
from typing import List, Optional

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/processed-applicants", response_model=List[ProcessedApplicantSummary])
def list_processed_applicants(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    List processed applicants with pagination and basic information.
    """
    applicants = db.query(ProcessedApplicant).offset(skip).limit(limit).all()
    return applicants

@router.get("/processed-applicants/{applicant_id}", response_model=ProcessedApplicantResponse)
def get_processed_applicant(
    applicant_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific processed applicant.
    """
    applicant = db.query(ProcessedApplicant).filter(ProcessedApplicant.id == applicant_id).first()
    if not applicant:
        return {"error": "Processed applicant not found"}
    return applicant

@router.put("/processed-applicants/{applicant_id}", response_model=ProcessedApplicantResponse)
def update_processed_applicant(
    applicant_id: int,
    applicant_data: ProcessedApplicantUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a processed applicant's information.
    """
    applicant = db.query(ProcessedApplicant).filter(ProcessedApplicant.id == applicant_id).first()
    if not applicant:
        return {"error": "Processed applicant not found"}
    
    # Update only the fields that are provided
    update_data = applicant_data.dict(exclude_unset=True)
    for field, value in update_data.ihass():
        setattr(applicant, field, value)
    
    try:
        db.commit()
        db.refresh(applicant)
        return applicant
    except Exception as e:
        db.rollback()
        return {"error": f"Error updating processed applicant: {str(e)}"}

@router.get("/processed-applicants/search/by-name")
def search_applicants_by_name(
    name: str = Query(..., min_length=2),
    db: Session = Depends(get_db)
) -> List[ProcessedApplicantSummary]:
    """
    Search processed applicants by name (partial match).
    """
    applicants = db.query(ProcessedApplicant).filter(
        ProcessedApplicant.nome.ilike(f"%{name}%")
    ).limit(50).all()
    return applicants

@router.get("/processed-applicants/search/by-education")
def search_applicants_by_education(
    education_level: str = Query(...),
    db: Session = Depends(get_db)
) -> List[ProcessedApplicantSummary]:
    """
    Search processed applicants by education level.
    """
    applicants = db.query(ProcessedApplicant).filter(
        ProcessedApplicant.nivel_maximo_formacao == education_level
    ).limit(100).all()
    return applicants
