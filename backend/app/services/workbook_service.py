from typing import List, Optional, Any
import uuid
from sqlalchemy.orm import Session
from app.repositories.workbook_repository import WorkbookRepository
from app.repositories.vaga_repository import get_vaga_by_id
from app.models.match_prospect import MatchProspect
from app.core.exceptions import APIExceptions
from app.core.logging import log_info, log_error

class WorkbookService:
    """Camada de serviço para regras de negócio do Workbook"""
    
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
            vaga.status_vaga = 'em_andamento'
            self.db.commit()
            
            log_info(f"Workbook {workbook.id} criado para vaga {vaga_id} e status da vaga atualizado para 'em_andamento'")
            
            return workbook
        except Exception as e:
            self.db.rollback()
            log_error(f"Erro ao criar workbook: {str(e)}")
            APIExceptions.internal_error("Erro ao criar workbook")
    
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
                    origem=data.get('origin'),
                    selecionado=data.get('selecionado', False),
                    observacoes=data.get('observacoes')
                )
                new_prospects.append(prospect)
            
            self.db.add_all(new_prospects)
            self.db.commit()
            
            log_info(f"Atualizados {len(new_prospects)} match prospects para workbook {workbook_id}")
            return new_prospects
            
        except Exception as e:
            self.db.rollback()
            log_error(f"Erro ao atualizar match prospects: {str(e)}")
            APIExceptions.internal_error("Erro ao atualizar match prospects")
    
    def get_match_prospects(self, workbook_id: uuid.UUID):
        """Busca match prospects de um workbook"""
        # Verifica se o workbook existe
        self.get_workbook(workbook_id)
        
        return self.db.query(MatchProspect).filter(
            MatchProspect.workbook_id == workbook_id
        ).all()
    
    def delete_workbook(self, workbook_id: uuid.UUID):
        """Remove workbook e reverte status da vaga para 'aberta'"""
        # Busca o workbook
        workbook = self.get_workbook(workbook_id)
        
        try:
            # Busca vaga associada para reverter status
            vaga = get_vaga_by_id(self.db, workbook.vaga_id)
            if vaga:
                # Reverte status da vaga para 'aberta' para permitir criação de novo workbook
                vaga.status_vaga = 'aberta'
            
            # Remove os match prospects associados
            self.db.query(MatchProspect).filter(
                MatchProspect.workbook_id == workbook_id
            ).delete()
            
            # Remove o workbook
            self.db.delete(workbook)
            self.db.commit()
            
            log_info(f"Workbook {workbook_id} removido e vaga {workbook.vaga_id} revertida para status 'aberta'")
            
            return {"message": f"Workbook {workbook_id} removido com sucesso"}
            
        except Exception as e:
            self.db.rollback()
            log_error(f"Erro ao remover workbook {workbook_id}: {str(e)}")
            APIExceptions.internal_error("Erro ao remover workbook")
