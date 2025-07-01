from fastapi import FastAPI
from app.routers import applicant_router
from app.llm.factory import get_llm_client

app = FastAPI()

app.include_router(applicant_router)

if __name__ == "__main__":
    # Exemplo de uso
    schema_snippet = '{"formacoes": [{"curso": "", "nivel": "", "instituicao": "", "ano_inicio": "", "ano_fim": "", "observacoes": null}]}'
    cv_text = "Seu texto de currículo aqui."
    llm_client = get_llm_client()
    result = llm_client.extract_section("formacoes", schema_snippet, cv_text)
    print(result)
