from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.llm.factory import get_llm_client
from app.core.logging import log_info, log_error
import json
import re


class SemanticCandidateService:
    """
    Serviço especializado para busca semântica de candidatos.
    Concentra toda a lógica de busca semântica e filtros SQL.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.llm_client = get_llm_client()
    
    def extract_criteria_with_llm(self, filter_text: str) -> Dict[str, Any]:
        """
        Usa LLM para extrair critérios específicos de filtro a partir de texto natural
        """
        prompt = self._build_extraction_prompt(filter_text)
        
        try:
            response = self.llm_client.extract_text(prompt)
            return self._parse_llm_response(response)
            
        except Exception as e:
            log_error(f"Erro ao extrair critérios com LLM: {str(e)}")
            return {"usar_similaridade": True, "filtros": {}}
    
    def search_candidates_semantic(
        self, 
        workbook_id: str, 
        criteria: Dict[str, Any], 
        limit: int = 20
    ) -> List[Dict]:
        """
        Executa busca semântica de candidatos baseada nos critérios extraídos
        """
        try:
            log_info(f"search_candidates_semantic chamado com limit={limit}")
            
            # Obtém dados da vaga
            vaga_data = self._get_job_data(workbook_id)
            if not vaga_data:
                log_error("Não foi possível obter dados da vaga")
                return []
            
            vaga_id = criteria.get('vaga_id') or vaga_data.get('id')
            if not vaga_id:
                log_error("Não foi possível determinar ID da vaga")
                return []
            
            log_info(f"Usando vaga_id: {vaga_id} para busca semântica com limit: {limit}")
            
            # Constrói e executa consulta SQL
            query, params = self._build_semantic_query(vaga_id, criteria, limit)
            
            log_info(f"Executando consulta semântica: {query}")
            log_info(f"Parâmetros: {params}")
            
            result = self.db.execute(text(query), params)
            candidates_raw = result.fetchall()
            
            # Processa resultados
            candidates = []
            for candidate in candidates_raw:
                try:
                    candidate_dict = self._process_candidate_row(candidate)
                    candidates.append(candidate_dict)
                except Exception as e:
                    log_error(f"Erro ao processar candidato {candidate.id}: {str(e)}")
                    continue
            
            log_info(f"Busca semântica retornou {len(candidates)} candidatos")
            return candidates
            
        except Exception as e:
            log_error(f"Erro na busca semântica: {str(e)}")
            return []
    
    def _build_extraction_prompt(self, filter_text: str) -> str:
        """Constrói prompt para extração de critérios pelo LLM"""
        
        return f"""
Analise esta solicitação de filtro de candidatos e extraia TODOS os critérios mencionados.

Solicitação: "{filter_text}"

REGRAS IMPORTANTES para LIMITE de candidatos:
- Se mencionar número específico (ex: "filtre 4", "busque 10") → use esse número
- Se for refinamento sem número (ex: "apenas os que têm inglês", "somente com Java") → use 10 como padrão
- Se for busca genérica sem número → use 20 como padrão

REGRAS para FILTROS:
- APENAS extraia critérios específicos que estão EXPLICITAMENTE mencionados
- SEMPRE use similaridade semântica (usar_similaridade: true)

Retorne APENAS um JSON válido com esta estrutura:

Para comandos com número específico:
{{
    "vaga_id": null,
    "usar_similaridade": true,
    "limite": 4,
    "filtros": {{
        "idiomas": [],
        "habilidades": [],
        "formacao": {{}},
        "experiencia": {{}},
        "localizacao": null,
        "sexo": null,
        "outros": []
    }}
}}

Para refinamentos sem número (use 10):
{{
    "vaga_id": null,
    "usar_similaridade": true,
    "limite": 10,
    "filtros": {{
        "idiomas": [
            {{"idioma": "inglês", "nivel_minimo": "básico", "incluir_superiores": true}}
        ],
        "habilidades": ["java"],
        "formacao": {{}},
        "experiencia": {{}},
        "localizacao": null,
        "sexo": null,
        "outros": []
    }}
}}

Exemplos de interpretação:
- "filtre 4 candidatos" → limite: 4, filtros vazios
- "apenas os que têm inglês básico" → limite: 10, filtro de inglês
- "busque pessoas com Java" → limite: 10, filtro de Java
- "mostre 15 candidatos" → limite: 15, filtros vazios

