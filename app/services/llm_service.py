import os
from app.core.logging import log_info, log_warning, log_error, log_debug, llm_log

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
