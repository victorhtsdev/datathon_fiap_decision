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
        """Remove códigos de escape ANSI do texto"""
        # Remove códigos ANSI completos (incluindo sequências de escape complexas)
        ansi_escape = re.compile(r'''
            \x1B  # ESC
            (?:   # 7-bit C1 Fe (exceto CSI)
                [@-Z\\-_]
            |     # ou [ para CSI, seguido por dados de parâmetro
                \[
                [0-?]*  # Parâmetros de 0-9:;<=>?
                [ -/]*  # Intermediários
                [@-~]   # Final
            )
        ''', re.VERBOSE)
        
        cleaned = ansi_escape.sub('', text)
        
        # Remove caracteres de spinner específicos do Unicode
        spinner_chars = ['⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏', '⠋']
        for char in spinner_chars:
            cleaned = cleaned.replace(char, '')
        
        # Remove padrões específicos do Ollama
        ollama_patterns = [
            r'\[.*?[GK]',  # Sequências como [1G, [K
            r'\?\d+[hl]',  # Sequências como ?2026h, ?25l
            r'\x1b\[\?\d+[hl]',  # Escape sequences específicas
        ]
        
        for pattern in ollama_patterns:
            cleaned = re.sub(pattern, '', cleaned)
        
        # Remove outros caracteres de controle
        control_chars = re.compile(r'[\x00-\x1F\x7F-\x9F]', re.MULTILINE)
        cleaned = control_chars.sub('', cleaned)
        
        # Limpa espaços extras e quebras de linha
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()
        
        return cleaned

    def extract_section(self, section_name, schema_snippet, cv_text):
        prompt = f"{schema_snippet}\n\n{cv_text}"
        if self.console_log:
            print(f"[OllamaClient] Sending prompt to model '{self.model_name}' for section '{section_name}'. Prompt size: {len(prompt)} chars")
        output = subprocess.check_output(
            ["ollama", "run", self.model_name, "--think=false"],
            input=prompt.encode("utf-8"),
            stderr=subprocess.STDOUT,
            timeout=300
        ).decode("utf-8")
        if self.console_log:
            print(f"[OllamaClient] Model response received for section '{section_name}'. Response size: {len(output)} chars")

        # ⚠️ Preserva comportamento anterior para JSON
        raw_json = output[output.find('{'):output.rfind('}') + 1]
        return json.loads(raw_json)

    def extract_text(self, prompt: str) -> str:
        if self.console_log:
            print(f"[OllamaClient] Sending raw prompt to model '{self.model_name}'. Prompt size: {len(prompt)} chars")
        output = subprocess.check_output(
            ["ollama", "run", self.model_name, "--think=false"],
            input=prompt.encode("utf-8"),
            stderr=subprocess.STDOUT,
            timeout=300
        ).decode("utf-8")
        
        # Limpa códigos de escape ANSI
        cleaned_output = self._clean_ansi_codes(output)
        
        if self.console_log:
            print(f"[OllamaClient] Model raw response received. Response size: {len(cleaned_output)} chars")
        return cleaned_output

    def chat(self, message: str, context: str = None) -> str:
        """
        Implementa conversação geral com o LLM
        """
        # Monta o prompt com contexto se fornecido
        if context:
            prompt = f"Contexto: {context}\n\nUsuário: {message}\n\nAssistente:"
        else:
            prompt = f"Usuário: {message}\n\nAssistente:"
        
        if self.console_log:
            print(f"[OllamaClient] Chat request to model '{self.model_name}'. Message: {message[:100]}...")
            
        try:
            output = subprocess.check_output(
                ["ollama", "run", self.model_name, "--think=false"],
                input=prompt.encode("utf-8"),
                stderr=subprocess.STDOUT,
                timeout=300
            ).decode("utf-8")
            
            # Limpa códigos de escape ANSI e caracteres de controle
            cleaned_output = self._clean_ansi_codes(output)
            
            if self.console_log:
                print(f"[OllamaClient] Chat response received. Raw size: {len(output)} chars, Cleaned size: {len(cleaned_output)} chars")
                print(f"[OllamaClient] Cleaned response: {cleaned_output[:200]}...")
                
            return cleaned_output
            
        except subprocess.TimeoutExpired:
            return "Desculpe, o tempo limite foi excedido. Tente uma pergunta mais simples."
        except Exception as e:
            if self.console_log:
                print(f"[OllamaClient] Chat error: {str(e)}")
            return "Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente."
