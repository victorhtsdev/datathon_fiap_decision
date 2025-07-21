from app.services.cv_extractor_service import process_single_applicant
from app.repositories.applicant_repository import ApplicantRepository
from app.core.logging import log_info, log_warning, log_error, log_debug, llm_log
from app.services.cv_semantic_service import CVSemanticService
from app.core.database import SessionLocal

class ApplicantProcessingOrchestrator:
    def __init__(self):
        log_info("[Orchestrator] Initializing ApplicantProcessingOrchestrator (semantic step skipped)")

    def process_applicant(self, applicant_dict):
        applicant_id = applicant_dict["id"]
        log_info(f"[Orchestrator] Processing applicant {applicant_id}")
        
        # ETAPA 1: Processar CV
        try:
            final_json, nivel_max_formacao = process_single_applicant(applicant_dict)
            log_info(f"[Orchestrator] CV processing completed for applicant {applicant_id}")
        except Exception as e:
            log_error(f"[Orchestrator] Error in CV processing for applicant {applicant_id}: {e}")
            return
        
        # ETAPA 2: Gerar embedding (OPCIONAL - comentado por performance)
        semantic_service = CVSemanticService()
        cv_texto_semantico = None
        cv_embedding = None
        cv_embedding_vector = None
        
        try:
            semantic_result = semantic_service.process(final_json)
            cv_texto_semantico = semantic_result.get("cv_texto_semantico")
            cv_embedding = semantic_result.get("cv_embedding")
            cv_embedding_vector = semantic_result.get("cv_embedding_vector")
            log_info(f"[Orchestrator] Semantic processing completed for applicant {applicant_id}")
        except Exception as e:
            log_warning(f"[Orchestrator] Semantic processing failed for applicant {applicant_id}: {e}")
            # Continue without semantic data
        
        # ETAPA 3: Salvar no banco
        try:
            with SessionLocal() as db:
                repository = ApplicantRepository(db)
                repository.upsert_applicant(
                    applicant_dict, 
                    final_json, 
                    nivel_max_formacao,
                    cv_texto_semantico=cv_texto_semantico,
                    cv_embedding=cv_embedding,
                    cv_embedding_vector=cv_embedding_vector
                )
            log_info(f"[Orchestrator] Successfully processed applicant {applicant_id}")
        except Exception as e:
            log_error(f"[Orchestrator] Error saving applicant {applicant_id}: {e}")
            raise
