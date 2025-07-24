import os
import re
import json
import requests
from .base import LLMClient

class DeepSeekClient(LLMClient):
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com/v1"
        self.console_log = os.getenv("LLM_CONSOLE_LOG", "false").lower() == "true"

    def _clean_ansi_codes(self, text: str) -> str:
        ansi = re.compile(r'(?:\x1B[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        cleaned = ansi.sub('', text)
        return re.sub(r'\s+', ' ', cleaned).strip()

    def _call_api(self, prompt: str, system_prompt: str = None, model: str = None) -> str:
        payload = {
            "model": model or "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt or "Você é um especialista em extração de dados de CVs."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0
        }
        if self.console_log:
            print(f"[DeepSeekClient] Calling API with prompt size {len(prompt)} chars")
        resp = requests.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=90
        )
        if resp.status_code != 200:
            raise ValueError(f"API error: {resp.status_code} - {resp.text}")
        return resp.json()["choices"][0]["message"]["content"]

    def extract_section(self, section_name, prompt_base):
        if not self.api_key:
            return {"error": "API key do DeepSeek não configurada."}
        try:
            content = self._call_api(prompt_base)
            raw = re.search(r"\{.*\}", content, re.DOTALL)
            if not raw:
                raise ValueError("JSON não encontrado")
            parsed = json.loads(raw.group())
        except Exception as e:
            fix_prompt = (
                f"{prompt_base}\n"
                f"⚠️ Erro: {e}\n"
                f"Resposta recebida:\n{content if 'content' in locals() else ''}\n"
                f"Por favor, retorne somente o JSON válido com a chave '{section_name}'."
            )
            try:
                content = self._call_api(fix_prompt)
                raw = re.search(r"\{.*\}", content, re.DOTALL)
                if not raw:
                    raise ValueError("JSON não encontrado após fix")
                parsed = json.loads(raw.group())
            except Exception as e2:
                return {"error": f"Falha após prompt_fix: {e2}"}
        if isinstance(parsed, list):
            parsed = {section_name: parsed}
        return parsed

    def extract_text(self, prompt: str) -> str:
        if not self.api_key:
            return "Erro: API key do DeepSeek não configurada."
        content = self._call_api(prompt)
        return self._clean_ansi_codes(content)

    def chat(self, message: str, context: str = None) -> str:
        if not self.api_key:
            return "Erro: API key do DeepSeek não configurada."
        sys_msg = context or "Você é um assistente de recrutamento especialista em JSON, precisa entender o contextoe  retornar o JSON VÁLIDO no schema solicitado. "
        content = self._call_api(
            message,
            system_prompt=sys_msg,
            model="deepseek-chat"
        )
        return self._clean_ansi_codes(content)
