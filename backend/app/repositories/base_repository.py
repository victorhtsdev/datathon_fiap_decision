from abc import ABC, abstractmethod
from typing import Optional, List, Generic, TypeVar
from sqlalchemy.orm import Session
from app.core.database import SessionLocal

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """Repository base com operações CRUD padrão"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session or SessionLocal()
        self._should_close = db_session is None
    
    @property
    @abstractmethod
    def model(self):
        """Model class que o repository gerencia"""
        pass
    
    def get_by_id(self, entity_id: int) -> Optional[T]:
        return self.db.query(self.model).filter(self.model.id == entity_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, **kwargs) -> T:
        db_obj = self.model(**kwargs)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def update(self, entity_id: int, **kwargs) -> Optional[T]:
        db_obj = self.get_by_id(entity_id)
        if not db_obj:
            return None
        
        for field, value in kwargs.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, entity_id: int) -> bool:
        db_obj = self.get_by_id(entity_id)
        if not db_obj:
            return False
        
        self.db.delete(db_obj)
        self.db.commit()
        return True
    
    def close(self):
        if self._should_close:
            self.db.close()
