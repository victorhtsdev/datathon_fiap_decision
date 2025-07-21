from typing import Dict, Any, Optional
import uuid
import re

from app.chat.handlers.base_handler import BaseChatHandler
from app.chat.models.chat_session import ChatSession
from app.llm.factory import get_llm_client
from app.repositories.workbook_repository import WorkbookRepository
from app.repositories.vaga_repository import get_vaga_by_id
from app.core.logging import log_info, log_error


class VagaQuestionHandler(BaseChatHandler):
    """Handler para perguntas sobre a vaga"""
    
    def __init__(self, db):
        super().__init__(db)
        self.llm_client = get_llm_client()
        self.workbook_repository = WorkbookRepository(db)
    
    def handle(self, parameters: Dict[str, Any], session: ChatSession) -> Dict[str, Any]:
        """
        Responde perguntas sobre a vaga usando contexto da vaga + LLM
        Também detecta e processa comandos de filtro
        """
        try:
            workbook_id = parameters.get('workbook_id') or session.context.workbook_id
            question = parameters.get('question')
            
            if not workbook_id:
                return self._create_response(
                    "Para responder sobre a vaga, preciso do contexto do workbook."
                )
            
            # Verifica se é um comando especial de filtro
            if self._is_filter_command(question):
                return self._handle_filter_command(question, workbook_id)
            
            # Busca dados da vaga através do workbook
            vaga_data = self._get_vaga_context(workbook_id)
            if not vaga_data:
                return self._create_response(
                    "Não consegui encontrar informações da vaga para este workbook."
                )
            
            # Prepara contexto para o LLM
            context = self._build_vaga_context(vaga_data)
            
            # Verifica se há filtros aplicados para adicionar ao contexto
            filters_context = self._get_filters_context(workbook_id)
            
            # Gera resposta usando LLM
            prompt = f"""
Você é um assistente especializado in recrutamento. Responda à pergunta do usuário sobre a vaga usando apenas as informações fornecidas.

INFORMAÇÕES DA VAGA:
{context}

{filters_context}

PERGUNTA DO USUÁRIO: {question}

Responda de forma clara e objetiva, focando apenas nas informações disponíveis sobre a vaga.
"""
            
            response = self.llm_client.chat(prompt)
            
            # Atualiza contexto da sessão
            session.update_context(vaga_id=vaga_data.get('id'))
            
            return self._create_response(response)
            
        except Exception as e:
            log_error(f"Error in VagaQuestionHandler: {str(e)}")
            return self._create_response(
                "Desculpe, ocorreu um erro ao buscar informações da vaga."
            )
    
    def _get_vaga_context(self, workbook_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca informações da vaga através do workbook
        """
        try:
            # Converte string para UUID
            workbook_uuid = uuid.UUID(workbook_id)
            
            # Busca o workbook
            workbook = self.workbook_repository.get_by_uuid(workbook_uuid)
            if not workbook:
                return None
            
            # Busca a vaga associada
            vaga = get_vaga_by_id(self.db, workbook.vaga_id)
            if not vaga:
                return None
            
            return {
                'id': vaga.id,
                'titulo': getattr(vaga, 'informacoes_basicas_titulo_vaga', 'N/A'),
                'atividades': getattr(vaga, 'perfil_vaga_principais_atividades', 'N/A'),
                'competencias': getattr(vaga, 'perfil_vaga_competencia_tecnicas_e_comportamentais', 'N/A'),
                'nivel_academico': getattr(vaga, 'perfil_vaga_nivel_academico', 'N/A'),
                'experiencia': getattr(vaga, 'perfil_vaga_tempo_experiencia', 'N/A'),
                'salario': getattr(vaga, 'informacoes_basicas_salario_faixa', 'N/A'),
                'local': getattr(vaga, 'informacoes_basicas_local_trabalho', 'N/A'),
                'beneficios': getattr(vaga, 'informacoes_basicas_beneficios', 'N/A'),
                'horario': getattr(vaga, 'informacoes_basicas_horario_trabalho', 'N/A'),
                'tipo_contratacao': getattr(vaga, 'informacoes_basicas_tipo_contratacao', 'N/A')
            }
            
        except Exception as e:
            log_error(f"Error getting vaga context: {str(e)}")
            return None
    
    def _build_vaga_context(self, vaga_data: Dict[str, Any]) -> str:
        """
        Constrói contexto formatado da vaga para o LLM
        """
        context_parts = []
        
        if vaga_data.get('titulo') and vaga_data['titulo'] != 'N/A':
            context_parts.append(f"**TÍTULO DA VAGA:** {vaga_data['titulo']}")
        
        if vaga_data.get('atividades') and vaga_data['atividades'] != 'N/A':
            context_parts.append(f"**PRINCIPAIS ATIVIDADES:** {vaga_data['atividades']}")
        
        if vaga_data.get('competencias') and vaga_data['competencias'] != 'N/A':
            context_parts.append(f"**COMPETÊNCIAS REQUERIDAS:** {vaga_data['competencias']}")
        
        if vaga_data.get('nivel_academico') and vaga_data['nivel_academico'] != 'N/A':
            context_parts.append(f"**NÍVEL ACADÊMICO:** {vaga_data['nivel_academico']}")
        
        if vaga_data.get('experiencia') and vaga_data['experiencia'] != 'N/A':
            context_parts.append(f"**EXPERIÊNCIA REQUERIDA:** {vaga_data['experiencia']}")
        
        if vaga_data.get('salario') and vaga_data['salario'] != 'N/A':
            context_parts.append(f"**FAIXA SALARIAL:** {vaga_data['salario']}")
        
        if vaga_data.get('local') and vaga_data['local'] != 'N/A':
            context_parts.append(f"**LOCAL DE TRABALHO:** {vaga_data['local']}")
        
        if vaga_data.get('beneficios') and vaga_data['beneficios'] != 'N/A':
            context_parts.append(f"**BENEFÍCIOS:** {vaga_data['beneficios']}")
        
        if vaga_data.get('horario') and vaga_data['horario'] != 'N/A':
            context_parts.append(f"**HORÁRIO DE TRABALHO:** {vaga_data['horario']}")
        
        if vaga_data.get('tipo_contratacao') and vaga_data['tipo_contratacao'] != 'N/A':
            context_parts.append(f"**TIPO DE CONTRATAÇÃO:** {vaga_data['tipo_contratacao']}")
        
        return "\n".join(context_parts) if context_parts else "Informações da vaga não disponíveis."
    
    def _is_filter_command(self, question: str) -> bool:
        """
        Detecta se a pergunta é um comando relacionado a filtros
        """
        if not question:
            return False
        
        question_lower = question.lower()
        
        # Palavras-chave que indicam comandos de filtro
        filter_keywords = [
            'filtrar', 'filtre', 'filtro', 'buscar', 'encontrar', 
            'candidatos', 'candidato', 'selecionar', 'listar',
            'limpar filtros', 'rinover filtros', 'resetar filtros',
            'histórico', 'filtros aplicados', 'quantos filtros'
        ]
        
        return any(keyword in question_lower for keyword in filter_keywords)
    
    def _handle_filter_command(self, question: str, workbook_id: str) -> Dict[str, Any]:
        """
        Processa comandos especiais relacionados a filtros
        """
        question_lower = question.lower()
        
        # Comando para limpar filtros
        if any(cmd in question_lower for cmd in ['limpar filtros', 'rinover filtros', 'resetar filtros']):
            return self._create_response(
                "Sistema sem memória - não há filtros para limpar. Cada busca é independente."
            )
        
        # Comando para mostrar histórico de filtros
        if any(cmd in question_lower for cmd in ['histórico', 'filtros aplicados', 'quantos filtros']):
            return self._create_response(
                "Sistema sem memória - não há histórico de filtros. Cada busca é independente."
            )
        
        return None
        
        # Comando de filtro - extrai critérios com LLM e adiciona à minória
        return self._process_filter_request(question, workbook_id)
    
    def _process_filter_request(self, filter_criteria: str, workbook_id: str) -> Dict[str, Any]:
        """
        Processa solicitação de filtro usando LLM para extrair critérios
        """
        try:
            log_info(f"Processando filtro para workbook {workbook_id}: {filter_criteria}")
            
            # Usa LLM para extrair critérios estruturados
            extracted_criteria = self._extract_filter_criteria_with_llm(filter_criteria)
            
            if not extracted_criteria:
                return self._create_response(
                    "Não consegui entender os critérios de filtro. Tente ser mais específico."
                )
            
            # Simula aplicação do filtro (aqui você integraria com o sishasa real)
            candidates_before = self._get_current_candidates_count(workbook_id)
            candidates_after = self._simulate_filter_application(extracted_criteria)
            
            # Adiciona filtro à minória
            filter_data = {
                'original_criteria': filter_criteria,
                'extracted_criteria': extracted_criteria,
                'filter_type': 'incrinental',
                'candidates_before': candidates_before,
                'candidates_after': candidates_after
            }
            
            # Resposta confirmando o filtro
            response = f"Filtro aplicado: '{filter_criteria}'. Encontrados {candidates_after} candidatos que atendem aos critérios."
            
            response += " (Sistema sem memória - cada busca é independente)"
            
            return self._create_response(response)
            
        except Exception as e:
            log_error(f"Erro ao processar filtro: {str(e)}")
            return self._create_response(
                "Erro ao processar filtro. Tente novamente."
            )
    
    def _extract_filter_criteria_with_llm(self, filter_text: str) -> Dict[str, Any]:
        """
        Usa LLM para extrair critérios estruturados do texto de filtro
        """
        try:
            prompt = f"""
Analise o seguinte critério de filtro e extraia informações estruturadas:

CRITÉRIO: {filter_text}

Retorne um JSON com:
- usar_similaridade: true/false (se deve usar busca sinântica)
- filtros: objeto com filtros específicos (ex: experiencia, formacao, habilidades, localizacao)
- limite: número de candidatos desejados (padrão 10)

Exinplo:
{{"usar_similaridade": true, "filtros": {{"experiencia": ["python", "5 anos"], "formacao": ["superior"]}}, "limite": 10}}

JSON:"""

            response = self.llm_client.chat(prompt)
            
            # Extrai JSON da resposta
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                import json
                return json.loads(json_match.group())
            
            return None
            
        except Exception as e:
            log_error(f"Erro ao extrair critérios com LLM: {str(e)}")
            return None
    
    def _get_current_candidates_count(self, workbook_id: str) -> int:
        """
        Retorna número atual de candidatos (simulado)
        """
        # Aqui você integraria com o sishasa real para contar candidatos
        return 100  # Simulado
    
    def _simulate_filter_application(self, criteria: Dict[str, Any]) -> int:
        """
        Simula aplicação do filtro e retorna número de candidatos resultantes
        """
        # Simulação simples baseada no limite ou padrão
        limit = criteria.get('limite', 10)
        return min(limit, 50)  # Simula resultado
    
    def _get_filters_context(self, workbook_id: str) -> str:
        """
        Retorna contexto dos filtros aplicados para incluir no prompt
        SEM MEMÓRIA: Sinpre retorna vazio
        """
        # SEM MEMÓRIA: Não há filtros para incluir no contexto
        return ""