Regras:
- Palavras como "apenas", "somente", "que tenham" = refinamento → limite: 10
- Número explícito sempre tem prioridade
- Se mencionar "vaga [número]" → extraia para vaga_id
- Para idiomas: ENTENDA HIERARQUIA DE NÍVEIS:
  * básico < intermediário < avançado < fluente
  * Se pedir "inglês básico", incluir superiores: true (básico, intermediário, avançado, fluente)
  * Se pedir "inglês avançado", incluir superiores: true (avançado, fluente)  
  * Se pedir especificamente "APENAS inglês básico", incluir superiores: false
  * Múltiplos níveis: "inglês avançado ou fluente" = nivel_minimo: "avançado", incluir_superiores: true
- Para habilidades: CAPTURE TODAS as tecnologias/ferramentas mencionadas (ex: "Java, Python e CSS" = ["java", "python", "css"])
- Se não detectar um critério específico, não inclua no JSON
- Normalize idiomas para português (english -> inglês)
- Normalize níveis (advanced -> avançado, fluent -> fluente, basic -> básico, intermediate -> intermediário)
- Extraia TODAS as habilidades técnicas mencionadas
- Identifique requisitos de formação se mencionados
- Detecte localização se mencionada
- Identifique sexo se mencionado (masculino/feminino)
- Para conectores como "ou", "e", "and", "or": SEMPRE inclua todas as opções mencionadas

