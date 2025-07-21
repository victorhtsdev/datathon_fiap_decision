import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import applicant_router, vaga_router, workbook_router, processed_applicant_router, chat_router, prospects_match_router, semantic_performance
from app.llm.factory import get_llm_client

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="DataThon Decision API",
    description="Candidate and Job Matching System",
    version="1.0.0"
)

# Configure CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",
        "http://localhost:5174",  # Vite dev server (alternative port)
        "http://127.0.0.1:5174",
        "http://localhost:5175",  # Vite dev server (alternative port)
        "http://127.0.0.1:5175",
        "http://localhost:3000",  # React dev server alternative
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(applicant_router)
app.include_router(vaga_router)
app.include_router(workbook_router)
app.include_router(processed_applicant_router)
app.include_router(chat_router)
app.include_router(prospects_match_router)
app.include_router(semantic_performance.router)


@app.get("/health")
def health_check():
    """Health check endpoint to verify API status and available endpoints."""
    return {
        "status": "ok",
        "message": "DataThon Decision API is running",
        "endpoints": [
            "/vagas/lista",
            "/workbook",
            "/processed-applicants",
            "/docs"
        ]
    }


if __name__ == "__main__":
    # Example usage for testing LLM integration
    schema_snippet = '{"formacoes": [{"curso": "", "nivel": "", "instituicao": "", "ano_inicio": "", "ano_fim": "", "observacoes": null}]}'
    cv_text = "Your CV text here."
    llm_client = get_llm_client()
    result = llm_client.extract_section("formacoes", schema_snippet, cv_text)
    print(result)
