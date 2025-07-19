import os
from app.core.logging import log_info, log_warning, log_error, log_debug, llm_log
from app.llm.factory import get_llm_client


class LLMService:
    """Service para integração com modelos LLM"""
    
    def __init__(self):
        self.llm_client = get_llm_client()
    
    async def process_with_llm(self, prompt: str) -> str:
        """
        Processa um prompt com o modelo LLM configurado
        """
        try:
            log_info(f"Processando prompt com LLM (tamanho: {len(prompt)} chars)")
            
            # Usar o client LLM para processar o prompt
            response = self.llm_client.chat(prompt)
            
            log_info(f"Resposta do LLM recebida (tamanho: {len(response)} chars)")
            return response
            
        except Exception as e:
            log_error(f"Erro ao processar prompt com LLM: {str(e)}")
            raise


def split_chunks_and_log(text, chunk_size=None, debug=False):
    chunk_size = chunk_size or int(os.getenv("CHUNK_SIZE", "5000"))
    debug = debug or os.getenv("DEBUG", "false").lower() == "true"
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    llm_log(f"[LLMService] Total chunks: {len(chunks)} (chunk size: {chunk_size})")
    if debug:
        print(f"[LLMService] Total chunks: {len(chunks)} (chunk size: {chunk_size})")
    for i, chunk in enumerate(chunks):
        llm_log(f"[LLMService] Chunk {i+1}/{len(chunks)} size: {len(chunk)} chars")
        if debug:
            print(f"[LLMService] Chunk {i+1}/{len(chunks)} size: {len(chunk)} chars")
    return chunks
