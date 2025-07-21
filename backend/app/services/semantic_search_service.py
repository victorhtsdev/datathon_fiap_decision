from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.logging import log_info, log_error
import json


class SemanticSearchService:
    """
    Serviço específico para busca semântica SQL com PostgreSQL.
    Extrai a lógica complexa de consulta SQL do handler de chat.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def execute_semantic_search(
        self, 
        workbook_id: str, 
        criteria: Dict[str, Any], 
        limit: int = 10
    ) -> List[Dict]:
        """
        Executa consulta SQL semântica baseada nos critérios extraídos
        """
        try:
            # Busca dados da vaga através do workbook
            vaga_data = self._get_vaga_data(workbook_id)
            if not vaga_data:
                log_error("Não foi possível obter dados da vaga")
                return []
            
            # Determina qual vaga usar (do criteria ou do workbook)
            vaga_id = criteria.get('vaga_id') or vaga_data.get('id')
            if not vaga_id:
                log_error("Não foi possível determinar ID da vaga")
                return []
            
            # Monta a consulta base - SEMPRE com similaridade semântica
            filtros = criteria.get('filtros', {})
            
            # Consulta SEMPRE com similaridade semântica
            query_parts = [
                "SELECT pa.id, pa.nome, pa.email, pa.endereco, pa.nivel_maximo_formacao,",
                "       pa.cv_pt_json, pa.cv_texto_semantico, pa.updated_at,",
                "       pa.cv_embedding_vector <=> v.vaga_embedding_vector AS distancia",
                "FROM processed_applicants pa, vagas v",
                "WHERE v.id = :vaga_id",
                "  AND pa.cv_embedding_vector IS NOT NULL",
                "  AND v.vaga_embedding_vector IS NOT NULL"
            ]
            
            # Adiciona filtros específicos
            params = {"vaga_id": vaga_id}
            
            # Aplica filtros específicos
            self._apply_language_filters(query_parts, params, filtros)
            self._apply_skills_filters(query_parts, params, filtros)
            self._apply_education_filters(query_parts, params, filtros)
            self._apply_location_filters(query_parts, params, filtros)
            self._apply_gender_filters(query_parts, params, filtros)
            
            # Ordenação e limite - SEMPRE por similaridade semântica
            query_parts.append("ORDER BY distancia ASC")
            query_parts.append(f"LIMIT {limit}")
            
            # Executa a consulta
            final_query = "\n".join(query_parts)
            log_info(f"Executando consulta SQL: {final_query}")
            log_info(f"Parâmetros: {params}")
            
            result = self.db.execute(text(final_query), params)
            candidates_raw = result.fetchall()
            
            # Processa resultados
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
                        'origin': 'sql_query_semantico'
                    }
                    candidates.append(candidate_dict)
                    
                except Exception as e:
                    log_error(f"Erro ao processar candidato {candidate.id}: {str(e)}")
                    continue
            
            log_info(f"Consulta SQL processou {len(candidates)} candidatos")
            return candidates
            
        except Exception as e:
            log_error(f"Erro na execução da consulta SQL: {str(e)}")
            return []
    
    def _apply_language_filters(self, query_parts: List[str], params: Dict, filtros: Dict):
        """Aplica filtros de idiomas com hierarquia de níveis"""
        if not filtros.get('idiomas'):
            return
            
        idiomas_conditions = []
        for idioma_req in filtros['idiomas']:
            idioma_nome = idioma_req.get('idioma', '').lower()
            nivel_minimo = idioma_req.get('nivel_minimo', '').lower()
            incluir_superiores = idioma_req.get('incluir_superiores', True)
            
            if idioma_nome and nivel_minimo:
                # Define hierarquia de níveis
                hierarquia_niveis = {
                    'básico': ['básico', 'intermediário', 'avançado', 'fluente'],
                    'basico': ['básico', 'intermediário', 'avançado', 'fluente'],
                    'intermediário': ['intermediário', 'avançado', 'fluente'],
                    'intermediario': ['intermediário', 'avançado', 'fluente'],
                    'avançado': ['avançado', 'fluente'],
                    'avancado': ['avançado', 'fluente'],
                    'fluente': ['fluente']
                }
                
                if incluir_superiores and nivel_minimo in hierarquia_niveis:
                    # Inclui o nível mínimo e todos os superiores
                    niveis_aceitos = hierarquia_niveis[nivel_minimo]
                else:
                    # Apenas o nível específico
                    niveis_aceitos = [nivel_minimo]
                
                # Monta condições OR para todos os níveis aceitos
                nivel_conditions = []
                for nivel in niveis_aceitos:
                    # Busca por variações do nível (com e sem acentos)
                    nivel_patterns = []
                    if nivel == 'básico':
                        nivel_patterns = ['básico', 'basico', 'basic']
                    elif nivel == 'intermediário':
                        nivel_patterns = ['intermediário', 'intermediario', 'intermediate']
                    elif nivel == 'avançado':
                        nivel_patterns = ['avançado', 'avancado', 'advanced']
                    elif nivel == 'fluente':
                        nivel_patterns = ['fluente', 'fluent']
                    else:
                        nivel_patterns = [nivel]
                    
                    for pattern in nivel_patterns:
                        nivel_conditions.append(f"@.nivel like_regex \"{pattern}\" flag \"i\"")
                
                nivel_query = f"({' || '.join(nivel_conditions)})"
                
                idiomas_conditions.append(
                    f"jsonb_path_exists(pa.cv_pt_json, "
                    f"'$.idiomas[*] ? (@.idioma like_regex \"{idioma_nome}\" flag \"i\" && {nivel_query})')"
                )
            
            # Suporte para múltiplos níveis (formato antigo - compatibilidade)
            elif 'niveis' in idioma_req and idioma_req['niveis']:
                niveis = [nivel.lower() for nivel in idioma_req['niveis']]
                nivel_conditions = []
                for nivel in niveis:
                    nivel_conditions.append(f"@.nivel like_regex \"{nivel}\" flag \"i\"")
                nivel_query = f"({' || '.join(nivel_conditions)})"
                
                idiomas_conditions.append(
                    f"jsonb_path_exists(pa.cv_pt_json, "
                    f"'$.idiomas[*] ? (@.idioma like_regex \"{idioma_nome}\" flag \"i\" && {nivel_query})')"
                )
            
            # Suporte para formato antigo (compatibilidade)
            elif 'nivel' in idioma_req and idioma_req['nivel']:
                idioma_nivel = idioma_req['nivel'].lower()
                idiomas_conditions.append(
                    f"jsonb_path_exists(pa.cv_pt_json, "
                    f"'$.idiomas[*] ? (@.idioma like_regex \"{idioma_nome}\" flag \"i\" && "
                    f"@.nivel like_regex \"{idioma_nivel}\" flag \"i\")')"
                )
            
            # Se só tem idioma sem nível específico
            elif idioma_nome:
                idiomas_conditions.append(
                    f"jsonb_path_exists(pa.cv_pt_json, "
                    f"'$.idiomas[*] ? (@.idioma like_regex \"{idioma_nome}\" flag \"i\")')"
                )
        
        if idiomas_conditions:
            query_parts.append(f"  AND ({' OR '.join(idiomas_conditions)})")
    
    def _apply_skills_filters(self, query_parts: List[str], params: Dict, filtros: Dict):
        """Aplica filtros de habilidades"""
        if not filtros.get('habilidades'):
            return
            
        habilidades_conditions = []
        for habilidade in filtros['habilidades']:
            habilidade_clean = habilidade.lower().strip()
            if habilidade_clean:
                habilidades_conditions.append(
                    f"jsonb_path_exists(pa.cv_pt_json, "
                    f"'$.habilidades[*] ? (@ like_regex \"{habilidade_clean}\" flag \"i\")')"
                )
        
        if habilidades_conditions:
            query_parts.append(f"  AND ({' OR '.join(habilidades_conditions)})")
    
    def _apply_education_filters(self, query_parts: List[str], params: Dict, filtros: Dict):
        """Aplica filtros de formação"""
        if not filtros.get('formacao'):
            return
            
        formacao = filtros['formacao']
        if formacao.get('nivel'):
            nivel = formacao['nivel'].lower()
            query_parts.append(
                f"  AND jsonb_path_exists(pa.cv_pt_json, "
                f"'$.formacoes[*] ? (@.nivel like_regex \"{nivel}\" flag \"i\")')"
            )
        
        if formacao.get('curso'):
            curso = formacao['curso'].lower()
            query_parts.append(
                f"  AND jsonb_path_exists(pa.cv_pt_json, "
                f"'$.formacoes[*] ? (@.curso like_regex \"{curso}\" flag \"i\")')"
            )
    
    def _apply_location_filters(self, query_parts: List[str], params: Dict, filtros: Dict):
        """Aplica filtros de localização"""
        if not filtros.get('localizacao'):
            return
            
        localizacao = filtros['localizacao'].lower()
        query_parts.append("  AND LOWER(pa.endereco) LIKE :localizacao")
        params['localizacao'] = f'%{localizacao}%'
    
    def _apply_gender_filters(self, query_parts: List[str], params: Dict, filtros: Dict):
        """Aplica filtros de sexo"""
        if not filtros.get('sexo'):
            return
            
        sexo = filtros['sexo'].lower()
        query_parts.append("  AND LOWER(pa.sexo) = :sexo")
        params['sexo'] = sexo
    
    def _get_vaga_data(self, workbook_id: str) -> Optional[Dict]:
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
            
            vaga_data = {
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
            
            return vaga_data
            
        except Exception as e:
            log_error(f"Erro ao buscar dados da vaga: {str(e)}")
            return None
    
    def save_filtered_candidates(self, workbook_id: str, candidates: List[Dict]):
        """Salva candidatos filtrados como match_prospects"""
        try:
            from app.models.match_prospect import MatchProspect
            
            # Rinove match_prospects existentes
            self.db.query(MatchProspect).filter(
                MatchProspect.workbook_id == workbook_id
            ).delete()
            
            # Adiciona novos match_prospects
            for candidate in candidates:
                match_prospect = MatchProspect(
                    workbook_id=workbook_id,
                    applicant_id=candidate['id'],
                    score_semantico=candidate.get('score_semantico', 0.5),
                    origem=candidate.get('origin', 'sql_query'),
                    selecionado=False
                )
                self.db.add(match_prospect)
            
            self.db.commit()
            log_info(f"Saved {len(candidates)} match_prospects via SQL para workbook {workbook_id}")
            
        except Exception as e:
            log_error(f"Erro ao salvar match_prospects: {str(e)}")
            self.db.rollback()
