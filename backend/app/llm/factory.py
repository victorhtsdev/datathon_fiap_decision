import os
from .ollama_client import OllamaClient
from .deepseek_client import DeepSeekClient

def get_llm_client():
    backend = os.getenv("LLM_BACKEND", "ollama").lower()
    if backend == "deepseek":
        return DeepSeekClient()
    return OllamaClient()
