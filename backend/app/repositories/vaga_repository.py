from sqlalchemy.orm import Session
from app.models.vaga import Vaga
from typing import Optional

def get_vaga_by_id(db: Session, vaga_id: int) -> Optional[Vaga]:
    return db.query(Vaga).filter(Vaga.id == vaga_id).first()

def create_vaga(db: Session, vaga, extra_fields: dict) -> Vaga:
    # Accept both dict and Pydantic models
    if hasattr(vaga, 'dict'):
        vaga_data = vaga.dict(exclude_unset=True)
    elif hasattr(vaga, 'model_dump'):
        vaga_data = vaga.model_dump(exclude_unset=True)
    else:
        vaga_data = vaga
    
    db_vaga = Vaga(**vaga_data, **extra_fields)
    db.add(db_vaga)
    db.commit()
    db.refresh(db_vaga)
    return db_vaga

def update_vaga(db: Session, vaga_id: int, vaga_update, extra_fields: dict) -> Optional[Vaga]:
    db_vaga = get_vaga_by_id(db, vaga_id)
    if not db_vaga:
        return None
    
    # Accept both dict and Pydantic models
    if hasattr(vaga_update, 'dict'):
        update_data = vaga_update.dict(exclude_unset=True)
    elif hasattr(vaga_update, 'model_dump'):
        update_data = vaga_update.model_dump(exclude_unset=True)
    else:
        update_data = vaga_update
    
    for field, value in update_data.items():
        setattr(db_vaga, field, value)
    
    for field, value in extra_fields.items():
        setattr(db_vaga, field, value)
    
    db.commit()
    db.refresh(db_vaga)
    return db_vaga