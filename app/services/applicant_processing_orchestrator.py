from app.services.cv_extractor_service import process_single_applicant
from app.repositories.applicant_repository import ApplicantRepository
from app.core.logging import log_info, log_warning, log_error, log_debug, llm_log
from app.services.cv_semantic_service import CVSemanticService

class ApplicantProcessingOrchestrator:
    def __init__(self):
        log_info("[Orchestrator] Initializing ApplicantProcessingOrchestrator (semantic step skipped)")

    def process_applicant(self, applicant_dict):
        applicant_id = applicant_dict["id"]
        log_info(f"[Orchestrator] Starting process_applicant for applicant {applicant_id}")
        # Step 1: Run CV extractor and get cv_pt_json
        log_info(f"[Orchestrator] Calling process_single_applicant for applicant {applicant_id}")
        final_json, max_education_level = process_single_applicant(applicant_dict)
        log_info(f"[Orchestrator] process_single_applicant returned for applicant {applicant_id}")
        if not final_json:
            log_error(f"[Orchestrator] CV extraction failed for applicant {applicant_id}")
            return {"status": "error", "message": "CV extraction failed", "id": applicant_id}

        # Step 2: Process semantic fields (cv_texto_semantico, cv_embedding, cv_embedding_vector)
        semantic_service = CVSemanticService()
        semantic_result = semantic_service.process(final_json)
        # Step 3: Upsert all results in the DB
        log_info(f"[Orchestrator] Calling ApplicantRepository.upsert_applicant for applicant {applicant_id}")
        repo = ApplicantRepository()
        db_obj = repo.upsert_applicant(
            applicant_dict,
            final_json,
            max_education_level,
            cv_texto_semantico=semantic_result.get("cv_texto_semantico"),
            cv_embedding=semantic_result.get("cv_embedding"),
            cv_embedding_vector=semantic_result.get("cv_embedding_vector"),
        )
        log_info(f"[Orchestrator] ApplicantRepository.upsert_applicant finished for applicant {applicant_id}")
        return {
            "status": "ok",
            "id": applicant_id,
            "max_education_level": max_education_level,
            "cv_json": final_json
        }
