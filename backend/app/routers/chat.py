from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.schemas.chat import ChatRequest, ChatResponse, ChatHistoryResponse
from app.chat.services.chat_service import ChatService
from app.dependencies import get_db

router = APIRouter()

def get_chat_service(db: Session = Depends(get_db)):
    return ChatService(db)

@router.post("/chat", response_model=ChatResponse)
async def chat_with_llm(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Endpoint para conversar com o LLM usando nova arquitetura modular
    
    Permite conversa geral ou no contexto de um workbook específico.
    Agora suporta sessões persistentes e classificação de intenções.
    """
    result = await chat_service.chat_with_context(
        message=request.message,
        workbook_id=request.workbook_id,
        context=request.context,
        session_id=request.session_id
    )
    
    return ChatResponse(
        response=result['response'],
        workbook_id=request.workbook_id,
        session_id=result.get('session_id'),
        filtered_candidates=result.get('filtered_candidates'),
        total_candidates=result.get('total_candidates'),
        intent=result.get('intent'),
        confidence=result.get('confidence')
    )

@router.get("/chat/history/{session_id}", response_model=ChatHistoryResponse)
def get_chat_history(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Endpoint para obter histórico de uma sessão de chat
    """
    history = chat_service.get_session_history(session_id)
    
    if not history:
        return ChatHistoryResponse(
            session_id=session_id,
            found=False,
            messages=[]
        )
    
    return ChatHistoryResponse(
        session_id=history['session_id'],
        found=True,
        context=history['context'],
        messages=history['messages'],
        created_at=history['created_at'],
        updated_at=history['updated_at']
    )

@router.delete("/chat/session/{session_id}")
def clear_chat_session(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Endpoint para limpar uma sessão de chat
    """
    success = chat_service.clear_session(session_id)
    
    return {
        "session_id": session_id,
        "cleared": success,
        "message": "Sessão removida com sucesso" if success else "Sessão não encontrada"
    }
