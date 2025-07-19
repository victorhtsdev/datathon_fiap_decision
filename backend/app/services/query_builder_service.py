from typing import Dict, Any, List, Tuple
from app.core.logging import log_info, log_error

class QueryBuilderService:
    """
    Service responsável por construir queries SQL baseadas em critérios extraídos
    """
    
    def build_semantic_query(
        self, 
        vaga_id: int, 
        filtros: Dict[str, Any], 
        limit: int = 20,
        candidate_ids: List[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Constrói query SQL com filtros semânticos
        
        Args:
            vaga_id: ID da vaga
            filtros: Filtros extraídos pelo LLM
            limit: Limite de resultados
            candidate_ids: IDs específicos de candidatos (para filtro incremental)
            
        Returns:
            Tupla com (query_string, parameters)
        """
        try:
            query_parts = self._build_base_query()
            params = {"vaga_id": vaga_id}
            
            # Restringe a candidatos específicos se fornecido (modo incremental)
            if candidate_ids:
                candidate_ids_str = ','.join(candidate_ids)
                query_parts.append(f"  AND pa.id IN ({candidate_ids_str})")
                log_info(f"Query restrita a {len(candidate_ids)} candidatos específicos")
            
            # Adiciona filtros específicos
            self._add_filter_conditions(query_parts, params, filtros)
            
            # Finaliza query
            query_parts.extend([
                "ORDER BY distancia ASC",
                f"LIMIT {limit}"
            ])
            
            final_query = "\n".join(query_parts)
            log_info(f"Query construída com {len(filtros)} tipos de filtros")
            
            return final_query, params
            
        except Exception as e:
            log_error(f"Erro ao construir query: {str(e)}")
            return "", {}
    
    def _build_base_query(self) -> List[str]:
        """Constrói a parte base da query"""
        return [
            "SELECT pa.id, pa.nome, pa.email, pa.endereco, pa.nivel_maximo_formacao,",
            "       pa.cv_pt_json, pa.cv_texto_semantico, pa.updated_at,",
            "       pa.cv_embedding_vector <=> v.vaga_embedding_vector AS distancia",
            "FROM processed_applicants pa, vagas v",
            "WHERE v.id = :vaga_id",
            "  AND pa.cv_embedding_vector IS NOT NULL",
            "  AND v.vaga_embedding_vector IS NOT NULL"
        ]
    
    def _add_filter_conditions(self, query_parts: List[str], params: Dict, filtros: Dict[str, Any]):
        """Adiciona todas as condições de filtro à query"""
        self._add_language_filters(query_parts, filtros)
        self._add_skill_filters(query_parts, filtros)
        self._add_education_filters(query_parts, filtros)
        self._add_location_filters(query_parts, params, filtros)
        self._add_gender_filters(query_parts, params, filtros)
    
    def _add_language_filters(self, query_parts: List[str], filtros: Dict[str, Any]):
        """Adiciona filtros de idiomas com hierarquia de níveis"""
        if not filtros.get('idiomas'):
            return
            
        idiomas_conditions = []
        for idioma_req in filtros['idiomas']:
            condition = self._build_language_condition(idioma_req)
            if condition:
                idiomas_conditions.append(condition)
        
        if idiomas_conditions:
            query_parts.append(f"  AND ({' OR '.join(idiomas_conditions)})")
    
    def _build_language_condition(self, idioma_req: Dict[str, Any]) -> str:
        """Constrói condição SQL para um idioma específico"""
        idioma_nome = idioma_req.get('idioma', '').lower()
        nivel_minimo = idioma_req.get('nivel_minimo', '').lower()
        incluir_superiores = idioma_req.get('incluir_superiores', True)
        
        if not idioma_nome:
            return ""
        
        if nivel_minimo:
            nivel_conditions = self._get_level_conditions(nivel_minimo, incluir_superiores)
            nivel_query = f"({' || '.join(nivel_conditions)})"
            
            return (
                f"jsonb_path_exists(pa.cv_pt_json, "
                f"'$.idiomas[*] ? (@.idioma like_regex \"{idioma_nome}\" flag \"i\" && {nivel_query})')"
            )
        else:
            return (
                f"jsonb_path_exists(pa.cv_pt_json, "
                f"'$.idiomas[*] ? (@.idioma like_regex \"{idioma_nome}\" flag \"i\")')"
            )
    
    def _get_level_conditions(self, nivel_minimo: str, incluir_superiores: bool) -> List[str]:
        """Retorna condições de nível baseadas na hierarquia"""
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
            niveis_aceitos = hierarquia_niveis[nivel_minimo]
        else:
            niveis_aceitos = [nivel_minimo]
        
        conditions = []
        for nivel in niveis_aceitos:
            patterns = self._get_level_patterns(nivel)
            for pattern in patterns:
                conditions.append(f"@.nivel like_regex \"{pattern}\" flag \"i\"")
        
        return conditions
    
    def _get_level_patterns(self, nivel: str) -> List[str]:
        """Retorna padrões de busca para um nível específico"""
        patterns_map = {
            'básico': ['básico', 'basico', 'basic'],
            'intermediário': ['intermediário', 'intermediario', 'intermediate'],
            'avançado': ['avançado', 'avancado', 'advanced'],
            'fluente': ['fluente', 'fluent']
        }
        return patterns_map.get(nivel, [nivel])
    
    def _add_skill_filters(self, query_parts: List[str], filtros: Dict[str, Any]):
        """Adiciona filtros de habilidades"""
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
    
    def _add_education_filters(self, query_parts: List[str], filtros: Dict[str, Any]):
        """Adiciona filtros de formação"""
        formacao = filtros.get('formacao')
        if not formacao:
            return
            
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
    
    def _add_location_filters(self, query_parts: List[str], params: Dict, filtros: Dict[str, Any]):
        """Adiciona filtros de localização"""
        if filtros.get('localizacao'):
            localizacao = filtros['localizacao'].lower()
            query_parts.append("  AND LOWER(pa.endereco) LIKE :localizacao")
            params['localizacao'] = f'%{localizacao}%'
    
    def _add_gender_filters(self, query_parts: List[str], params: Dict, filtros: Dict[str, Any]):
        """Adiciona filtros de sexo"""
        if filtros.get('sexo'):
            sexo = filtros['sexo'].lower()
            query_parts.append("  AND LOWER(pa.sexo) = :sexo")
            params['sexo'] = sexo
