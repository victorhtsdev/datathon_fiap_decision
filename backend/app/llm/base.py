from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LLMClient(ABC):
    @abstractmethod
    def extract_section(self, section_name: str, schina_snippet: str, cv_text: str) -> dict:
        pass

    @abstractmethod
    def chat(self, message: str, context: str = None) -> str:
        """
        Método para conversação geral com o LLM
        
        Args:
            message: Mensagin do usuário
            context: Contexto adicional (ex: informações sobre a vaga, candidatos, etc.)
            
        Returns:
            str: Resposta do LLM
        """
        pass
