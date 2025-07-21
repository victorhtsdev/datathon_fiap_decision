from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from app.schemas.vaga import VagaCreate, VagaUpdate
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.vaga import Vaga
from app.services.vaga_processing_orchestrator import VagaProcessingOrchestrator
from app.core.logging import log_info, log_warning, log_error
from app.core.processing_registry import ProcessingRegistryBase
from concurrent.futures import ThreadPoolExecutor
import traceback

router = APIRouter()
executor = ThreadPoolExecutor(max_workers=4)

class VagaProcessingRegistry(ProcessingRegistryBase):
    pass

registry = VagaProcessingRegistry()

def process_vaga_in_background(vaga_dict):
    vaga_id = vaga_dict["id"]
    log_info(f"[BG] Starting processing for vaga {vaga_id}")
    orchestrator = VagaProcessingOrchestrator()
    try:
        orchestrator.process_vaga(vaga_dict, vaga_id)
        log_info(f"[BG] Finished processing for vaga {vaga_id}")
    except Exception as e:
        log_error(f"[BG] Error processing vaga {vaga_id}: {e}\n{traceback.format_exc()}")
    finally:
        registry.finish_processing(vaga_id)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/vagas/lista")
def listar_vagas(apenas_ativas: bool = True, db: Session = Depends(get_db)):
    """
    Lista vagas. Por padrão, retorna apenas vagas ativas disponíveis para criação de workbook.
    Use apenas_ativas=false para listar todas as vagas.
    """
    query = db.query(Vaga.id, Vaga.informacoes_basicas_titulo_vaga, Vaga.status_vaga)
    
    if apenas_ativas:
        # Show only 'open' jobs (without workbook created yet)
        query = query.filter(Vaga.status_vaga == 'aberta')
    
    vagas = query.all()
    return [
        {
            "id": v.id, 
            "informacoes_basicas_titulo_vaga": v.informacoes_basicas_titulo_vaga,
            "status_vaga": v.status_vaga.value if hasattr(v.status_vaga, 'value') else v.status_vaga
        }
        for v in vagas
    ]

@router.get("/vagas/abertas")
def listar_vagas_abertas(db: Session = Depends(get_db)):
    """
    Lista apenas vagas com status 'aberta'.
    """
    vagas = db.query(Vaga.id, Vaga.informacoes_basicas_titulo_vaga, Vaga.status_vaga)\
             .filter(Vaga.status_vaga == 'aberta')\
             .all()
    
    return [
        {
            "id": v.id, 
            "informacoes_basicas_titulo_vaga": v.informacoes_basicas_titulo_vaga,
            "status_vaga": v.status_vaga.value if hasattr(v.status_vaga, 'value') else v.status_vaga
        }
        for v in vagas
    ]

# Endpoint for job details (excluding embedding)
@router.get("/vagas/{vaga_id}")
def detalhes_vaga(vaga_id: int, db: Session = Depends(get_db)):
    vaga = db.query(Vaga).filter(Vaga.id == vaga_id).first()
    if not vaga:
        return {"error": "Vaga not found"}
    # Exclude embedding fields
    data = {c.name: getattr(vaga, c.name) for c in vaga.__table__.columns if c.name not in ["vaga_embedding", "vaga_embedding_vector"]}
    return data

@router.post("/vagas")
def process_vaga(vaga: VagaCreate, background_tasks: BackgroundTasks):
    vaga_id = vaga.id
    log_info(f"[API] Received request to process vaga: {vaga_id}")
    if registry.is_processing(vaga_id):
        log_warning(f"Vaga {vaga_id} is already being processed.")
        return {"error": "This vaga is already being processed. Please wait until it finishes."}
    if not registry.start_processing(vaga_id):
        log_warning(f"Vaga {vaga_id} could not be marked as processing.")
        return {"error": "Failed to start processing vaga."}

    vaga_dict = vaga.dict()
    background_tasks.add_task(executor.submit, process_vaga_in_background, vaga_dict)
    log_info(f"[API] Background task added for vaga {vaga_id}")
    return {"message": "Vaga received for processing."}


