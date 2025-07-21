from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from app.models.match_prospect import MatchProspect
from app.models.processed_applicant import ProcessedApplicant
from app.models.workbook import Workbook
from app.models.vaga import Vaga
from app.schemas.prospects_match import (
    ApplicantProspectResponse, 
    ProspectMatchByWorkbookResponse, 
    ProspectMatchByVagaResponse
)
from app.core.logging import log_info, log_error, log_warning
import json
import uuid

class ProspectsMatchService:
    def __init__(self, db: Session):
        self.db = db
    
    def _convert_to_applicant_prospect_response(self, match_prospect: MatchProspect, applicant: ProcessedApplicant) -> ApplicantProspectResponse:
        """Converte os dados do match_prospect e processed_applicant para o response schina"""
        
        # Processar cv_pt_json se existir
        cv_pt_data = None
        if applicant.cv_pt_json:
            if isinstance(applicant.cv_pt_json, str):
                try:
                    cv_pt_data = json.loads(applicant.cv_pt_json)
                except json.JSONDecodeError:
                    cv_pt_data = None
            else:
                cv_pt_data = applicant.cv_pt_json
        
        return ApplicantProspectResponse(
            # Dados do match_prospect
            workbook_id=str(match_prospect.workbook_id),
            applicant_id=match_prospect.applicant_id,
            score_semantico=match_prospect.score_semantico,
            origem=match_prospect.origem,
            selecionado=match_prospect.selecionado,
            data_entrada=match_prospect.data_entrada,
            observacoes=match_prospect.observacoes,
            
            # Dados do processed_applicant
            nome=applicant.nome,
            email=applicant.email,
            cpf=applicant.cpf,
            telefone_celular=applicant.telefone_celular,
            nivel_maximo_formacao=applicant.nivel_maximo_formacao,
            cv_pt=cv_pt_data,
            updated_at=applicant.updated_at
        )
    
    def get_prospects_by_workbook_id(self, workbook_id: str) -> Optional[ProspectMatchByWorkbookResponse]:
        """
        Busca todos os prospects (processed_applicants) associados a um workbook através da tabela match_prospects
        """
        try:
            # Validar UUID
            try:
                workbook_uuid = uuid.UUID(workbook_id)
            except ValueError:
                log_error(f"Invalid UUID for workbook: {workbook_id}")
                return None
            
            # Search workbook to get job information
            workbook = self.db.query(Workbook).filter(Workbook.id == workbook_uuid).first()
            if not workbook:
                log_warning(f"Workbook not found: {workbook_id}")
                return None
            
            # Buscar título da vaga
            vaga = self.db.query(Vaga).filter(Vaga.id == workbook.vaga_id).first()
            vaga_titulo = vaga.informacoes_basicas_titulo_vaga if vaga else None
            
            # Buscar match_prospects com seus applicants relacionados
            query = self.db.query(MatchProspect, ProcessedApplicant).join(
                ProcessedApplicant, 
                MatchProspect.applicant_id == ProcessedApplicant.id
            ).filter(
                MatchProspect.workbook_id == workbook_uuid
            )
            
            results = query.all()
            
            if not results:
                log_warning(f"No prospects found for workbook: {workbook_id}")
                return None
            
            prospects_list = []
            for match_prospect, applicant in results:
                prospect_response = self._convert_to_applicant_prospect_response(match_prospect, applicant)
                prospects_list.append(prospect_response)
            
            log_info(f"Found {len(prospects_list)} prospects for workbook {workbook_id}")
            
            return ProspectMatchByWorkbookResponse(
                workbook_id=workbook_id,
                vaga_id=workbook.vaga_id,
                vaga_titulo=vaga_titulo,
                prospects=prospects_list,
                total_prospects=len(prospects_list)
            )
            
        except Exception as e:
            log_error(f"Error fetching prospects for workbook {workbook_id}: {str(e)}")
            return None
    
    def get_prospects_by_vaga_id(self, vaga_id: int) -> Optional[ProspectMatchByVagaResponse]:
        """
        Busca todos os prospects (processed_applicants) associados a uma vaga através de todos os workbooks da vaga
        """
        try:
            # Buscar título da vaga
            vaga = self.db.query(Vaga).filter(Vaga.id == vaga_id).first()
            if not vaga:
                log_warning(f"Job not found: {vaga_id}")
                return None
            
            vaga_titulo = vaga.informacoes_basicas_titulo_vaga
            
            # Buscar todos os workbooks desta vaga
            workbooks = self.db.query(Workbook).filter(Workbook.vaga_id == vaga_id).all()
            
            if not workbooks:
                log_warning(f"No workbooks found for job: {vaga_id}")
                return None
            
            workbooks_data = []
            total_prospects = 0
            
            for workbook in workbooks:
                # Search prospects for each workbook
                workbook_prospects = self.get_prospects_by_workbook_id(str(workbook.id))
                if workbook_prospects:
                    workbooks_data.append(workbook_prospects)
                    total_prospects += workbook_prospects.total_prospects
            
            if not workbooks_data:
                log_warning(f"No prospects found for job: {vaga_id}")
                return None
            
            log_info(f"Found {total_prospects} total prospects for job {vaga_id} in {len(workbooks_data)} workbooks")
            
            return ProspectMatchByVagaResponse(
                vaga_id=vaga_id,
                vaga_titulo=vaga_titulo,
                workbooks=workbooks_data,
                total_prospects=total_prospects
            )
            
        except Exception as e:
            log_error(f"Error fetching prospects for job {vaga_id}: {str(e)}")
            return None
    
    def search_prospects_by_name(self, name: str, limit: int = 50) -> List[ApplicantProspectResponse]:
        """
        Busca prospects por nome do applicant
        """
        try:
            name_lower = name.lower().strip()
            
            if len(name_lower) < 2:
                log_warning("Nome de busca muito curto (mínimo 2 caracteres)")
                return []
            
            # Buscar match_prospects com applicants cujo nome contenha o termo
            query = self.db.query(MatchProspect, ProcessedApplicant).join(
                ProcessedApplicant, 
                MatchProspect.applicant_id == ProcessedApplicant.id
            ).filter(
                ProcessedApplicant.nome.ilike(f"%{name}%")
            ).limit(limit)
            
            results = query.all()
            
            prospects_list = []
            for match_prospect, applicant in results:
                prospect_response = self._convert_to_applicant_prospect_response(match_prospect, applicant)
                prospects_list.append(prospect_response)
            
            log_info(f"Found {len(prospects_list)} prospects com nome contendo '{name}'")
            return prospects_list
            
        except Exception as e:
            log_error(f"Erro ao buscar prospects por nome '{name}': {str(e)}")
            return []
    
    def get_workbooks_with_prospects_summary(self) -> List[Dict[str, Any]]:
        """
        Returns a summary list of all workbooks that have prospects
        """
        try:
            # Buscar workbooks que têm match_prospects
            query = self.db.query(
                Workbook.id,
                Workbook.vaga_id,
                Vaga.informacoes_basicas_titulo_vaga,
                self.db.query(MatchProspect).filter(
                    MatchProspect.workbook_id == Workbook.id
                ).count().label('prospects_count')
            ).join(
                Vaga, Workbook.vaga_id == Vaga.id
            ).join(
                MatchProspect, MatchProspect.workbook_id == Workbook.id
            ).group_by(
                Workbook.id, Workbook.vaga_id, Vaga.informacoes_basicas_titulo_vaga
            ).having(
                self.db.query(MatchProspect).filter(
                    MatchProspect.workbook_id == Workbook.id
                ).count() > 0
            )
            
            results = query.all()
            
            workbooks_summary = []
            for workbook_id, vaga_id, vaga_titulo, prospects_count in results:
                workbooks_summary.append({
                    "workbook_id": str(workbook_id),
                    "vaga_id": vaga_id,
                    "vaga_titulo": vaga_titulo,
                    "total_prospects": prospects_count
                })
            
            log_info(f"Retornando resumo de {len(workbooks_summary)} workbooks com prospects")
            return workbooks_summary
            
        except Exception as e:
            log_error(f"Erro ao listar workbooks com prospects: {str(e)}")
            return []
