from app.repositories.vaga_repository import get_vaga_by_id, create_vaga
from app.services.vaga_extractor_service import VagaExtractorService
from app.schemas.vaga import VagaCreate
from app.core.database import SessionLocal
from app.core.logging import log_info, log_error
import traceback

class VagaProcessingOrchestrator:
    def __init__(self):
        log_info("[Orchestrator] Initializing VagaProcessingOrchestrator")

    def process_vaga(self, vaga_dict, vaga_id):
        db = SessionLocal()
        try:
            log_info(f"[Orchestrator] Starting process_vaga for vaga {vaga_id}")
            extractor = VagaExtractorService()

            vaga_existente = get_vaga_by_id(db, vaga_id)
            if vaga_existente:
                log_info(f"[Orchestrator] Updating existing vaga {vaga_id}")
                extractor.processar_vaga(db, vaga_id, vaga_dict)
            else:
                log_info(f"[Orchestrator] Creating new vaga {vaga_id}")
                db_vaga = create_vaga(db, VagaCreate(**vaga_dict), {})
                db.commit()
                if db_vaga.id:
                    extractor.processar_vaga(db, db_vaga.id, vaga_dict)
                else:
                    log_error(f"[Orchestrator] Failed to create vaga, no ID returned")

        except Exception as e:
            log_error(f"[Orchestrator] Error processing vaga {vaga_id}: {e}\n{traceback.format_exc()}")
        finally:
            db.close()
            log_info(f"[Orchestrator] Finished processing vaga {vaga_id}")
