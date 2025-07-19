from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.logging import log_info, log_error
import json

class CandidateRepository:
    """
    Repository responsável por operações de acesso a dados de candidatos
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def execute_candidate_query(self, query: str, params: Dict[str, Any]) -> List[Dict]:
        """
        Executa query de candidatos e retorna resultados processados
        
        Args:
            query: Query SQL para executar
            params: Parâmetros da query
            
        Returns:
            Lista de candidatos processados
        """
        try:
            log_info(f"Executando query: {query}")
            log_info(f"Parâmetros: {params}")
            
            result = self.db.execute(text(query), params)
            candidates_raw = result.fetchall()
            
            return self._process_candidate_results(candidates_raw)
            
        except Exception as e:
            log_error(f"Erro ao executar query de candidatos: {str(e)}")
            return []
    
    def get_current_workbook_candidates(self, workbook_id: str) -> List[Dict]:
        """
        Busca candidatos atualmente ativos no workbook
        
        Args:
            workbook_id: ID do workbook
            
        Returns:
            Lista de candidatos ativos
        """
        try:
            from app.models.match_prospect import MatchProspect
            from app.models.processed_applicant import ProcessedApplicant
            
            query = self.db.query(
                ProcessedApplicant.id,
                ProcessedApplicant.nome,
                ProcessedApplicant.email,
                ProcessedApplicant.endereco,
                ProcessedApplicant.nivel_maximo_formacao,
                ProcessedApplicant.cv_pt_json,
                MatchProspect.score_semantico
            ).join(
                MatchProspect, 
                ProcessedApplicant.id == MatchProspect.applicant_id
            ).filter(
                MatchProspect.workbook_id == workbook_id,
                MatchProspect.is_active == True
            )
            
            results = query.all()
            
            candidates = []
            for result in results:
                cv_data = result.cv_pt_json
                if isinstance(cv_data, str):
                    cv_data = json.loads(cv_data)
                
                candidates.append({
                    'id': result.id,
                    'nome': result.nome,
                    'email': result.email,
                    'endereco': result.endereco,
                    'nivel_maximo_formacao': result.nivel_maximo_formacao,
                    'cv_pt': cv_data,
                    'score_semantico': result.score_semantico
                })
            
            log_info(f"Encontrados {len(candidates)} candidatos ativos no workbook")
            return candidates
            
        except Exception as e:
            log_error(f"Erro ao buscar candidatos do workbook: {str(e)}")
            return []
    
    def save_match_prospects(self, workbook_id: str, candidates: List[Dict], mode: str = 'incremental'):
        """
        Salva candidatos como match_prospects
        
        Args:
            workbook_id: ID do workbook
            candidates: Lista de candidatos
            mode: 'incremental' ou 'reset'
        """
        try:
            from app.models.match_prospect import MatchProspect
            
            if mode == 'reset':
                # Remove todos os match_prospects existentes
                self.db.query(MatchProspect).filter(
                    MatchProspect.workbook_id == workbook_id
                ).delete()
                log_info(f"Removidos match_prospects existentes (modo reset)")
            else:
                # Modo incremental: desativa os atuais
                self.db.query(MatchProspect).filter(
                    MatchProspect.workbook_id == workbook_id
                ).update({"is_active": False})
                log_info(f"Desativados match_prospects existentes (modo incremental)")
            
            # Determina o próximo step
            filter_step = self._get_next_filter_step(workbook_id)
            
            # Adiciona novos match_prospects
            for candidate in candidates:
                match_prospect = MatchProspect(
                    workbook_id=workbook_id,
                    applicant_id=candidate['id'],
                    score_semantico=candidate.get('score_semantico', 0.5),
                    origem=candidate.get('origem', 'sql_query'),
                    selecionado=False,
                    filter_step_added=filter_step,
                    is_active=True
                )
                self.db.add(match_prospect)
            
            self.db.commit()
            log_info(f"Salvos {len(candidates)} match_prospects (step {filter_step})")
            
        except Exception as e:
            log_error(f"Erro ao salvar match_prospects: {str(e)}")
            self.db.rollback()
    
    def get_vaga_data(self, workbook_id: str) -> Optional[Dict]:
        """Busca dados da vaga através do workbook"""
        try:
            from app.repositories.workbook_repository import WorkbookRepository
            from app.models.vaga import Vaga
            
            workbook_repo = WorkbookRepository(self.db)
            workbook = workbook_repo.get_workbook(workbook_id)
            
            if not workbook:
                return None
            
            vaga = self.db.query(Vaga).filter(Vaga.id == workbook.vaga_id).first()
            if not vaga:
                return None
            
            return {
                'id': vaga.id,
                'titulo': vaga.informacoes_basicas_titulo_vaga,
                'texto_semantico': vaga.vaga_texto_semantico,
                'embedding_vector': vaga.vaga_embedding_vector,
                'principais_atividades': vaga.perfil_vaga_principais_atividades,
                'competencias': vaga.perfil_vaga_competencia_tecnicas_e_comportamentais,
                'areas_atuacao': vaga.perfil_vaga_areas_atuacao,
                'nivel_profissional': vaga.perfil_vaga_nivel_profissional,
                'nivel_academico': vaga.perfil_vaga_nivel_academico
            }
            
        except Exception as e:
            log_error(f"Erro ao buscar dados da vaga: {str(e)}")
            return None
    
    def _process_candidate_results(self, candidates_raw) -> List[Dict]:
        """Processa resultados brutos da query e converte para formato padrão"""
        candidates = []
        for candidate in candidates_raw:
            try:
                cv_data = candidate.cv_pt_json
                if isinstance(cv_data, str):
                    cv_data = json.loads(cv_data)
                
                candidate_dict = {
                    'id': candidate.id,
                    'nome': candidate.nome,
                    'email': candidate.email,
                    'endereco': candidate.endereco,
                    'nivel_maximo_formacao': candidate.nivel_maximo_formacao,
                    'cv_pt': cv_data,
                    'score_semantico': float(1 - candidate.distancia),
                    'distancia': float(candidate.distancia),
                    'origem': 'sql_query_semantic'
                }
                candidates.append(candidate_dict)
                
            except Exception as e:
                log_error(f"Erro ao processar candidato {candidate.id}: {str(e)}")
                continue
        
        log_info(f"Processados {len(candidates)} candidatos")
        return candidates
    
    def _get_next_filter_step(self, workbook_id: str) -> int:
        """Determina o próximo step do filtro"""
        try:
            from app.models.match_prospect import MatchProspect
            
            result = self.db.query(MatchProspect.filter_step_added).filter(
                MatchProspect.workbook_id == workbook_id
            ).order_by(MatchProspect.filter_step_added.desc()).first()
            
            return (result.filter_step_added + 1) if result else 1
            
        except Exception as e:
            log_error(f"Erro ao determinar próximo step: {str(e)}")
            return 1
