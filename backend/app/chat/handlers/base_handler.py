from abc import ABC, abstractmethod
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.chat.models.chat_session import ChatSession


class BaseChatHandler(ABC):
    """
    Classe base para todos os handlers de chat
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    @abstractmethod
    def handle(self, parameters: Dict[str, Any], session: ChatSession) -> Dict[str, Any]:
        """
        Processa a solicitação do usuário
        
        Args:
            parameters: Parameters extraídos da mensagem
            session: Sessão de chat atual
            
        Returns:
            Dict contendo:
            - response: str - resposta para o usuário
            - filtered_candidates: List[Dict] | None
            - total_candidates: int | None
        """
        pass
    
    def _create_response(
        self, 
        response: str, 
        filtered_candidates=None, 
        total_candidates=None
    ) -> Dict[str, Any]:
        """Helper para criar resposta padronizada"""
        return {
            'response': response,
            'filtered_candidates': filtered_candidates,
            'total_candidates': total_candidates
        }
