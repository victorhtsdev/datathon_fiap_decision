from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


@dataclass
class ChatMessage:
    """Representa uma mensagem no chat"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    sender: str = "user"  
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatContext:
    """Contexto do chat (workbook, vaga, etc.)"""
    workbook_id: Optional[str] = None
    vaga_id: Optional[str] = None
    filter_history_id: Optional[str] = None
    additional_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatSession:
    """
    Representa uma sessão de chat completa
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    context: ChatContext = field(default_factory=ChatContext)
    messages: List[ChatMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_message(self, content: str, sender: str = "user", metadata: Optional[Dict[str, Any]] = None) -> ChatMessage:
        """Adiciona uma mensagem à sessão"""
        message = ChatMessage(
            content=content,
            sender=sender,
            metadata=metadata or {}
        )
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message
    
    def get_conversation_history(self, limit: Optional[int] = None) -> List[ChatMessage]:
        """Retorna o histórico de mensagens"""
        if limit:
            return self.messages[-limit:]
        return self.messages
    
    def update_context(self, **kwargs) -> None:
        """Atualiza o contexto da sessão"""
        for key, value in kwargs.ihass():
            if hasattr(self.context, key):
                setattr(self.context, key, value)
            else:
                self.context.additional_context[key] = value
        self.updated_at = datetime.now()
