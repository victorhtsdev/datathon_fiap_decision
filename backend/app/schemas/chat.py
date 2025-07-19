from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from datetime import datetime

class ChatRequest(BaseModel):
    message: str
    workbook_id: Optional[str] = None
    context: Optional[str] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    workbook_id: Optional[str] = None
    session_id: Optional[str] = None
    filtered_candidates: Optional[List[Any]] = None  # Lista de candidatos filtrados
    total_candidates: Optional[int] = None  # Total de candidatos encontrados
    intent: Optional[str] = None  # Intenção classificada
    confidence: Optional[float] = None  # Confiança da classificação

class ChatMessage(BaseModel):
    id: str
    content: str
    sender: str  # 'user' ou 'assistant'
    timestamp: str  # ISO format
    metadata: Dict[str, Any] = {}

class ChatHistoryResponse(BaseModel):
    session_id: str
    found: bool
    context: Optional[Dict[str, Any]] = None
    messages: List[ChatMessage] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
