from app.models.processed_applicant import ProcessedApplicant
from app.core.database import SessionLocal
import json
from app.core.logging import log_info, log_warning, log_error, log_debug, llm_log
from datetime import datetime

class ApplicantRepository:
    def __init__(self, db_session=None):
        log_info("[Repository] Initializing ApplicantRepository")
        self.db = db_session or SessionLocal()

    def upsert_applicant(self, applicant_dict, final_json, max_education_level, cv_texto_semantico=None, cv_embedding=None, cv_embedding_vector=None):
        applicant_id = applicant_dict["id"]
        log_info(f"[Repository] Upserting applicant {applicant_id}")
        db_obj = self.db.query(ProcessedApplicant).filter_by(id=applicant_id).first()
        now = datetime.utcnow()
        if db_obj:
            log_info(f"[Repository] Updating existing applicant {applicant_id}")
            for field, value in applicant_dict.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db_obj.cv_pt_json = final_json  
            db_obj.nivel_maximo_formacao = max_education_level
            db_obj.updated_at = now
            if cv_texto_semantico is not None:
                db_obj.cv_texto_semantico = cv_texto_semantico
            if cv_embedding is not None:
                db_obj.cv_embedding = cv_embedding
            if cv_embedding_vector is not None:
                db_obj.cv_embedding_vector = json.dumps(cv_embedding_vector, ensure_ascii=False)
        else:
            log_info(f"[Repository] Creating new applicant {applicant_id}")
            model_fields = {k: v for k, v in applicant_dict.items() if k != "cv_pt" and hasattr(ProcessedApplicant, k)}
            db_obj = ProcessedApplicant(
                **model_fields,
                cv_pt_json=final_json,  
                nivel_maximo_formacao=max_education_level,
                cv_texto_semantico=cv_texto_semantico,
                cv_embedding=cv_embedding,
                cv_embedding_vector=json.dumps(cv_embedding_vector, ensure_ascii=False) if cv_embedding_vector is not None else None,
                updated_at=now,
            )
            self.db.add(db_obj)
        self.db.commit()
        log_info(f"[Repository] Upsert committed for applicant {applicant_id}")
        return db_obj

    def get_applicant(self, applicant_id):
        log_info(f"[Repository] Getting applicant {applicant_id}")
        return self.db.query(ProcessedApplicant).filter_by(id=applicant_id).first()

    def close(self):
        log_info("[Repository] Closing DB session")
        self.db.close()
