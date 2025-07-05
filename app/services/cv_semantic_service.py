import numpy as np
from app.llm.embedding_client import get_embedding_client

class CVSemanticService:
    def __init__(self):
        self.embedding_client = get_embedding_client()

    def cv_json_to_text(self, data):
        parts = []
        if "experiencias" in data:
            for exp in data["experiencias"]:
                empresa = exp.get("empresa", "")
                cargo = exp.get("cargo", "")
                inicio = exp.get("inicio", "")
                fim = exp.get("fim", "") or "o momento"
                descricao = exp.get("descricao", "")
                sentence = f"Experiência como {cargo} na empresa {empresa}, de {inicio} até {fim}. {descricao}".strip()
                parts.append(sentence)
        if "formacoes" in data:
            for form in data["formacoes"]:
                curso = form.get("curso", "")
                instituicao = form.get("instituicao", "")
                sentence = f"Formação acadêmica em {curso} pela instituição {instituicao}."
                parts.append(sentence)
        habilidades = data.get("habilidades", [])
        if habilidades:
            sentence = f"Habilidades técnicas incluem: {', '.join(habilidades)}."
            parts.append(sentence)
        idiomas = data.get("idiomas", [])
        if idiomas:
            idiomas_str = []
            for idioma in idiomas:
                nome = idioma.get("idioma", "")
                nivel = idioma.get("nivel", "")
                idiomas_str.append(f"{nome} ({nivel})")
            sentence = "Idiomas: " + ", ".join(idiomas_str) + "."
            parts.append(sentence)
        return " ".join(parts)

    def process(self, cv_json):
        try:
            text = self.cv_json_to_text(cv_json)
            embedding = self.embedding_client.generate_embedding(text, label="cv_semantic")
            if embedding is not None:
                return {
                    "cv_texto_semantico": text,
                    "cv_embedding": embedding.tobytes(),
                    "cv_embedding_vector": embedding.tolist(),
                }
            else:
                return {
                    "cv_texto_semantico": text,
                    "cv_embedding": None,
                    "cv_embedding_vector": None,
                }
        except Exception as e:
            # In case of error, return None for the fields without interrupting the flow
            return {
                "cv_texto_semantico": None,
                "cv_embedding": None,
                "cv_embedding_vector": None,
            }
