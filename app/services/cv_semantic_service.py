import numpy as np
from app.llm.embedding_client import get_embedding_client

class CVSemanticService:
    def __init__(self):
        self.embedding_client = get_embedding_client()

    def cv_json_to_text(self, data):
        partes = []
        if "experiencias" in data:
            for exp in data["experiencias"]:
                empresa = exp.get("empresa", "")
                cargo = exp.get("cargo", "")
                inicio = exp.get("inicio", "")
                fim = exp.get("fim", "") or "o momento"
                descricao = exp.get("descricao", "")
                frase = f"Experiência como {cargo} na empresa {empresa}, de {inicio} até {fim}. {descricao}".strip()
                partes.append(frase)
        if "formacoes" in data:
            for form in data["formacoes"]:
                curso = form.get("curso", "")
                instituicao = form.get("instituicao", "")
                frase = f"Formação acadêmica em {curso} pela instituição {instituicao}."
                partes.append(frase)
        habilidades = data.get("habilidades", [])
        if habilidades:
            frase = f"Habilidades técnicas incluem: {', '.join(habilidades)}."
            partes.append(frase)
        idiomas = data.get("idiomas", [])
        if idiomas:
            idiomas_str = []
            for idioma in idiomas:
                nome = idioma.get("idioma", "")
                nivel = idioma.get("nivel", "")
                idiomas_str.append(f"{nome} ({nivel})")
            frase = "Idiomas: " + ", ".join(idiomas_str) + "."
            partes.append(frase)
        return " ".join(partes)

    def process(self, cv_json):
        try:
            texto = self.cv_json_to_text(cv_json)
            embedding = self.embedding_client.generate_embedding(texto, label="cv_semantic")
            if embedding is not None:
                return {
                    "cv_texto_semantico": texto,
                    "cv_embedding": embedding.tobytes(),
                    "cv_embedding_vector": embedding.tolist(),
                }
            else:
                return {
                    "cv_texto_semantico": texto,
                    "cv_embedding": None,
                    "cv_embedding_vector": None,
                }
        except Exception as e:
            # Em caso de erro, retorna None para os campos sem interromper o fluxo
            return {
                "cv_texto_semantico": None,
                "cv_embedding": None,
                "cv_embedding_vector": None,
            }
