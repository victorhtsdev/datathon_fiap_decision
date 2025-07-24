import os
from .ollama_client import OllamaClient
from .deepseek_client import DeepSeekClient
from .openai_client import OpenAIClient 

def get_llm_client():
    backend = os.getenv("LLM_BACKEND", "ollama").lower()
    if backend == "deepseek":
        return DeepSeekClient()
    if backend == "openai":
        return OpenAIClient()
    return OllamaClient()
