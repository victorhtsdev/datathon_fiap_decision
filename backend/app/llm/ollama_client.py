import subprocess
import json
import os
import re
from .base import LLMClient

class OllamaClient(LLMClient):
    def __init__(self, model_name=None):
        self.model_name = model_name or os.getenv("OLLAMA_MODEL", "gemma3:4b-it-qat")
        self.console_log = os.getenv("LLM_CONSOLE_LOG", "false").lower() == "true"

    def _clean_ansi_codes(self, text: str) -> str:
        ansi_escape = re.compile(r'''
            \x1B
            (?:
                [@-Z\\-_]
            |
                \[
                [0-?]*
                [ -/]*
                [@-~]
            )
        ''', re.VERBOSE)
        cleaned = ansi_escape.sub('', text)
        spinner_chars = ['⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏', '⠋']
        for char in spinner_chars:
            cleaned = cleaned.replace(char, '')
        ollama_patterns = [
            r'\[.*?[GK]',
            r'\?\d+[hl]',
            r'\x1b\[\?\d+[hl]',
        ]
        for pattern in ollama_patterns:
            cleaned = re.sub(pattern, '', cleaned)
        cleaned = re.compile(r'[\x00-\x1F\x7F-\x9F]', re.MULTILINE).sub('', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def extract_section(self, section_name: str, prompt_base: str) -> dict:
        """
        Extrai a seção indicada do CV usando um prompt já montado.
        Tenta parsear o JSON retornado; se falhar, envia um prompt de correção e parseia novamente.
        """
        if self.console_log:
            print(f"[OllamaClient] Enviando prompt para seção '{section_name}' (modelo {self.model_name}), tamanho {len(prompt_base)} chars")
        try:
            output = subprocess.check_output(
                ["ollama", "run", self.model_name, "--think=false"],
                input=prompt_base.encode("utf-8"),
                stderr=subprocess.STDOUT,
                timeout=300
            ).decode("utf-8")
            if self.console_log:
                print(f"[OllamaClient] Resposta recebida, tamanho {len(output)} chars")
            cleaned = self._clean_ansi_codes(output)
            if "{" not in cleaned or "}" not in cleaned:
                raise ValueError("Resposta não contém JSON")
            json_str = cleaned[cleaned.find("{"):cleaned.rfind("}")+1]
            parsed = json.loads(json_str)
        except Exception as first_err:
            if self.console_log:
                print(f"[OllamaClient] Erro ao parsear JSON inicial: {first_err}")
            fix_prompt = (
                f"{prompt_base}\n\n"
                f"⚠️ A resposta anterior apresentou o erro: {first_err}\n"
                f"Resposta recebida:\n{output if 'output' in locals() else ''}\n\n"
                f"Por favor, corrija e retorne apenas o JSON válido contendo a chave '{section_name}'."
            )
            try:
                output = subprocess.check_output(
                    ["ollama", "run", self.model_name, "--think=false"],
                    input=fix_prompt.encode("utf-8"),
                    stderr=subprocess.STDOUT,
                    timeout=300
                ).decode("utf-8")
                if self.console_log:
                    print(f"[OllamaClient] Resposta corrigida recebida, tamanho {len(output)} chars")
                cleaned = self._clean_ansi_codes(output)
                if "{" not in cleaned or "}" not in cleaned:
                    raise ValueError("Resposta corrigida não contém JSON")
                json_str = cleaned[cleaned.find("{"):cleaned.rfind("}")+1]
                parsed = json.loads(json_str)
            except Exception as second_err:
                return {"error": f"Falha após prompt de correção: {second_err}. Resposta raw: {output if 'output' in locals() else ''}"}
        if isinstance(parsed, list):
            parsed = {section_name: parsed}
        return parsed

    def extract_text(self, prompt: str) -> str:
        if self.console_log:
            print(f"[OllamaClient] Enviando prompt de texto cru (tamanho {len(prompt)} chars)")
        output = subprocess.check_output(
            ["ollama", "run", self.model_name, "--think=false"],
            input=prompt.encode("utf-8"),
            stderr=subprocess.STDOUT,
            timeout=300
        ).decode("utf-8")
        cleaned_output = self._clean_ansi_codes(output)
        if self.console_log:
            print(f"[OllamaClient] Texto recebido e limpo (tamanho {len(cleaned_output)} chars)")
        return cleaned_output

    def chat(self, message: str, context: str = None) -> str:
        if context:
            prompt = f"Contexto: {context}\n\nUsuário: {message}\n\nAssistente:"
        else:
            prompt = f"Usuário: {message}\n\nAssistente:"
        if self.console_log:
            print(f"[OllamaClient] Chat para '{self.model_name}'. Mensagem: {message[:100]}...")
        try:
            output = subprocess.check_output(
                ["ollama", "run", self.model_name, "--think=false"],
                input=prompt.encode("utf-8"),
                stderr=subprocess.STDOUT,
                timeout=300
            ).decode("utf-8")
            cleaned_output = self._clean_ansi_codes(output)
            if self.console_log:
                print(f"[OllamaClient] Resposta bruta: {len(output)} chars; limpa: {len(cleaned_output)} chars")
                print(f"[OllamaClient] Conteúdo limpo: {cleaned_output[:200]}...")
            return cleaned_output
        except subprocess.TimeoutExpired:
            return "Desculpe, o tempo limite foi excedido. Tente uma pergunta mais simples."
        except Exception as e:
            if self.console_log:
                print(f"[OllamaClient] Erro no chat: {e}")
            return "Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente."
