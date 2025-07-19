from typing import Dict, Any, Optional

from app.chat.handlers.base_handler import BaseChatHandler
from app.chat.models.chat_session import ChatSession
from app.llm.factory import get_llm_client
from app.models.processed_applicant import ProcessedApplicant
from app.core.logging import log_info, log_error


class CandidateQuestionHandler(BaseChatHandler):
    """Handler para perguntas sobre candidatos específicos"""
    
    def __init__(self, db):
        super().__init__(db)
        self.llm_client = get_llm_client()
    
    def handle(self, parameters: Dict[str, Any], session: ChatSession) -> Dict[str, Any]:
        """
        Responde perguntas sobre candidatos específicos
        """
        try:
            candidate_id = parameters.get('candidate_id')
            question = parameters.get('question')
            
            if candidate_id:
                # Pergunta sobre candidato específico
                return self._handle_specific_candidate(candidate_id, question)
            else:
                # Pergunta genérica sobre candidatos
                return self._handle_generic_candidate_question(question)
                
        except Exception as e:
            log_error(f"Error in CandidateQuestionHandler: {str(e)}")
            return self._create_response(
                "Desculpe, ocorreu um erro ao buscar informações sobre candidatos."
            )
    
    def _handle_specific_candidate(self, candidate_id: str, question: str) -> Dict[str, Any]:
        """
        Responde sobre um candidato específico
        """
        try:
            # Busca o candidato
            candidate = self.db.query(ProcessedApplicant).filter(
                ProcessedApplicant.id == int(candidate_id)
            ).first()
            
            if not candidate:
                return self._create_response(
                    f"Candidato com ID {candidate_id} não encontrado."
                )
            
            # Prepara contexto do candidato
            context = self._build_candidate_context(candidate)
            
            # Gera resposta usando LLM
            prompt = f"""
Você é um assistente especializado em recrutamento. Responda à pergunta do usuário sobre o candidato usando apenas as informações fornecidas.

INFORMAÇÕES DO CANDIDATO:
{context}

PERGUNTA DO USUÁRIO: {question}

Responda de forma clara e objetiva, focando apenas nas informações disponíveis sobre o candidato.
"""
            
            response = self.llm_client.chat(prompt)
            return self._create_response(response)
            
        except ValueError:
            return self._create_response(
                "ID do candidato deve ser um número válido."
            )
        except Exception as e:
            log_error(f"Error handling specific candidate: {str(e)}")
            return self._create_response(
                "Erro ao buscar informações do candidato."
            )
    
    def _handle_generic_candidate_question(self, question: str) -> Dict[str, Any]:
        """
        Responde perguntas genéricas sobre candidatos
        """
        return self._create_response(
            """Para responder sobre um candidato específico, mencione o ID do candidato.

Exemplos:
• "Me fale sobre o candidato 123"
• "Qual a experiência do candidato ID 456?"
• "O candidato 789 tem as competências necessárias?"

Você também pode filtrar candidatos com critérios específicos:
• "Encontre 5 desenvolvedores Python"
• "Busque candidatos de São Paulo"
• "Mostre os melhores candidatos para esta vaga"
"""
        )
    
    def _build_candidate_context(self, candidate: ProcessedApplicant) -> str:
        """
        Constrói contexto formatado do candidato para o LLM
        """
        context_parts = [f"**CANDIDATO ID:** {candidate.id}"]
        
        if candidate.nome:
            context_parts.append(f"**NOME:** {candidate.nome}")
        
        if candidate.email:
            context_parts.append(f"**EMAIL:** {candidate.email}")
        
        if candidate.telefone:
            context_parts.append(f"**TELEFONE:** {candidate.telefone}")
        
        if candidate.cidade:
            context_parts.append(f"**CIDADE:** {candidate.cidade}")
        
        if candidate.estado:
            context_parts.append(f"**ESTADO:** {candidate.estado}")
        
        if candidate.nivel_escolaridade:
            context_parts.append(f"**ESCOLARIDADE:** {candidate.nivel_escolaridade}")
        
        if candidate.area_formacao:
            context_parts.append(f"**ÁREA DE FORMAÇÃO:** {candidate.area_formacao}")
        
        if candidate.experiencia_anos:
            context_parts.append(f"**ANOS DE EXPERIÊNCIA:** {candidate.experiencia_anos}")
        
        if candidate.area_experiencia:
            context_parts.append(f"**ÁREA DE EXPERIÊNCIA:** {candidate.area_experiencia}")
        
        if candidate.habilidades_tecnicas:
            context_parts.append(f"**HABILIDADES TÉCNICAS:** {candidate.habilidades_tecnicas}")
        
        if candidate.habilidades_comportamentais:
            context_parts.append(f"**HABILIDADES COMPORTAMENTAIS:** {candidate.habilidades_comportamentais}")
        
        if candidate.ultimo_cargo:
            context_parts.append(f"**ÚLTIMO CARGO:** {candidate.ultimo_cargo}")
        
        if candidate.ultima_empresa:
            context_parts.append(f"**ÚLTIMA EMPRESA:** {candidate.ultima_empresa}")
        
        if candidate.pretensao_salarial:
            context_parts.append(f"**PRETENSÃO SALARIAL:** {candidate.pretensao_salarial}")
        
        if candidate.disponibilidade:
            context_parts.append(f"**DISPONIBILIDADE:** {candidate.disponibilidade}")
        
        if candidate.observacoes:
            context_parts.append(f"**OBSERVAÇÕES:** {candidate.observacoes}")
        
        return "\n".join(context_parts)
