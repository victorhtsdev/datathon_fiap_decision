from typing import Dict, Any, List

from app.chat.handlers.base_handler import BaseChatHandler
from app.chat.models.chat_session import ChatSession
from app.services.candidate_filter_llm_handler import CandidateFilterLLMHandler
from app.services.llm_service import LLMService
from app.repositories.in_memory_candidate_repository import InMemoryCandidateRepository
from app.core.logging import log_info, log_error


class FilterHandler(BaseChatHandler):
    """Handler para filtros e gerenciamento de candidatos"""
    
    def __init__(self, db):
        super().__init__(db)
        llm_service = LLMService()
        self.filter_llm_handler = CandidateFilterLLMHandler(llm_service, db)
        self.candidate_repo = InMemoryCandidateRepository(db)
    
    async def handle(self, parameters: Dict[str, Any], session: ChatSession) -> Dict[str, Any]:
        """
        Método handle principal - dispatcher para diferentes tipos de filtro
        """
        # Por padrão, assume que é uma solicitação de filtro
        return await self.handle_filter(parameters, session)
    
    async def handle_filter(self, parameters: Dict[str, Any], session: ChatSession) -> Dict[str, Any]:
        """
        Processa solicitação de filtro de candidatos
        """
        try:
            workbook_id = parameters.get('workbook_id') or session.context.workbook_id
            message = parameters.get('message')
            
            if not workbook_id:
                return self._create_response(
                    "Para filtrar candidatos, preciso do contexto do workbook."
                )
            
            # Buscar todos os candidatos se não estão na sessão
            all_candidates = self.candidate_repo.get_session_candidates(session.id)
            if not all_candidates:
                # Buscar candidatos do banco de dados
                query = """
                    SELECT 
                        id, 
                        nome, 
                        email, 
                        endereco, 
                        nivel_maximo_formacao, 
                        cv_texto_semantico
                    FROM processed_applicants 
                    WHERE cv_texto_semantico IS NOT NULL
                    ORDER BY id
                """
                all_candidates = self.candidate_repo.execute_candidate_query(query, {})
                self.candidate_repo.save_session_candidates(session.id, all_candidates, mode='replace')
            
            # Processar filtro usando o handler LLM
            result = await self.filter_llm_handler.process_filter_request(
                session_id=session.id,
                message=message,
                job_id=workbook_id,
                all_candidates=all_candidates
            )
            
            if result.get('status') == 'success':
                return {
                    'response': result.get('message', ''),
                    'filtered_candidates': self.candidate_repo.get_session_candidates(session.id),
                    'total_candidates': result.get('filtered_count', 0)
                }
            else:
                return self._create_response(result.get('message', 'Erro ao processar filtro'))
            
        except Exception as e:
            log_error(f"Error in FilterHandler.handle_filter: {str(e)}")
            return self._create_response(
                "Desculpe, ocorreu um erro ao filtrar candidatos."
            )
    
    def handle_reset(self, parameters: Dict[str, Any], session: ChatSession) -> Dict[str, Any]:
        """
        Processa solicitação de reset de filtros
        """
        try:
            # Limpa candidatos da sessão
            self.candidate_repo.clear_session_candidates(session.id)
            
            # Limpa contexto da sessão
            session.update_context(filter_history_id=None)
            
            return self._create_response(
                """[OK] **Filtros resetados com sucesso!**

Todos os filtros anteriores foram removidos. Agora você pode fazer uma nova busca de candidatos.

Exemplo: "Encontre 10 desenvolvedores Python de São Paulo"
"""
            )
                
        except Exception as e:
            log_error(f"Error in FilterHandler.handle_reset: {str(e)}")
            return self._create_response(
                "Desculpe, ocorreu um erro ao resetar filtros."
            )
    
    def handle_history(self, parameters: Dict[str, Any], session: ChatSession) -> Dict[str, Any]:
        """
        Mostra histórico de filtros aplicados (versão simplificada)
        """
        try:
            # Mostra informações básicas da sessão
            candidates = self.candidate_repo.get_session_candidates(session.id)
            
            if not candidates:
                return self._create_response(
                    """📋 **Histórico de Filtros**

Nenhum filtro ativo no momento.

Para aplicar filtros, digite algo como:
• "Encontre 5 desenvolvedores Python"
• "Busque candidatos de São Paulo com experiência em React"
"""
                )
            
            return self._create_response(
                f"""📋 **Estado Atual da Sessão**

Você tem {len(candidates)} candidatos filtrados na sessão atual.

Para aplicar novos filtros:
• "Filtre por Python" (refinará os {len(candidates)} candidatos atuais)

Para resetar e começar nova busca:
• "resetar filtros"
"""
            )
            
        except Exception as e:
            log_error(f"Error in FilterHandler.handle_history: {str(e)}")
            return self._create_response(
                "Desculpe, ocorreu um erro ao buscar o histórico de filtros."
            )

