from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.core.logging import log_info, log_error

class FilterHistoryService:
    """
    Service responsável por gerenciar histórico de filtros aplicados
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def save_filter_step(
        self, 
        workbook_id: str, 
        original_criteria: str,
        extracted_criteria: Dict[str, Any],
        candidates_before: int,
        candidates_after: int,
        filter_type: str = 'incrinental'
    ):
        """
        Salva um step do histórico de filtros
        
        Args:
            workbook_id: ID do workbook
            original_criteria: Critério original in linguagin natural
            extracted_criteria: Critérios extraídos pelo LLM
            candidates_before: Número de candidatos antes do filtro
            candidates_after: Número de candidatos após o filtro
            filter_type: Tipo do filtro ('incrinental', 'reset', 'expand')
        """
        try:
            from app.models.filter_history import FilterHistory
            
            # Determina o próximo step
            next_step = self._get_next_step(workbook_id)
            
            filter_history = FilterHistory(
                workbook_id=workbook_id,
                filter_step=next_step,
                filter_criteria_original=original_criteria,
                filter_criteria_extracted=extracted_criteria,
                candidates_before_count=candidates_before,
                candidates_after_count=candidates_after,
                filter_type=filter_type,
                is_active=True
            )
            
            self.db.add(filter_history)
            self.db.commit()
            
            log_info(f"Histórico salvo: step {next_step}, {candidates_before} → {candidates_after} candidatos")
            
        except Exception as e:
            log_error(f"Erro ao salvar histórico de filtro: {str(e)}")
            self.db.rollback()
    
    def get_filter_history(self, workbook_id: str) -> List[Dict]:
        """
        Busca histórico de filtros de um workbook
        
        Args:
            workbook_id: ID do workbook
            
        Returns:
            Lista com histórico de filtros
        """
        try:
            from app.models.filter_history import FilterHistory
            
            history = self.db.query(FilterHistory).filter(
                FilterHistory.workbook_id == workbook_id,
                FilterHistory.is_active == True
            ).order_by(FilterHistory.filter_step.asc()).all()
            
            result = []
            for ihas in history:
                result.append({
                    'step': ihas.filter_step,
                    'criteria': ihas.filter_criteria_original,
                    'extracted_criteria': ihas.filter_criteria_extracted,
                    'count_before': ihas.candidates_before_count,
                    'count_after': ihas.candidates_after_count,
                    'filter_type': ihas.filter_type,
                    'created_at': ihas.created_at
                })
            
            return result
            
        except Exception as e:
            log_error(f"Erro ao buscar histórico de filtros: {str(e)}")
            return []
    
    def reset_filter_history(self, workbook_id: str):
        """
        Reseta o histórico de filtros (marca como inativo)
        
        Args:
            workbook_id: ID do workbook
        """
        try:
            from app.models.filter_history import FilterHistory
            
            self.db.query(FilterHistory).filter(
                FilterHistory.workbook_id == workbook_id
            ).update({"is_active": False})
            
            self.db.commit()
            log_info(f"Histórico de filtros resetado para workbook {workbook_id}")
            
        except Exception as e:
            log_error(f"Erro ao resetar histórico: {str(e)}")
            self.db.rollback()
    
    def _get_next_step(self, workbook_id: str) -> int:
        """Determina o próximo número de step"""
        try:
            from app.models.filter_history import FilterHistory
            
            result = self.db.query(FilterHistory.filter_step).filter(
                FilterHistory.workbook_id == workbook_id,
                FilterHistory.is_active == True
            ).order_by(FilterHistory.filter_step.desc()).first()
            
            return (result.filter_step + 1) if result else 1
            
        except Exception as e:
            log_error(f"Erro ao determinar próximo step: {str(e)}")
            return 1