JSON:"""
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Extrai e valida JSON da resposta do LLM"""
        # Extrai apenas o JSON da resposta
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            criteria = json.loads(json_str)
            log_info(f"LLM extraiu critérios: {criteria}")
            return criteria
        else:
            log_error(f"LLM não retornou JSON válido: {response}")
            return {"usar_similaridade": True, "filtros": {}}
    
    def _build_semantic_query(self, vaga_id: int, criteria: Dict[str, Any], limit: int) -> tuple:
        """Constrói consulta SQL para busca semântica"""
        filtros = criteria.get('filtros', {})
        
        # Query base com similaridade semântica
        query_parts = [
            "SELECT pa.id, pa.nome, pa.email, pa.endereco, pa.nivel_maximo_formacao,",
            "       pa.cv_pt_json, pa.cv_texto_semantico, pa.updated_at,",
            "       pa.cv_embedding_vector <=> v.vaga_embedding_vector AS distancia",
            "FROM processed_applicants pa, vagas v",
            "WHERE v.id = :vaga_id",
            "  AND pa.cv_embedding_vector IS NOT NULL",
            "  AND v.vaga_embedding_vector IS NOT NULL"
        ]
        
        params = {"vaga_id": vaga_id}
        
        # Adiciona filtros específicos
        if filtros.get('idiomas'):
            idiomas_conditions = self._build_language_filters(filtros['idiomas'])
            if idiomas_conditions:
                query_parts.append(f"  AND ({' OR '.join(idiomas_conditions)})")
        
        if filtros.get('habilidades'):
            skills_conditions = self._build_skills_filters(filtros['habilidades'])
            if skills_conditions:
                query_parts.append(f"  AND ({' OR '.join(skills_conditions)})")
        
        if filtros.get('formacao'):
            education_conditions = self._build_education_filters(filtros['formacao'])
            query_parts.extend(education_conditions)
        
        if filtros.get('localizacao'):
            location = filtros['localizacao'].lower()
            query_parts.append("  AND LOWER(pa.endereco) LIKE :localizacao")
            params['localizacao'] = f'%{location}%'
        
        if filtros.get('sexo'):
            gender = filtros['sexo'].lower()
            query_parts.append("  AND LOWER(pa.sexo) = :sexo")
            params['sexo'] = gender
        
        # Ordenação por similaridade semântica e limite
        query_parts.append("ORDER BY distancia ASC")
        
        # Só adiciona LIMIT se o valor for válido
        if limit is not None and limit > 0:
            query_parts.append(f"LIMIT {limit}")
        else:
            query_parts.append("LIMIT 20")  # valor padrão
        
        return "\n".join(query_parts), params
    
    def _build_language_filters(self, language_filters: List[Dict]) -> List[str]:
        """Constrói filtros SQL para idiomas com hierarquia de níveis"""
        conditions = []
        
        # Hierarquia de níveis de idiomas
        level_hierarchy = {
            'básico': ['básico', 'intermediário', 'avançado', 'fluente'],
            'basico': ['básico', 'intermediário', 'avançado', 'fluente'],
            'intermediário': ['intermediário', 'avançado', 'fluente'],
            'intermediario': ['intermediário', 'avançado', 'fluente'],
            'avançado': ['avançado', 'fluente'],
            'avancado': ['avançado', 'fluente'],
            'fluente': ['fluente']
        }
        
        # Padrões de variação de níveis
        level_patterns = {
            'básico': ['básico', 'basico', 'basic'],
            'intermediário': ['intermediário', 'intermediario', 'intermediate'],
            'avançado': ['avançado', 'avancado', 'advanced'],
            'fluente': ['fluente', 'fluent']
        }
        
        for lang_req in language_filters:
            language = lang_req.get('idioma', '').lower()
            min_level = lang_req.get('nivel_minimo', '').lower()
            include_higher = lang_req.get('incluir_superiores', True)
            
            if language and min_level:
                # Determina níveis aceitos
                if include_higher and min_level in level_hierarchy:
                    accepted_levels = level_hierarchy[min_level]
                else:
                    accepted_levels = [min_level]
                
                # Cria condições para cada nível aceito
                level_conditions = []
                for level in accepted_levels:
                    patterns = level_patterns.get(level, [level])
                    for pattern in patterns:
                        level_conditions.append(f"@.nivel like_regex \"{pattern}\" flag \"i\"")
                
                level_query = f"({' || '.join(level_conditions)})"
                
                conditions.append(
                    f"jsonb_path_exists(pa.cv_pt_json, "
                    f"'$.idiomas[*] ? (@.idioma like_regex \"{language}\" flag \"i\" && {level_query})')"
                )
            elif language:
                # Apenas idioma, sem nível específico
                conditions.append(
                    f"jsonb_path_exists(pa.cv_pt_json, "
                    f"'$.idiomas[*] ? (@.idioma like_regex \"{language}\" flag \"i\")')"
                )
        
        return conditions
    
    def _build_skills_filters(self, skills: List[str]) -> List[str]:
        """Constrói filtros SQL para habilidades"""
        conditions = []
        
        for skill in skills:
            skill_clean = skill.lower().strip()
            if skill_clean:
                conditions.append(
                    f"jsonb_path_exists(pa.cv_pt_json, "
                    f"'$.habilidades[*] ? (@ like_regex \"{skill_clean}\" flag \"i\")')"
                )
        
        return conditions
    
    def _build_education_filters(self, education: Dict) -> List[str]:
        """Constrói filtros SQL para formação"""
        conditions = []
        
        if education.get('nivel'):
            level = education['nivel'].lower()
            conditions.append(
                f"  AND jsonb_path_exists(pa.cv_pt_json, "
                f"'$.formacoes[*] ? (@.nivel like_regex \"{level}\" flag \"i\")')"
            )
        
        if education.get('curso'):
            course = education['curso'].lower()
            conditions.append(
                f"  AND jsonb_path_exists(pa.cv_pt_json, "
                f"'$.formacoes[*] ? (@.curso like_regex \"{course}\" flag \"i\")')"
            )
        
        return conditions
    
    def _process_candidate_row(self, candidate) -> Dict:
        """Processa linha de candidato da consulta SQL"""
        cv_data = candidate.cv_pt_json
        if isinstance(cv_data, str):
            cv_data = json.loads(cv_data)
        
        return {
            'id': candidate.id,
            'nome': candidate.nome,
            'email': candidate.email,
            'endereco': candidate.endereco,
            'nivel_maximo_formacao': candidate.nivel_maximo_formacao,
            'cv_pt': cv_data,
            'score_semantico': float(1 - candidate.distancia),
            'distancia': float(candidate.distancia),
            'origem': 'semantic_search_service'
        }
    
    def _get_job_data(self, workbook_id: str) -> Optional[Dict]:
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
    
    def save_candidates_as_prospects(self, workbook_id: str, candidates: List[Dict]):
        """Salva candidatos encontrados como prospects"""
        try:
            from app.models.match_prospect import MatchProspect
            
            # Remove prospects existentes
            self.db.query(MatchProspect).filter(
                MatchProspect.workbook_id == workbook_id
            ).delete()
            
            # Adiciona novos prospects
            for candidate in candidates:
                match_prospect = MatchProspect(
                    workbook_id=workbook_id,
                    applicant_id=candidate['id'],
                    score_semantico=candidate.get('score_semantico', 0.5),
                    origem=candidate.get('origem', 'semantic_search'),
                    selecionado=False
                )
                self.db.add(match_prospect)
            
            self.db.commit()
            log_info(f"Salvos {len(candidates)} prospects semânticos para workbook {workbook_id}")
            
        except Exception as e:
            log_error(f"Erro ao salvar prospects: {str(e)}")
            self.db.rollback()
