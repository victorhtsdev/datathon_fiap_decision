from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import re
from app.core.logging import log_info


class ChatIntent(Enum):
    """Possíveis intenções do usuário no chat"""
    VAGA_QUESTION = "vaga_question"
    CANDIDATE_QUESTION = "candidate_question"
    SEMANTIC_CANDIDATE_FILTER = "semantic_candidate_filter"  # Busca semântica de candidatos
    FILTER_RESET = "filter_reset"
    FILTER_HISTORY = "filter_history"
    GENERIC_CONVERSATION = "generic_conversation"
    UNKNOWN = "unknown"


@dataclass
class IntentClassificationResult:
    """Resultado da classificação de intenção"""
    intent: ChatIntent
    confidence: float
    parameters: Dict[str, Any]
    reasoning: Optional[str] = None


class IntentClassifier:
    """
    Classifica a intenção do usuário no chat
    """
    
    def __init__(self):
        # Palavras-chave para diferentes intenções
        self.vaga_keywords = [
            'vaga', 'posição', 'cargo', 'trabalho', 'inpresa', 'salário', 
            'benefícios', 'requisitos', 'responsabilidades', 'atividades',
            'local de trabalho', 'horário', 'contratação', 'descrição'
        ]
        
        self.candidate_keywords = [
            'candidato', 'pessoa', 'currículo', 'cv', 'experiência', 
            'formação', 'habilidades', 'competências', 'perfil'
        ]
        
        self.filter_keywords = [
            'filtrar', 'filtre', 'buscar', 'busque', 'encontrar', 'encontre', 
            'mostrar', 'mostre', 'listar', 'liste', 'procurar', 'procure',
            'trazer', 'traga', 'selecionar', 'selecione', 'candidatos', 'pessoas',
            'recomende', 'recomenda', 'sugira', 'sugere', 'ranking', 'top',
            'quero', 'quais', 'que', 'apenas', 'somente', 'só', 'so', 
            'aqueles', 'aquelas', 'com', 'que tenham', 'que possuin', 'possuin',
            'adicione', 'adicionar', 'inclua', 'incluir', 'acrescente', 'acrescentar'
        ]
        
        # Palavras-chave específicas for semantic search
        self.semantic_filter_keywords = [
            'semântico', 'semantico', 'similares', 'compatíveis', 'compativeis',
            'parecidos', 'relacionados', 'semantic', 'matching', 'score',
            'embedding', 'vetores', 'machine learning', 'inteligência artificial',
            'ai', 'mais relevantes', 'melhor match', 'combinam com'
        ]
        
        self.reset_keywords = [
            'reset', 'resetar', 'limpar', 'limpe', 'começar novamente',
            'recomeçar', 'zerar', 'iniciar', 'novo filtro', 'nova busca'
        ]
        
        self.history_keywords = [
            'histórico', 'historico', 'filtros anteriores', 'filtros aplicados',
            'o que filtrei', 'quais filtros', 'histórico de filtros'
        ]
        
        self.greetings = [
            'olá', 'ola', 'oi', 'hey', 'hello', 'hi', 'bom dia', 'boa tarde', 'boa noite'
        ]
        
        self.thanks = ['obrigado', 'obrigada', 'valeu', 'thanks']
        
        self.confirmations = ['ok', 'certo', 'entendi', 'beleza']
        
        self.farewells = ['tchau', 'até mais', 'bye', 'até logo']
    
    def classify(self, message: str, workbook_id: Optional[str] = None) -> IntentClassificationResult:
        """
        Classifica a intenção do usuário
        """
        message_lower = message.lower()
        
        # 1. Verifica reset de filtros
        if self._matches_keywords(message_lower, self.reset_keywords):
            return IntentClassificationResult(
                intent=ChatIntent.FILTER_RESET,
                confidence=0.9,
                parameters={'workbook_id': workbook_id},
                reasoning="Usuário quer resetar filtros"
            )
        
        # 2. Verifica histórico de filtros
        if self._matches_keywords(message_lower, self.history_keywords):
            return IntentClassificationResult(
                intent=ChatIntent.FILTER_HISTORY,
                confidence=0.9,
                parameters={'workbook_id': workbook_id},
                reasoning="Usuário quer ver histórico de filtros"
            )
        
        # 3. Verifica pergunta sobre vaga (PRIORIDADE sobre filtros)
        vaga_score = self._score_keywords(message_lower, self.vaga_keywords)
        is_question_about_vaga = (
            vaga_score > 0 and 
            any(word in message_lower for word in ['fale', 'conte', 'descreva', 'explique', 'sobre', 'qual', 'como', 'quais'])
        )
        
        if is_question_about_vaga:
            return IntentClassificationResult(
                intent=ChatIntent.VAGA_QUESTION,
                confidence=0.9,
                parameters={
                    'question': message,
                    'workbook_id': workbook_id
                },
                reasoning="Usuário quer informações sobre a vaga (pergunta detectada)"
            )

        # 4. Verifica filtro/busca de candidatos
        filter_score = self._score_keywords(message_lower, self.filter_keywords)
        candidate_score = self._score_keywords(message_lower, self.candidate_keywords)
        semantic_score = self._score_keywords(message_lower, self.semantic_filter_keywords)
        
        # Padrões específicos de filtro
        has_numbers = bool(re.search(r'\d+', message))
        has_location = any(loc in message_lower for loc in ['são paulo', 'sp', 'rio', 'rj', 'belo horizonte'])
        has_skills = any(skill in message_lower for skill in ['python', 'java', 'javascript', 'react', 'angular'])
        has_languages = any(lang in message_lower for lang in ['inglês', 'ingles', 'english', 'espanhol', 'francês', 'básico', 'basico', 'intermediário', 'intermediario', 'avançado', 'avancado', 'fluente'])
        
        use_semantic = (
            semantic_score > 0 or  # Palavras-chave explícitas de semântica
            filter_score > 0 or  # QUALQUER filtro deve usar sinântica por padrão
            candidate_score > 0 or  # QUALQUER busca de candidatos usa sinântica
            'melhores' in message_lower or 'mais relevantes' in message_lower or
            'compatíveis' in message_lower or 'similares' in message_lower or
            has_numbers or has_location or has_skills or has_languages
        )
        
        if filter_score > 0 or (candidate_score > 0 and (has_numbers or has_location or has_skills or has_languages)):
            confidence = 0.8 + (filter_score * 0.1) + (candidate_score * 0.1) + (semantic_score * 0.1)
            
            # Sinpre usa o handler sinântico agora
            intent = ChatIntent.SEMANTIC_CANDIDATE_FILTER
            
            return IntentClassificationResult(
                intent=intent,
                confidence=min(confidence, 0.95),
                parameters={
                    'message': message,
                    'workbook_id': workbook_id,
                    'has_quantity': has_numbers,
                    'has_location': has_location,
                    'has_skills': has_skills,
                    'has_languages': has_languages,
                    'use_semantic': use_semantic
                },
                reasoning=f"Usuário quer filtrar candidatos {'com busca semântica' if use_semantic else 'com filtros específicos'}"
            )
        
        # 5. Verifica pergunta sobre candidato específico
        candidate_id_pattern = r'candidato\s+(\d+)|id\s*:?\s*(\d+)'
        candidate_id_match = re.search(candidate_id_pattern, message_lower)
        
        if candidate_id_match or (candidate_score > 0 and not filter_score):
            candidate_id = None
            if candidate_id_match:
                candidate_id = candidate_id_match.group(1) or candidate_id_match.group(2)
            
            return IntentClassificationResult(
                intent=ChatIntent.CANDIDATE_QUESTION,
                confidence=0.85,
                parameters={
                    'question': message,
                    'candidate_id': candidate_id,
                    'workbook_id': workbook_id
                },
                reasoning="Usuário quer informações sobre candidato específico"
            )
        
        # 6. Verifica pergunta sobre vaga (fallback)
        vaga_score = self._score_keywords(message_lower, self.vaga_keywords)
        if vaga_score > 0:
            return IntentClassificationResult(
                intent=ChatIntent.VAGA_QUESTION,
                confidence=0.8 + (vaga_score * 0.1),
                parameters={
                    'question': message,
                    'workbook_id': workbook_id
                },
                reasoning="Usuário quer informações sobre a vaga"
            )
        
        # 7. Verifica conversação genérica
        if self._is_generic_conversation(message_lower):
            return IntentClassificationResult(
                intent=ChatIntent.GENERIC_CONVERSATION,
                confidence=0.9,
                parameters={'message': message},
                reasoning="Conversação genérica (saudação, agradecimento, etc.)"
            )
        
        # 8. Intent desconhecida
        return IntentClassificationResult(
            intent=ChatIntent.UNKNOWN,
            confidence=0.3,
            parameters={'message': message, 'workbook_id': workbook_id},
            reasoning="Não foi possível classificar a intenção"
        )
    
    def _matches_keywords(self, text: str, keywords: List[str]) -> bool:
        """Verifica se o texto contém alguma das palavras-chave"""
        return any(keyword in text for keyword in keywords)
    
    def _score_keywords(self, text: str, keywords: List[str]) -> float:
        """Calcula um score baseado na presença de palavras-chave"""
        matches = sum(1 for keyword in keywords if keyword in text)
        return min(matches / len(keywords), 1.0)
    
    def _is_generic_conversation(self, text: str) -> bool:
        """Verifica se é uma conversação genérica"""
        clean_text = text.strip('.,!?;:')
        
        return (
            any(greeting in clean_text for greeting in self.greetings) or
            any(thank in clean_text for thank in self.thanks) or
            any(conf in clean_text for conf in self.confirmations) or
            any(farewell in clean_text for farewell in self.farewells)
        )
