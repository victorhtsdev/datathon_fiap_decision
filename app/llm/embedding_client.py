import os
import openai
import numpy as np

class EmbeddingClient:
    def generate_embedding(self, text, label=""):
        raise NotImplementedError

class OpenAIEmbeddingClient(EmbeddingClient):
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
        self.client = openai.OpenAI(api_key=self.api_key)

    def generate_embedding(self, text, label=""):
        import time
        try:
            start = time.time()
            response = self.client.embeddings.create(input=[text], model=self.model)
            elapsed = time.time() - start
            print(f"[Embedding] Time to generate embedding ({label}): {elapsed:.2f}s")
            return np.array(response.data[0].embedding, dtype=np.float32)
        except Exception as e:
            print(f"[Embedding] Error generating embedding ({label}): {e}")
            return None

def get_embedding_client():
    backend = os.getenv("EMBEDDING_BACKEND", "openai").lower()
    if backend == "openai":
        return OpenAIEmbeddingClient()
    raise NotImplementedError(f"Embedding backend '{backend}' not implemented.")
