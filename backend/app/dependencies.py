from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.workbook_service import WorkbookService

def get_db():
    """Dependency para sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_workbook_service(db: Session = Depends(get_db)) -> WorkbookService:
    """Dependency para o WorkbookService"""
    return WorkbookService(db)
