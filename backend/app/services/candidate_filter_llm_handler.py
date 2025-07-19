from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.llm.factory import get_llm_client
from app.core.logging import log_info, log_error
from app.repositories.in_memory_candidate_repository import InMemoryCandidateRepository
import json
import re

class CandidateFilterLLMHandler:
    """
    Handler para filtrar candidatos usando LLM para interpretar critérios
    em linguagem natural e converter para consultas SQL compatíveis.
    Mantém contexto de memória na sessão de chat.
    """
    
    def __init__(self, llm_service, db: Session):
        self.db = db
        self.llm_client = get_llm_client()
        self.candidate_repo = InMemoryCandidateRepository(db)
        self.llm_service = llm_service
    
    def handle(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa consulta de candidatos:
        1. LLM identifica intenção e extrai critérios específicos
        2. Monta consulta SQL compatível com o banco 
        3. Executa busca com similaridade semântica + filtros
        4. Mantém contexto de memória na sessão
        """
        try:
            workbook_id = parameters.get('workbook_id')
            session_id = parameters.get('session_id')
            count = parameters.get('count', 20)  # Default para 20 mais relevantes
            filter_criteria = parameters.get('filter_criteria') or parameters.get('message')
            
            log_info(f"LLM Filter Handler - criteria: {filter_criteria}, session: {session_id}")
            
            if not workbook_id or not filter_criteria:
                return {
                    'response': "Preciso do contexto do workbook e critérios de filtro.",
                    'candidates': [],
                    'total_found': 0
                }
            
            # ETAPA 1: LLM IDENTIFICA INTENÇÃO E EXTRAI CRITÉRIOS
            log_info("ETAPA 1: LLM analisando intenção e extraindo critérios")
            extracted_criteria = self._extract_intent_and_criteria(filter_criteria)
            log_info(f"LLM extraiu: {extracted_criteria}")
            
            # ETAPA 2: MONTA E EXECUTA CONSULTA SQL COM CONTEXTO DE SESSÃO
            log_info("ETAPA 2: Montando e executando consulta SQL")
            sql_candidates = self._execute_sql_query_with_session(
                workbook_id=workbook_id,
                session_id=session_id,
                criteria=extracted_criteria,
                limit=count
            )
            
            if not sql_candidates:
                return {
                    'response': f"Não encontrei candidatos que atendam aos critérios: '{filter_criteria}'",
                    'candidates': [],
                    'total_found': 0
                }
            
            log_info(f"Consulta SQL retornou {len(sql_candidates)} candidatos")
            
            # ETAPA 3: SALVA CANDIDATOS COMO PROSPECTS E NA SESSÃO
            if sql_candidates:
                self._save_filtered_candidates(workbook_id, sql_candidates)
                # Salva na sessão para manter contexto
                self.candidate_repo.save_session_candidates(session_id, sql_candidates, mode='replace')
            
            # ETAPA 4: GERA RESPOSTA FINAL
            response = self._generate_response_with_llm(
                candidates=sql_candidates,
                original_criteria=filter_criteria,
                extracted_criteria=extracted_criteria
            )
            
            return {
                'response': response,
                'candidates': sql_candidates,
                'total_found': len(sql_candidates)
            }
            
        except Exception as e:
            log_error(f"Erro no LLM Filter Handler: {str(e)}")
            return {
                'response': "Desculpe, ocorreu um erro ao filtrar candidatos.",
                'candidates': [],
                'total_found': 0
            }
    
    async def process_filter_request(self, session_id: str, message: str, job_id: int, all_candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Processa uma solicitação de filtro de candidatos para uma sessão específica.
        Novo método que usa o motor SQL semântico com contexto de memória.
        """
        try:
            log_info(f"Iniciando processo de filtro para sessao {session_id}, job_id {job_id}")
            
            # Verifica se há candidatos na sessão (contexto de memória)
            session_candidates = self.candidate_repo.get_session_candidates(session_id)
            use_session_context = bool(session_candidates)
            
            if use_session_context:
                log_info(f"Usando contexto de memória: {len(session_candidates)} candidatos na sessão")
                # Aplica filtro refinado aos candidatos já filtrados
                result = await self._apply_refinement_filter(session_id, message, session_candidates)
            else:
                log_info("Primeira busca - usando busca semântica completa")
                # Primeira busca: usa motor SQL semântico completo
                result = self.handle({
                    'workbook_id': str(job_id),
                    'session_id': session_id,
                    'filter_criteria': message,
                    'count': 50  # Primeira busca retorna mais candidatos
                })
                
                if result.get('total_found', 0) > 0:
                    return {
                        'status': 'success',
                        'message': result.get('response', ''),
                        'filtered_count': result.get('total_found', 0),
                        'session_id': session_id
                    }
                else:
                    return {
                        'status': 'error',
                        'message': result.get('response', 'Nenhum candidato encontrado'),
                        'session_id': session_id
                    }
            
            return result
            
        except Exception as e:
            log_error(f"Erro ao processar filtro para sessao {session_id}: {str(e)}")
            return {
                'status': 'error',
                'message': f"Erro ao processar filtro: {str(e)}",
                'session_id': session_id
            }
    
    async def _apply_refinement_filter(self, session_id: str, message: str, session_candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aplica filtro de refinamento aos candidatos já presentes na sessão
        """
        try:
            # Criar prompt para o LLM
            prompt = self._create_filter_prompt(message, session_candidates)
            
            # Processar com LLM
            llm_response = await self.llm_service.process_with_llm(prompt)
            
            # Extrair IDs dos candidatos filtrados
            filtered_ids = self._extract_candidate_ids(llm_response)
            
            # Filtrar candidatos baseado nos IDs
            filtered_candidates = [
                candidate for candidate in session_candidates 
                if candidate.get("id") in filtered_ids
            ]
            
            # Atualizar candidatos na sessão
            self.candidate_repo.save_session_candidates(session_id, filtered_candidates, mode='replace')
            
            # Formatar resposta
            response = await self.response_formatter.format_filter_response(
                filtered_candidates, 
                message, 
                len(session_candidates)
            )
            
            log_info(f"Filtro aplicado: {len(session_candidates)} -> {len(filtered_candidates)} candidatos para sessao {session_id}")
            
            return {
                "status": "success",
                "message": response,
                "filtered_count": len(filtered_candidates),
                "total_before_filter": len(session_candidates),
                "session_id": session_id
            }
            
        except Exception as e:
            log_error(f"Erro ao processar filtro para sessao {session_id}: {str(e)}")
            return {
                "status": "error",
                "message": f"Erro ao processar filtro: {str(e)}",
                "session_id": session_id
            }
    
    def _create_filter_prompt(self, filter_message: str, candidates: List[Dict[str, Any]]) -> str:
        """
        Cria o prompt para o LLM processar o filtro de candidatos.
        """
        candidates_json = []
        for candidate in candidates:
            candidate_data = {
                "id": candidate.get("id"),
                "name": candidate.get("nome") or candidate.get("name"),
                "skills": candidate.get("skills", []),
                "experience": candidate.get("experience", ""),
                "education": candidate.get("nivel_maximo_formacao") or candidate.get("education", ""),
                "location": candidate.get("endereco") or candidate.get("location", ""),
                "summary": candidate.get("cv_texto_semantico") or candidate.get("summary", "")
            }
            candidates_json.append(candidate_data)
        
        prompt = f"""
        Você é um assistente especializado em filtrar candidatos baseado em critérios específicos.
        
        SOLICITAÇÃO DO USUÁRIO: {filter_message}
        
        CANDIDATOS DISPONÍVEIS:
        {json.dumps(candidates_json, ensure_ascii=False, indent=2)}
        
        INSTRUÇÕES:
        1. Analise a solicitação do usuário e identifique os critérios de filtro
        2. Aplique esses critérios aos candidatos fornecidos
        3. Retorne APENAS uma lista com os IDs dos candidatos que atendem aos critérios
        4. O formato de resposta deve ser: [1, 2, 3, ...]
        
        RESPOSTA (apenas IDs):
        """
        
        return prompt
    
    def _extract_candidate_ids(self, llm_response: str) -> List[int]:
        """
        Extrai os IDs dos candidatos da resposta do LLM.
        """
        try:
            # Tentar extrair lista de IDs da resposta
            import re
            
            # Procurar por padrões de lista: [1, 2, 3] ou 1, 2, 3
            pattern = r'\[([0-9,\s]+)\]|(?:^|\n)([0-9,\s]+)(?:\n|$)'
            match = re.search(pattern, llm_response)
            
            if match:
                ids_str = match.group(1) or match.group(2)
                ids = [int(id_str.strip()) for id_str in ids_str.split(',') if id_str.strip().isdigit()]
                return ids
            
            # Fallback: tentar parsear como JSON
            try:
                ids = json.loads(llm_response.strip())
                if isinstance(ids, list):
                    return [int(id) for id in ids if isinstance(id, (int, str)) and str(id).isdigit()]
            except:
                pass
            
            log_error(f"Não foi possível extrair IDs da resposta do LLM: {llm_response}")
            return []
            
        except Exception as e:
            log_error(f"Erro ao extrair IDs dos candidatos: {str(e)}")
            return []
    
    def get_session_candidates(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Obtém os candidatos filtrados da sessão.
        """
        return self.candidate_repo.get_session_candidates(session_id)
    
    def reset_session_filters(self, session_id: str, all_candidates: List[Dict[str, Any]]) -> None:
        """
        Reseta os filtros da sessão, retornando todos os candidatos.
        """
        log_info(f"Resetando filtros para sessao {session_id}")
        self.candidate_repo.save_session_candidates(session_id, all_candidates, mode='replace')
    
    def clear_session(self, session_id: str) -> None:
        """
        Limpa completamente os dados da sessão.
        """
        log_info(f"Limpando sessao {session_id}")
        self.candidate_repo.clear_session_candidates(session_id)
    
    def _extract_intent_and_criteria(self, filter_criteria: str) -> Dict[str, Any]:
        """
        Método temporário para compatibilidade. 
        Extrai critérios básicos até migração completa para novo handler.
        """
        try:
            # Método simplificado que retorna critérios básicos
            criteria = {
                "usar_similaridade": True,
                "filtros": {}
            }
            
            # Detecta número de candidatos
            import re
            numbers = re.findall(r'\d+', filter_criteria)
            if numbers:
                criteria["count"] = int(numbers[0])
            
            log_info(f"Critérios básicos extraídos: {criteria}")
            return criteria
            
        except Exception as e:
            log_error(f"Erro ao extrair critérios básicos: {str(e)}")
            return {"usar_similaridade": True, "filtros": {}}
