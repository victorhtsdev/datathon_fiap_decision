from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.chat.models.chat_session import ChatSession, ChatContext
from app.chat.services.intent_classifier import IntentClassifier, ChatIntent
from app.chat.handlers.vaga_handler import VagaQuestionHandler
from app.chat.handlers.candidate_handler import CandidateQuestionHandler
from app.chat.handlers.filter_handler import FilterHandler
from app.chat.handlers.generic_handler import GenericConversationHandler
from app.chat.handlers.candidate_semantic_filter_handler import CandidateSemanticFilterHandler
from app.core.logging import log_info, log_error


class ChatOrchestrator:
    """
    Orquestra as conversas do chat, direcionando para os handlers apropriados
    Implementa padrão Singleton para manter sessões entre requisições
    """
    
    _instance = None
    _lock = None
    
    def __new__(cls, db: Session):
        if cls._instance is None:
            import threading
            if cls._lock is None:
                cls._lock = threading.Lock()
            
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, db: Session):
        # Evita re-inicialização do singleton
        if self._initialized:
            return
            
        self.db = db
        self.intent_classifier = IntentClassifier()
        
        # Inicializa handlers
        self.vaga_handler = VagaQuestionHandler(db)
        self.candidate_handler = CandidateQuestionHandler(db)
        self.filter_handler = FilterHandler(db)
        self.semantic_filter_handler = CandidateSemanticFilterHandler(db)  # Novo handler semântico
        self.generic_handler = GenericConversationHandler()
        
        # Cache de sessões ativas (em produção, usar Redis ou similar)
        self._active_sessions: Dict[str, ChatSession] = {}
        
        self._initialized = True
    
    async def process_message(
        self, 
        message: str, 
        session_id: Optional[str] = None,
        workbook_id: Optional[str] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processa uma mensagem do usuário
        
        Returns:
            Dict contendo:
            - response: str - resposta do assistente
            - session_id: str - ID da sessão
            - filtered_candidates: List[Dict] | None
            - total_candidates: int | None
            - intent: str - intenção classificada
            - confidence: float - confiança da classificação
        """
        try:
            log_info(f"Processing message: {message[:100]}...")
            
            # Obtém ou cria sessão
            session = self._get_or_create_session(session_id, workbook_id)
            
            # Adiciona mensagem do usuário
            session.add_message(message, sender="user")
            
            # Classifica intenção
            intent_result = self.intent_classifier.classify(message, workbook_id)
            
            log_info(f"Classified intent: {intent_result.intent.value} (confidence: {intent_result.confidence:.2f})")
            
            # Direciona para o handler apropriado
            response_data = await self._route_to_handler(intent_result, session)
            
            # Adiciona resposta do assistente à sessão
            filtered_candidates = response_data.get('filtered_candidates') or []
            session.add_message(
                response_data['response'], 
                sender="assistant",
                metadata={
                    'intent': intent_result.intent.value,
                    'confidence': intent_result.confidence,
                    'filtered_candidates_count': len(filtered_candidates)
                }
            )
            
            # Atualiza cache da sessão
            self._active_sessions[session.id] = session
            
            return {
                **response_data,
                'session_id': session.id,
                'intent': intent_result.intent.value,
                'confidence': intent_result.confidence
            }
            
        except Exception as e:
            log_error(f"Error processing message: {str(e)}")
            return {
                'response': "Desculpe, ocorreu um erro interno. Tente novamente em alguns instantes.",
                'session_id': session_id or "unknown",
                'filtered_candidates': None,
                'total_candidates': None,
                'intent': ChatIntent.UNKNOWN.value,
                'confidence': 0.0
            }
    
    def _get_or_create_session(self, session_id: Optional[str], workbook_id: Optional[str]) -> ChatSession:
        """Obtém sessão existente ou cria nova"""
        log_info(f"Session management - session_id: {session_id}, existing sessions: {list(self._active_sessions.keys())}")
        
        if session_id and session_id in self._active_sessions:
            session = self._active_sessions[session_id]
            log_info(f"Using existing session: {session_id} (workbook: {session.context.workbook_id})")
            # Atualiza contexto se workbook_id foi fornecido
            if workbook_id and workbook_id != session.context.workbook_id:
                log_info(f"Updating workbook context from {session.context.workbook_id} to {workbook_id}")
                session.update_context(workbook_id=workbook_id)
            return session
        
        # Cria nova sessão
        context = ChatContext(workbook_id=workbook_id)
        session = ChatSession(context=context)
        self._active_sessions[session.id] = session
        log_info(f"Created new session: {session.id} (workbook: {workbook_id})")
        
        return session
    
    async def _route_to_handler(self, intent_result, session: ChatSession) -> Dict[str, Any]:
        """Direciona para o handler apropriado baseado na intenção"""
        
        if intent_result.intent == ChatIntent.VAGA_QUESTION:
            return self.vaga_handler.handle(intent_result.parameters, session)
        
        elif intent_result.intent == ChatIntent.CANDIDATE_QUESTION:
            return self.candidate_handler.handle(intent_result.parameters, session)
        
        elif intent_result.intent == ChatIntent.CANDIDATE_FILTER:
            return await self.filter_handler.handle_filter(intent_result.parameters, session)
        
        elif intent_result.intent == ChatIntent.SEMANTIC_CANDIDATE_FILTER:
            return self.semantic_filter_handler.handle(intent_result.parameters, session)
        
        elif intent_result.intent == ChatIntent.FILTER_RESET:
            return self.filter_handler.handle_reset(intent_result.parameters, session)
        
        elif intent_result.intent == ChatIntent.FILTER_HISTORY:
            return self.filter_handler.handle_history(intent_result.parameters, session)
        
        elif intent_result.intent == ChatIntent.GENERIC_CONVERSATION:
            return self.generic_handler.handle(intent_result.parameters, session)
        
        else:
            # Fallback para intent desconhecida
            return {
                'response': self._generate_help_message(),
                'filtered_candidates': None,
                'total_candidates': None
            }
    
    def _generate_help_message(self) -> str:
        """Gera mensagem de ajuda quando a intenção não é reconhecida"""
        return """Não entendi bem sua solicitação.

Como assistente de **recrutamento**, posso ajudá-lo com:

• **Filtrar candidatos** com critérios específicos
  Ex: "encontre 10 desenvolvedores Python"
  
• **Analisar perfis** de candidatos individuais
  Ex: "me conte sobre o candidato ID 456"
  
• **Consultar informações** sobre a vaga atual
  Ex: "quais os requisitos técnicos?"

• **Gerenciar filtros**
  Ex: "resetar filtros", "histórico de filtros"

Tente uma dessas opções! 🚀"""
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Retorna uma sessão específica"""
        return self._active_sessions.get(session_id)
    
    def clear_session(self, session_id: str) -> bool:
        """Remove uma sessão do cache"""
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]
            return True
        return False
