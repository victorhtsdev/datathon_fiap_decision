from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.schemas import ApplicantIn
from app.models import ProcessedApplicant
from app.core.database import SessionLocal
from app.llm.factory import get_llm_client
from app.core.logging import logger
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import traceback
import threading
import os
from app.services.cv_extractor_service import extract_section, merge_results, ordem_niveis, VALID_NIVEIS_IDIOMA
from app.repositories.applicant_repository import ApplicantRepository
from app.services.applicant_processing_orchestrator import ApplicantProcessingOrchestrator

router = APIRouter()
executor = ThreadPoolExecutor(max_workers=4)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Singleton para controle de processamento concorrente
class ProcessingRegistry:
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

    def is_processing(self, applicant_id):
        with self.processing_lock:
            return applicant_id in self.processing_ids

    def start_processing(self, applicant_id):
        with self.processing_lock:
            if applicant_id in self.processing_ids:
                return False
            self.processing_ids.add(applicant_id)
            return True

    def finish_processing(self, applicant_id):
        with self.processing_lock:
            self.processing_ids.discard(applicant_id)

processing_registry = ProcessingRegistry()

def process_cv_in_background(applicant_dict, db_dict):
    applicant_id = applicant_dict["id"]
    logger.info(f"[BG] Iniciando processamento do applicant {applicant_id}")
    orchestrator = ApplicantProcessingOrchestrator()
    try:
        cv_text = applicant_dict["cv_pt"]
        logger.info(f"[BG] CV extraído para applicant {applicant_id}: {cv_text[:50]}...")
        if not cv_text or len(cv_text.strip()) < 30:
            logger.warning(f"Empty or too short CV for applicant {applicant_id}.")
            return
        logger.info(f"[BG] Chamando orchestrator.process_applicant para {applicant_id}")
        orchestrator.process_applicant(applicant_dict)
        logger.info(f"Applicant {applicant_id} processed successfully.")
    except Exception as e:
        logger.error(f"Error processing applicant {applicant_id}: {e}\n{traceback.format_exc()}")
    finally:
        logger.info(f"[BG] Finalizando processamento do applicant {applicant_id}")
        processing_registry.finish_processing(applicant_id)
        repo = ApplicantRepository()
        repo.close()

@router.post("/process_applicant/")
def process_applicant(applicant: ApplicantIn, background_tasks: BackgroundTasks):
    logger.info(f"[API] Recebida requisição para processar applicant: {applicant.id}")
    applicant_id = applicant.id
    if processing_registry.is_processing(applicant_id):
        logger.warning(f"Applicant {applicant_id} is already being processed.")
        return {"error": "This applicant is already being processed. Please wait until it finishes."}
    if not processing_registry.start_processing(applicant_id):
        logger.warning(f"Applicant {applicant_id} could not be marked as processing.")
        return {"error": "Failed to start processing applicant."}
    try:
        applicant_dict = applicant.dict()
        db_dict = applicant.dict()
        logger.info(f"[API] Adicionando tarefa de background para applicant {applicant_id}")
        background_tasks.add_task(executor.submit, process_cv_in_background, applicant_dict, db_dict)
        logger.info(f"[API] Tarefa de background adicionada para applicant {applicant_id}")
        return {"message": "Applicant received for processing."}
    except Exception as e:
        processing_registry.finish_processing(applicant_id)
        logger.error(f"Error receiving applicant: {e}\n{traceback.format_exc()}")
        return {"error": "Failed to receive applicant for processing."}

@router.get("/get_processed_applicant/{applicant_id}")
def get_processed_applicant(applicant_id: int):
    db = SessionLocal()
    try:
        db_obj = db.query(ProcessedApplicant).filter_by(id=applicant_id).first()
        if not db_obj:
            return {"error": "Applicant not found."}
        # Monta o dicionário com todos os campos, mas substitui cv_pt pelo json de cv_pt_json
        result = {c.name: getattr(db_obj, c.name) for c in db_obj.__table__.columns if c.name not in ["cv_texto_semantico", "cv_embedding", "cv_embedding_vector"]}
        # Remove cv_pt_json from the result, only return cv_pt with the processed JSON
        if "cv_pt_json" in result:
            del result["cv_pt_json"]
        if db_obj.cv_pt_json:
            if isinstance(db_obj.cv_pt_json, str):
                result["cv_pt"] = json.loads(db_obj.cv_pt_json)
            else:
                result["cv_pt"] = db_obj.cv_pt_json
        else:
            result["cv_pt"] = None
        # updated_at já estará presente em result, pois está no modelo
        return result
    finally:
        db.close()
