from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.chat.services.chat_orchestrator import ChatOrchestrator
from app.core.logging import log_info, log_error


class ChatService:
    """
    Service principal para gerenciar conversas com LLM.
    Agora atua como uma facade para o ChatOrchestrator.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.orchestrator = ChatOrchestrator(db)
    
    async def chat_with_context(
        self, 
        message: str, 
        workbook_id: Optional[str] = None, 
        context: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Realiza uma conversa com o LLM usando a nova arquitetura modular
        
        Args:
            message: Mensagem do usuário
            workbook_id: ID do workbook (contexto da vaga)
            context: Contexto adicional (legacy, não usado na nova arquitetura)
            session_id: ID da sessão (opcional)
        
        Returns:
            Dict contendo:
            - response: str - resposta do LLM
            - session_id: str - ID da sessão
            - filtered_candidates: List[Dict] | None - candidatos filtrados (se aplicável)
            - total_candidates: int | None - total de candidatos encontrados
            - intent: str - intenção classificada
            - confidence: float - confiança da classificação
        """
        try:
            log_info(f"Processing chat message via new architecture: {message[:100]}...")
            
            result = await self.orchestrator.process_message(
                message=message,
                session_id=session_id,
                workbook_id=workbook_id,
                context=context
            )
            
            # Retorna resultado com formato compatível com a API existente
            return {
                'response': result.get('response', ''),
                'session_id': result.get('session_id'),
                'filtered_candidates': result.get('filtered_candidates'),
                'total_candidates': result.get('total_candidates'),
                'intent': result.get('intent'),
                'confidence': result.get('confidence')
            }
            
        except Exception as e:
            log_error(f"Error in ChatService: {str(e)}")
            return {
                'response': "Desculpe, ocorreu um erro interno. Tente novamente em alguns instantes.",
                'session_id': session_id or "unknown",
                'filtered_candidates': None,
                'total_candidates': None,
                'intent': 'unknown',
                'confidence': 0.0
            }
    
    def get_session_history(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retorna o histórico de uma sessão específica
        """
        try:
            session = self.orchestrator.get_session(session_id)
            if not session:
                return None
            
            return {
                'session_id': session.id,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat(),
                'context': {
                    'workbook_id': session.context.workbook_id,
                    'vaga_id': session.context.vaga_id,
                    'filter_history_id': session.context.filter_history_id
                },
                'messages': [
                    {
                        'id': msg.id,
                        'content': msg.content,
                        'sender': msg.sender,
                        'timestamp': msg.timestamp.isoformat(),
                        'metadata': msg.metadata
                    }
                    for msg in session.messages
                ]
            }
            
        except Exception as e:
            log_error(f"Error getting session history: {str(e)}")
            return None
    
    def clear_session(self, session_id: str) -> bool:
        """
        Remove uma sessão do cache
        """
        try:
            return self.orchestrator.clear_session(session_id)
        except Exception as e:
            log_error(f"Error clearing session: {str(e)}")
            return False
