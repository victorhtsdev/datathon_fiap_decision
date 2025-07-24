import os
import re
import json
from openai import OpenAI
from .base import LLMClient

class OpenAIClient(LLMClient):
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o")
        self.console_log = os.getenv("LLM_CONSOLE_LOG", "false").lower() == "true"

    def _clean_ansi_codes(self, text: str) -> str:

        return re.sub(r'\s+', ' ', text).strip()

    def _call_api(self, prompt: str, max_tokens: int = 1200) -> str:
        client = OpenAI(api_key=self.api_key)
        if self.console_log:
            print(f"[OpenAIClient] Calling API with model '{self.model}' prompt size {len(prompt)} chars")
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Você é um especialista em extração de dados de CVs."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=max_tokens,
            response_format={"type": "text"} 
        )
        content = response.choices[0].message.content
        return self._clean_ansi_codes(content)

    def extract_section(self, section_name, prompt_base):
        """
        Extrai seção do CV usando prompt já montado. Faz fallback com prompt_fix em caso de erro.
        """
        if not self.api_key:
            return {"error": "API key do OpenAI não configurada."}
        # Primeira tentativa
        try:
            content = self._call_api(prompt_base, max_tokens=1500)
            raw = re.search(r"\{.*\}", content, re.DOTALL)
            if not raw:
                raise ValueError("JSON não encontrado")
            parsed = json.loads(raw.group())
        except Exception as e:
            # fallback
            fix_prompt = (
                f"{prompt_base}\n"
                f"⚠️ Erro: {e}\n"
                f"Resposta recebida:\n{content if 'content' in locals() else ''}\n"
                f"Por favor, retorne somente o JSON válido com a chave '{section_name}'."
            )
            try:
                content = self._call_api(fix_prompt, max_tokens=1500)
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
            return "Erro: API key do OpenAI não configurada."
        content = self._call_api(prompt, max_tokens=1200)
        return self._clean_ansi_codes(content)

    def chat(self, message: str, context: str = None) -> str:
        if not self.api_key:
            return "Erro: API key do OpenAI não configurada."
        sys_msg = context and f"Você é um assistente de recrutamento. Contexto: {context}" or "Você é um assistente de recrutamento."
        prompt = f"{sys_msg}\nUsuário: {message}"
        content = self._call_api(prompt, max_tokens=1000)
        return self._clean_ansi_codes(content)
