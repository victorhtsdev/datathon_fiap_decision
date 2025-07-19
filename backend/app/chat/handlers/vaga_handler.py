from typing import Dict, Any, Optional
import uuid

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
        """
        try:
            workbook_id = parameters.get('workbook_id') or session.context.workbook_id
            question = parameters.get('question')
            
            if not workbook_id:
                return self._create_response(
                    "Para responder sobre a vaga, preciso do contexto do workbook."
                )
            
            # Busca dados da vaga através do workbook
            vaga_data = self._get_vaga_context(workbook_id)
            if not vaga_data:
                return self._create_response(
                    "Não consegui encontrar informações da vaga para este workbook."
                )
            
            # Prepara contexto para o LLM
            context = self._build_vaga_context(vaga_data)
            
            # Gera resposta usando LLM
            prompt = f"""
Você é um assistente especializado em recrutamento. Responda à pergunta do usuário sobre a vaga usando apenas as informações fornecidas.

INFORMAÇÕES DA VAGA:
{context}

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
