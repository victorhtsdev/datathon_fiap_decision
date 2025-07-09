import subprocess
import json
import os
from .base import LLMClient

class OllamaClient(LLMClient):
    def __init__(self, model_name=None):
        self.model_name = model_name or os.getenv("OLLAMA_MODEL", "gemma3:4b-it-qat")
        self.console_log = os.getenv("LLM_CONSOLE_LOG", "false").lower() == "true"

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
        if self.console_log:
            print(f"[OllamaClient] Model raw response received. Response size: {len(output)} chars")
        return output.strip()
