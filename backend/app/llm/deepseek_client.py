import os
import requests
import json
from .base import LLMClient

class DeepSeekClient(LLMClient):
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com/v1"

    def extract_section(self, section_name, schema_snippet, cv_text):
        # Aqui vai a chamada à API do DeepSeek (ainda não implementada)
        raise NotImplementedError("DeepSeek API integration not implemented yet.")

    def chat(self, message: str, context: str = None) -> str:
        """
        Implementa conversação geral com DeepSeek API
        """
        if not self.api_key:
            return "Erro: API key do DeepSeek não configurada."
        
        # Monta as mensagens para a API
        messages = []
        
        if context:
            messages.append({
                "role": "system",
                "content": f"Você é um assistente especializado em recrutamento. Contexto: {context}"
            })
        else:
            messages.append({
                "role": "system", 
                "content": "Você é um assistente especializado em recrutamento e análise de candidatos."
            })
            
        messages.append({
            "role": "user",
            "content": message
        })

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "max_tokens": 1000,
                    "temperature": 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                return f"Erro na API: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "Desculpe, o tempo limite foi excedido. Tente uma pergunta mais simples."
        except Exception as e:
            return f"Desculpe, ocorreu um erro ao processar sua mensagem: {str(e)}"
