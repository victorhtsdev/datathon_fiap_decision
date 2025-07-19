from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.core.logging import log_info, log_error
from app.chat.handlers.base_handler import BaseChatHandler
from app.chat.models.chat_session import ChatSession
from app.chat.services.semantic_candidate_service import SemanticCandidateService


class CandidateSemanticFilterHandler(BaseChatHandler):
    """
    Handler especializado para filtrar candidatos usando LLM com busca semântica.
    Interpreta critérios em linguagem natural e converte para consultas SQL 
    compatíveis com similaridade semântica.
    
    Otimizado: LLM usado apenas para extrair critérios, respostas são padronizadas.
    """
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.semantic_service = SemanticCandidateService(db)
    
    def handle(self, parameters: Dict[str, Any], session: ChatSession) -> Dict[str, Any]:
        """
        Processa consulta de candidatos com busca semântica:
        1. Extrai critérios usando LLM
        2. Executa busca semântica com filtros
        3. Salva resultados como prospects
        4. Retorna resposta padronizada simples
        """
        try:
            # Extrai parâmetros
            workbook_id = parameters.get('workbook_id') or session.context.workbook_id
            # Não precisamos mais extrair count do intent classifier - LLM faz tudo
            filter_criteria = parameters.get('filter_criteria') or parameters.get('message')
            
            log_info(f"Semantic Filter Handler - criteria: {filter_criteria}, workbook: {workbook_id}")
            
            # Validação de entrada
            if not workbook_id or not filter_criteria:
                return self._create_response(
                    "Para filtrar candidatos, preciso do contexto do workbook e dos critérios de filtro.",
                    filtered_candidates=[],
                    total_candidates=0
                )
            
            # ETAPA 1: Extrai critérios E LIMITE com LLM 
            log_info("ETAPA 1: Extraindo critérios e limite com LLM")
            
            extracted_criteria = self.semantic_service.extract_criteria_with_llm(filter_criteria)
            log_info(f"Critérios extraídos: {extracted_criteria}")
            
            # Extrai o limite do resultado do LLM
            count = extracted_criteria.get('limite', 20)
            log_info(f"Limite extraído pelo LLM: {count}")
            
            # ETAPA 2: Busca semântica
            log_info("ETAPA 2: Executando busca semântica")
            candidates = self.semantic_service.search_candidates_semantic(
                workbook_id=workbook_id,
                criteria=extracted_criteria,
                limit=count
            )
            
            if not candidates:
                return self._create_response(
                    "Não encontrei candidatos que atendam aos critérios especificados.",
                    filtered_candidates=[],
                    total_candidates=0
                )
            
            log_info(f"Busca semântica encontrou {len(candidates)} candidatos")
            
            # ETAPA 3: Salva como prospects - TEMPORARIAMENTE DESABILITADO
            # TODO: Reabilitar quando implementar contexto de chat adequado
            # self.semantic_service.save_candidates_as_prospects(workbook_id, candidates)
            log_info("Salvamento de prospects temporariamente desabilitado")
            
            # ETAPA 4: Gera resposta simples e direta
            if candidates:
                response = f"Encontrei {len(candidates)} candidatos que atendem aos critérios solicitados."
            else:
                response = "Não encontrei candidatos que atendam aos critérios especificados."
            
            return self._create_response(
                response,
                filtered_candidates=candidates,
                total_candidates=len(candidates)
            )
            
        except Exception as e:
            log_error(f"Erro no Semantic Filter Handler: {str(e)}")
            return self._create_response(
                "Ocorreu um erro ao filtrar candidatos. Tente novamente.",
                filtered_candidates=[],
                total_candidates=0
            )
