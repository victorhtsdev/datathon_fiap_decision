from fastapi import APIRouter, BackgroundTasks
from app.schemas.vaga import VagaCreate
from app.services.vaga_processing_orchestrator import VagaProcessingOrchestrator
from app.core.logging import log_info, log_warning, log_error
from concurrent.futures import ThreadPoolExecutor
import threading
import traceback

router = APIRouter()
executor = ThreadPoolExecutor(max_workers=4)

class VagaProcessingRegistry:
    _instance = None
    _lock = threading.Lock()
    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance.processing_ids = set()
                    cls._instance.processing_lock = threading.Lock()
        return cls._instance

    def is_processing(self, vaga_id):
        with self.processing_lock:
            return vaga_id in self.processing_ids

    def start_processing(self, vaga_id):
        with self.processing_lock:
            if vaga_id in self.processing_ids:
                return False
            self.processing_ids.add(vaga_id)
            return True

    def finish_processing(self, vaga_id):
        with self.processing_lock:
            self.processing_ids.discard(vaga_id)

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
