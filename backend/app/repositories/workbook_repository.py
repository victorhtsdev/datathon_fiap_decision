from typing import Optional, List
import uuid
from sqlalchemy.orm import Session, joinedload
from app.models.workbook import Workbook
from app.models.vaga import Vaga
from app.repositories.base_repository import BaseRepository

class WorkbookRepository(BaseRepository[Workbook]):
    @property
    def model(self):
        return Workbook
    
    def get_all(self) -> List[dict]:
        """Returns all workbooks with job title"""
        result = self.db.query(
            Workbook.id,
            Workbook.vaga_id,
            Workbook.criado_por,
            Workbook.criado_em,
            Workbook.fechado_em,
            Workbook.status,
            Vaga.informacoes_basicas_titulo_vaga.label('vaga_titulo')
        ).join(
            Vaga, Workbook.vaga_id == Vaga.id
        ).order_by(Workbook.criado_em.desc()).all()
        
        workbooks = []
        for row in result:
            # Create an object that simulates the Workbook model but with vaga_titulo
            workbook_dict = {
                'id': row.id,
                'vaga_id': row.vaga_id,
                'criado_por': row.criado_por,
                'criado_em': row.criado_em,
                'fechado_em': row.fechado_em,
                'status': row.status,
                'vaga_titulo': row.vaga_titulo
            }
            workbooks.append(workbook_dict)
        
        return workbooks
    
    def get_by_uuid(self, workbook_id: uuid.UUID) -> Optional[Workbook]:
        return self.db.query(Workbook).filter(Workbook.id == workbook_id).first()
    
    def get_workbook(self, workbook_id: str) -> Optional[Workbook]:
        """Search workbook by string UUID"""
        try:
            workbook_uuid = uuid.UUID(workbook_id)
            return self.get_by_uuid(workbook_uuid)
        except (ValueError, TypeError):
            return None
    
    def get_by_vaga_id(self, vaga_id: int) -> List[Workbook]:
        return self.db.query(Workbook).filter(Workbook.vaga_id == vaga_id).all()
    
    def update_by_uuid(self, workbook_id: uuid.UUID, **kwargs) -> Optional[Workbook]:
        db_obj = self.get_by_uuid(workbook_id)
        if not db_obj:
            return None
        
        for field, value in kwargs.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def delete_by_uuid(self, workbook_id: uuid.UUID) -> bool:
        """Delete a workbook by UUID"""
        workbook = self.get_by_uuid(workbook_id)
        if not workbook:
            return False
        
        self.db.delete(workbook)
        self.db.commit()
        return True
