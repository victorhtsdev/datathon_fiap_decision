import os
from .base import LLMClient

class DeepSeekClient(LLMClient):
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")

    def extract_section(self, section_name, schema_snippet, cv_text):
        # Aqui vai a chamada à API do DeepSeek (ainda não implementada)
        raise NotImplementedError("DeepSeek API integration not implemented yet.")
