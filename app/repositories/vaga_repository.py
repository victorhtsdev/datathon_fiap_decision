from sqlalchemy.orm import Session
from app.models.vaga import Vaga
from app.schemas.vaga import VagaCreate, VagaUpdate
from typing import Optional

def get_vaga_by_id(db: Session, vaga_id: int) -> Optional[Vaga]:
    return db.query(Vaga).filter(Vaga.id == vaga_id).first()

def create_vaga(db: Session, vaga: VagaCreate, extra_fields: dict) -> Vaga:
    db_vaga = Vaga(**vaga.dict(exclude_unset=True), **extra_fields)
    db.add(db_vaga)
    db.commit()
    db.refresh(db_vaga)
    return db_vaga

def update_vaga(db: Session, vaga_id: int, vaga_update: VagaUpdate, extra_fields: dict) -> Optional[Vaga]:
    db_vaga = get_vaga_by_id(db, vaga_id)
    if not db_vaga:
        return None
    for field, value in vaga_update.dict(exclude_unset=True).items():
        setattr(db_vaga, field, value)
    for field, value in extra_fields.items():
        setattr(db_vaga, field, value)
    db.commit()
    db.refresh(db_vaga)
    return db_vaga
