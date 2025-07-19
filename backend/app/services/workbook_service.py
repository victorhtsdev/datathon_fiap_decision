from typing import List, Optional, Any
import uuid
from sqlalchemy.orm import Session
from app.repositories.workbook_repository import WorkbookRepository
from app.repositories.vaga_repository import get_vaga_by_id
from app.models.match_prospect import MatchProspect
from app.core.exceptions import APIExceptions
from app.core.logging import log_info, log_error

class WorkbookService:
    """Service layer para regras de negócio do Workbook"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = WorkbookRepository(db)
    
    def create_workbook(self, workbook_data: Any):
        """Cria um workbook verificando se a vaga existe e atualiza seu status"""
        # Verifica se a vaga existe
        vaga_id = workbook_data.vaga_id if hasattr(workbook_data, 'vaga_id') else workbook_data.get('vaga_id')
        criado_por = workbook_data.criado_por if hasattr(workbook_data, 'criado_por') else workbook_data.get('criado_por')
        
        vaga = get_vaga_by_id(self.db, vaga_id)
        if not vaga:
            APIExceptions.not_found("Vaga", str(vaga_id))
        
        try:
            # Cria o workbook
            workbook = self.repository.create(
                vaga_id=vaga_id,
                criado_por=criado_por
            )
            
            # Atualiza o status da vaga para 'em_andamento' 
            # (indica que tem workbook criado e está em processo de análise)
            vaga.status_vaga = 'em_andamento'
            self.db.commit()
            
            log_info(f"Created workbook {workbook.id} for vaga {vaga_id} and updated vaga status to 'em_andamento'")
            
            return workbook
        except Exception as e:
            self.db.rollback()
            log_error(f"Error creating workbook: {str(e)}")
            APIExceptions.internal_error("Error creating workbook")
    
    def get_workbook(self, workbook_id: uuid.UUID):
        """Busca um workbook por ID"""
        workbook = self.repository.get_by_uuid(workbook_id)
        if not workbook:
            APIExceptions.not_found("Workbook", str(workbook_id))
        return workbook
    
    def update_workbook(self, workbook_id: uuid.UUID, workbook_data: Any):
        """Atualiza um workbook"""
        if hasattr(workbook_data, 'dict'):
            update_data = workbook_data.dict(exclude_unset=True)
        else:
            update_data = workbook_data
        
        workbook = self.repository.update_by_uuid(workbook_id, **update_data)
        if not workbook:
            APIExceptions.not_found("Workbook", str(workbook_id))
        return workbook
    
    def update_match_prospects(self, workbook_id: uuid.UUID, prospects: List[Any]):
        """Atualiza os match prospects (overwrite)"""
        # Verifica se o workbook existe
        workbook = self.get_workbook(workbook_id)
        
        try:
            # Remove prospects existentes
            self.db.query(MatchProspect).filter(
                MatchProspect.workbook_id == workbook_id
            ).delete()
            
            # Cria novos prospects
            new_prospects = []
            for prospect_data in prospects:
                if hasattr(prospect_data, 'dict'):
                    data = prospect_data.dict()
                else:
                    data = prospect_data
                    
                prospect = MatchProspect(
                    workbook_id=workbook_id,
                    applicant_id=data.get('applicant_id'),
                    score_semantico=data.get('score_semantico'),
                    origem=data.get('origem'),
                    selecionado=data.get('selecionado', False),
                    observacoes=data.get('observacoes')
                )
                new_prospects.append(prospect)
            
            self.db.add_all(new_prospects)
            self.db.commit()
            
            log_info(f"Updated {len(new_prospects)} match prospects for workbook {workbook_id}")
            return new_prospects
            
        except Exception as e:
            self.db.rollback()
            log_error(f"Error updating match prospects: {str(e)}")
            APIExceptions.internal_error("Error updating match prospects")
    
    def get_match_prospects(self, workbook_id: uuid.UUID):
        """Busca match prospects de um workbook"""
        # Verifica se o workbook existe
        self.get_workbook(workbook_id)
        
        return self.db.query(MatchProspect).filter(
            MatchProspect.workbook_id == workbook_id
        ).all()
    
    def delete_workbook(self, workbook_id: uuid.UUID):
        """Deleta um workbook e reverte o status da vaga para 'aberta'"""
        # Busca o workbook
        workbook = self.get_workbook(workbook_id)
        
        try:
            # Busca a vaga associada para reverter o status
            vaga = get_vaga_by_id(self.db, workbook.vaga_id)
            if vaga:
                # Reverte o status da vaga para 'aberta' para permitir nova criação de workbook
                vaga.status_vaga = 'aberta'
            
            # Remove os match prospects associados
            self.db.query(MatchProspect).filter(
                MatchProspect.workbook_id == workbook_id
            ).delete()
            
            # Remove o workbook
            self.db.delete(workbook)
            self.db.commit()
            
            log_info(f"Deleted workbook {workbook_id} and reverted vaga {workbook.vaga_id} status to 'aberta'")
            
            return {"message": f"Workbook {workbook_id} deleted successfully"}
            
        except Exception as e:
            self.db.rollback()
            log_error(f"Error deleting workbook {workbook_id}: {str(e)}")
            APIExceptions.internal_error("Error deleting workbook")
