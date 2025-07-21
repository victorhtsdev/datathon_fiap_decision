from app.repositories.vaga_repository import get_vaga_by_id, create_vaga, update_vaga
from app.services.vaga_extractor_service import VagaExtractorService
from app.schemas.vaga import VagaCreate, VagaUpdate
from app.models.vaga import StatusVaga
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
            
            vaga_existente = get_vaga_by_id(db, vaga_id)
            if vaga_existente:
                log_info(f"[Orchestrator] Processing existing vaga {vaga_id}")
                # Não força mudança de status para vaga existente, mantém o atual
                
                # Initialize extractor only when needed
                extractor = VagaExtractorService()
                extractor.processar_vaga(db, vaga_id, vaga_dict)
                
                # Não atualiza status automaticamente após processamento
                log_info(f"[Orchestrator] Finished processing existing vaga {vaga_id}")
            else:
                log_info(f"[Orchestrator] Creating new vaga {vaga_id}")
                # Cria nova vaga com status padrão 'nao_iniciada' (a menos que seja especificado no vaga_dict)
                status_inicial = vaga_dict.get('status_vaga', StatusVaga.nao_iniciada)
                db_vaga = create_vaga(db, VagaCreate(**vaga_dict), {"status_vaga": status_inicial})
                db.commit()
                if db_vaga.id:
                    # Initialize extractor only when needed
                    extractor = VagaExtractorService()
                    extractor.processar_vaga(db, db_vaga.id, vaga_dict)
                    
                    # Não força mudança de status após processamento
                    log_info(f"[Orchestrator] Finished processing new vaga {db_vaga.id}")
                else:
                    log_error(f"[Orchestrator] Failed to create vaga, no ID returned")

        except Exception as e:
            log_error(f"[Orchestrator] Error processing vaga {vaga_id}: {e}")
            # Add detailed debug info
            log_error(f"[Orchestrator] StatusVaga enum values: {[e.value for e in StatusVaga]}")
            log_error(f"[Orchestrator] Traceback: {traceback.format_exc()}")
        finally:
            db.close()
            log_info(f"[Orchestrator] Finished processing vaga {vaga_id}")