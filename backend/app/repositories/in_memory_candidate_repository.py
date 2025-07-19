from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.logging import log_info, log_error
import json


class InMemoryCandidateRepository:
    """
    Repository para trabalhar com candidatos em memória (sem usar match_prospects)
    Usado durante o chat antes de finalizar/salvar
    """
    
    def __init__(self, db: Session):
        self.db = db
        # Cache em memória para candidatos filtrados por sessão
        self._session_candidates: Dict[str, List[Dict]] = {}
    
    def execute_candidate_query(self, query: str, params: Dict[str, Any]) -> List[Dict]:
        """
        Executa query de candidatos direto na tabela processed_applicants
        
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
    
    def get_session_candidates(self, session_id: str) -> List[Dict]:
        """
        Busca candidatos salvos na sessão (em memória)
        
        Args:
            session_id: ID da sessão de chat
            
        Returns:
            Lista de candidatos da sessão ou lista vazia se não houver
        """
        candidates = self._session_candidates.get(session_id, [])
        log_info(f"Encontrados {len(candidates)} candidatos na sessão {session_id}")
        return candidates
    
    def save_session_candidates(self, session_id: str, candidates: List[Dict], mode: str = 'incremental'):
        """
        Salva candidatos na sessão (em memória)
        
        Args:
            session_id: ID da sessão de chat
            candidates: Lista de candidatos
            mode: 'incremental' ou 'reset'
        """
        try:
            if mode == 'reset' or session_id not in self._session_candidates:
                self._session_candidates[session_id] = candidates
                log_info(f"Reset: salvos {len(candidates)} candidatos na sessão {session_id}")
            else:
                # Modo incremental: combina com candidatos existentes
                existing = self._session_candidates[session_id]
                existing_ids = {c['id'] for c in existing}
                
                # Adiciona apenas candidatos novos
                new_candidates = [c for c in candidates if c['id'] not in existing_ids]
                self._session_candidates[session_id].extend(new_candidates)
                
                total = len(self._session_candidates[session_id])
                log_info(f"Incremental: adicionados {len(new_candidates)} novos candidatos. Total na sessão: {total}")
                
        except Exception as e:
            log_error(f"Erro ao salvar candidatos na sessão: {str(e)}")
    
    def clear_session_candidates(self, session_id: str):
        """
        Limpa candidatos da sessão
        """
        if session_id in self._session_candidates:
            del self._session_candidates[session_id]
            log_info(f"Candidatos da sessão {session_id} foram limpos")
    
    def get_vaga_data(self, workbook_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca dados da vaga através do workbook
        """
        try:
            import uuid
            from app.models.workbook import Workbook
            from app.models.vaga import Vaga
            
            # Converte workbook_id para UUID se necessário
            if isinstance(workbook_id, str):
                workbook_uuid = uuid.UUID(workbook_id)
            else:
                workbook_uuid = workbook_id
            
            # Busca workbook
            workbook = self.db.query(Workbook).filter(Workbook.id == workbook_uuid).first()
            if not workbook:
                log_error(f"Workbook não encontrado: {workbook_id}")
                return None
            
            # Busca vaga
            vaga = self.db.query(Vaga).filter(Vaga.id == workbook.vaga_id).first()
            if not vaga:
                log_error(f"Vaga não encontrada para workbook: {workbook_id}")
                return None
            
            return {
                'id': vaga.id,
                'titulo': getattr(vaga, 'informacoes_basicas_titulo_vaga', 'N/A'),
                'workbook_id': workbook_id
            }
            
        except Exception as e:
            log_error(f"Erro ao buscar dados da vaga: {str(e)}")
            return None
    
    def _process_candidate_results(self, candidates_raw) -> List[Dict]:
        """
        Processa resultados raw da query em formato padronizado
        """
        candidates = []
        
        for row in candidates_raw:
            try:
                # Converte row para dict se necessário
                if hasattr(row, '_mapping'):
                    row_dict = dict(row._mapping)
                else:
                    # Para resultados de text() query
                    row_dict = dict(row)
                
                # Processa CV JSON se presente
                cv_data = {}
                if 'cv_pt_json' in row_dict and row_dict['cv_pt_json']:
                    try:
                        if isinstance(row_dict['cv_pt_json'], str):
                            cv_data = json.loads(row_dict['cv_pt_json'])
                        else:
                            cv_data = row_dict['cv_pt_json']
                    except (json.JSONDecodeError, TypeError):
                        cv_data = {}
                
                candidate = {
                    'id': row_dict.get('id') or row_dict.get('processed_applicants_id'),
                    'nome': row_dict.get('nome') or row_dict.get('processed_applicants_nome'),
                    'email': row_dict.get('email') or row_dict.get('processed_applicants_email'),
                    'endereco': row_dict.get('endereco') or row_dict.get('processed_applicants_endereco'),
                    'nivel_maximo_formacao': row_dict.get('nivel_maximo_formacao') or row_dict.get('processed_applicants_nivel_maximo_formacao'),
                    'cv_pt': cv_data,
                    'score_semantico': row_dict.get('distancia', 0.0),  # distancia é o score semântico
                    'cv_texto_semantico': row_dict.get('cv_texto_semantico', ''),
                    'updated_at': row_dict.get('updated_at')
                }
                
                candidates.append(candidate)
                
            except Exception as e:
                log_error(f"Erro ao processar candidato: {str(e)}")
                continue
        
        log_info(f"Processados {len(candidates)} candidatos com sucesso")
        return candidates
