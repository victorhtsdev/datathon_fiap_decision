from typing import Dict, Any

from app.chat.handlers.base_handler import BaseChatHandler
from app.chat.models.chat_session import ChatSession
from app.core.logging import log_info, log_error


class GenericConversationHandler(BaseChatHandler):
    """Handler for generic conversations (greetings, thanks, etc.)"""
    
    def __init__(self, db=None):
        super().__init__(db)
        self.db = db
    
    def handle(self, parameters: Dict[str, Any], session: ChatSession) -> Dict[str, Any]:
        """
        Handles generic conversations like greetings
        """
        try:
            log_info(f"GenericHandler.handle called with parameters: {parameters}")
            
            message = parameters.get('message', '').lower().strip()
            log_info(f"Processing generic message: '{message}'")
            
            # Remove punctuation for analysis
            clean_message = message.strip('.,!?;:')
            
            greetings = ['olá', 'ola', 'oi', 'hey', 'hello', 'hi', 'bom dia', 'boa tarde', 'boa noite']
            thanks = ['obrigado', 'obrigada', 'valeu', 'thanks']
            confirmations = ['ok', 'certo', 'entendi', 'beleza']
            farewells = ['tchau', 'até mais', 'bye', 'até logo']
            
            if any(greeting in clean_message for greeting in greetings):
                response = self._get_greeting_response()
            elif any(thank in clean_message for thank in thanks):
                response = self._get_thanks_response()
            elif any(conf in clean_message for conf in confirmations):
                response = self._get_confirmation_response()
            elif any(farewell in clean_message for farewell in farewells):
                response = self._get_farewell_response()
            else:
                response = self._get_help_response()
            
            log_info(f"GenericHandler returning response: {response[:50]}...")
            return self._create_response(response)
            
        except Exception as e:
            log_error(f"Error in GenericHandler.handle: {str(e)}")
            return self._create_response("Olá! Como posso ajudá-lo hoje?")
    
    def _get_greeting_response(self) -> str:
        """Response for greetings"""
        return """Olá!

Sou seu assistente especializado in **recrutamento e seleção**. Estou aqui para ajudá-lo a encontrar os melhores candidatos para esta vaga!

Posso ajudá-lo a:
- **Filtrar candidatos** - Ex: "filtre 5 candidatos com Java", "busque pessoas de São Paulo"
- **Analisar candidatos** - Ex: "me fale sobre o candidato ID 123"
- **Consultar a vaga** - Ex: "quais são os requisitos?", "me explique as responsabilidades"
🔄 **Gerenciar filtros** - Ex: "histórico de filtros", "resetar filtros"

Como posso ajudá-lo hoje?"""
    
    def _get_thanks_response(self) -> str:
        """Response for thanks"""
        return """De nada! 😊 

Estou aqui para tornar seu processo de recrutamento mais eficiente. Se precisar filtrar mais candidatos ou analisar perfis específicos, é só me avisar!

Posso ajudar com:
• Filters adicionais ou refinamento de busca
• Análise detalhada de candidatos específicos
• Informações sobre requisitos da vaga
• Histórico e gerenciamento de filtros aplicados"""
    
    def _get_confirmation_response(self) -> str:
        """Response for confirmations"""
        return "Perfeito! Se precisar de ajuda com candidatos ou informações sobre a vaga, estarei aqui. 👍"
    
    def _get_farewell_response(self) -> str:
        """Response for farewells"""
        return "Até mais! Foi um prazer ajudar com o processo de recrutamento."
    
    def _get_help_response(self) -> str:
        """Help response when message is not understood"""
        return """Não entendi bin sua solicitação.

Como assistente de **recrutamento**, posso ajudá-lo com:

• **Filtrar candidatos** com critérios específicos
  Ex: "encontre 10 desenvolvedores Python"
  
• **Analisar perfis** de candidatos individuais
  Ex: "me conte sobre o candidato ID 456"
  
• **Consultar informações** sobre a vaga atual
  Ex: "quais os requisitos técnicos?"

• **Gerenciar filtros aplicados**
  Ex: "histórico de filtros", "resetar filtros"

Tente uma dessas opções! 🚀"""
