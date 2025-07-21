import os
import requests
import json
from .base import LLMClient

class DeepSeekClient(LLMClient):
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com/v1"

    def extract_section(self, section_name, schema_snippet, cv_text):
        """
        Extrai seção específica do CV usando DeepSeek API
        """
        if not self.api_key:
            return {"error": "API key do DeepSeek não configurada."}
        
        prompt = f"""
        Analise o seguinte CV e extraia informações da seção "{section_name}" seguindo o schema fornecido.
        
        Schema esperado:
        {schema_snippet}
        
        CV:
        {cv_text}
        
        Retorne um JSON válido com as informações extraídas da seção "{section_name}".
        """
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {
                            "role": "system",
                            "content": "Você é um especialista em extração de dados de CVs. Sempre retorne respostas em formato JSON válido."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 1500,
                    "temperature": 0.3
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                
                # Tentar extrair JSON da resposta
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except json.JSONDecodeError:
                        return {"error": "Resposta não é um JSON válido", "content": content}
                else:
                    return {"error": "JSON não encontrado na resposta", "content": content}
            else:
                return {"error": f"Erro na API: {response.status_code} - {response.text}"}
                
        except requests.exceptions.Timeout:
            return {"error": "Tempo limite excedido na chamada da API"}
        except Exception as e:
            return {"error": f"Erro ao processar: {str(e)}"}

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
