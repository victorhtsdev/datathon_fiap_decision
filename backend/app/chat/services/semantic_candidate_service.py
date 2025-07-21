from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.llm.factory import get_llm_client
from app.core.logging import log_info, log_error
import json
import re


class SemanticCandidateService:
    """
    Simplified service for semantic candidate search.
    
    Single flow:
    1. extract_criteria_with_llm() - Extract criteria from text
    2. semantic_filter_candidates() - Search pool + filter in Python
    
    No duplications: Removed obsolete SQL methods.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.llm_client = get_llm_client()
    
    def filter_candidates_complete(self, workbook_id: str, user_input: str) -> Dict[str, Any]:
        """
        Single simplified method: No minory, just extract criteria and search.
        
        Input: user text
        Output: complete response for chat
        """
        try:
            log_info(f"=== SIMPLE FILTER: '{user_input}' ===")
            
            # Step 1: Extract criteria with LLM (no context)
            criteria = self.extract_criteria_with_llm(user_input)
            
            # Step 2: Search candidates directly
            candidates = self.semantic_filter_candidates(workbook_id, criteria)
            
            # Step 3: Save as prospects
            self.save_candidates_as_prospects(workbook_id, candidates)
            
            # Step 4: Smart response considering selected candidates
            total_count = len(candidates)
            
            # Count existing selected candidates
            from app.models.match_prospect import MatchProspect
            selected_count = self.db.query(MatchProspect).filter(
                MatchProspect.workbook_id == workbook_id,
                MatchProspect.selecionado == True
            ).count()
            
            new_candidates_count = total_count - selected_count
            
            # Build appropriate message
            if total_count == 0:
                message = "Nenhum candidato encontrado."
            elif selected_count == 0:
                # Only new candidates
                if new_candidates_count == 1:
                    message = "Encontrei 1 candidato."
                else:
                    message = f"Encontrei {new_candidates_count} candidatos."
            else:
                # Has selected candidates
                if new_candidates_count == 0:
                    message = f"Existem {selected_count} candidato{selected_count != 1 and 's' or ''} selecionado{selected_count != 1 and 's' or ''} (nenhum novo encontrado)."
                elif new_candidates_count == 1:
                    message = f"Encontrei mais 1 candidato e existem {selected_count} selecionado{selected_count != 1 and 's' or ''}."
                else:
                    message = f"Encontrei mais {new_candidates_count} candidatos e existem {selected_count} selecionado{selected_count != 1 and 's' or ''}."
            
            return {
                "response": message,
                "data": {
                    "candidates": candidates,
                    "total": total_count
                },
                "intent": "filter_candidates"
            }
            
        except Exception as e:
            log_error(f"Error in complete filter: {str(e)}")
            return {
                "response": "Erro ao filtrar candidatos.",
                "data": {"candidates": [], "total": 0},
                "intent": "filter_candidates"
            }
    
    def extract_criteria_with_llm(self, filter_text: str) -> Dict[str, Any]:
        """
        Use LLM to extract specific filter criteria from natural text
        Simplified version: No historical context
        """
        prompt = self._build_extraction_prompt(filter_text)
        
        try:
            response = self.llm_client.extract_text(prompt)
            criteria = self._parse_llm_response(response)
            
            # Fallback: If LLM didn't extract limit but there's a number in text, force extraction
            if criteria.get('limite') is None:
                extracted_limit = self._extract_limit_fallback(filter_text)
                if extracted_limit:
                    criteria['limite'] = extracted_limit
                    log_info(f"FALLBACK: Extracted limit {extracted_limit} via regex from '{filter_text}'")
            
            return criteria
            
        except Exception as e:
            log_error(f"Error extracting criteria with LLM: {str(e)}")
            # Try fallback even on error
            fallback_limit = self._extract_limit_fallback(filter_text)
            return {
                "usar_similaridade": True, 
                "limite": fallback_limit,
                "filtros": {}
            }
    
    def _extract_limit_fallback(self, text: str) -> Optional[int]:
        """
        Extract limit by regex as fallback when LLM fails
        """
        import re
        
        # Patterns to extract candidate numbers
        patterns = [
            r'\b(?:me\s+)?(?:traga|busque|filtre|quero|encontre)\s+(\d+)\s*candidatos?\b',
            r'\b(\d+)\s*candidatos?\b',
            r'\btraga\s+(\d+)\b',
            r'\bbusque\s+(\d+)\b'
        ]
        
        text_lower = text.lower()
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    limit = int(match.group(1))
                    if 1 <= limit <= 100:  # Reasonable limit
                        return limit
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def semantic_filter_candidates(
        self, 
        workbook_id: str, 
        criteria: Dict[str, Any]
    ) -> List[Dict]:
        """
        MAIN METHOD: Semantic search + Python filters
        
        SIMPLIFIED STRATEGY:
        1. Search large pool by semantic similarity
        2. Filter with Python (more reliable than complex SQL)
        3. Exclude candidates already in match prospects
        4. Apply final limit
        """
        try:
            # Extrai limite dos critérios
            limit = criteria.get('limite', 10)
            
            # Garantir que limit seja um número inteiro
            if isinstance(limit, list) and limit:
                limit = int(limit[0]) if str(limit[0]).isdigit() else 10
            elif isinstance(limit, str) and limit.isdigit():
                limit = int(limit)
            elif not isinstance(limit, int) or limit <= 0:
                limit = 10
            
            log_info(f"BUSCA SEMÂNTICA: workbook={workbook_id}, limite={limit}")
            
            # Obtém dados da vaga
            vaga_data = self._get_job_data(workbook_id)
            if not vaga_data:
                log_error("Unable to retrieve job data")
                return []
            
            vaga_id = criteria.get('vaga_id') or vaga_data.get('id')
            if not vaga_id:
                log_error("Unable to determine job ID")
                return []
            
            log_info(f"Using job_id: {vaga_id} for semantic search")
            
            # STEP 0: Busca candidatos já nos match prospects para referência
            existing_prospect_ids = self._get_existing_prospect_ids(workbook_id)
            selected_prospect_ids = self._get_selected_prospect_ids(workbook_id)
            log_info(f"Candidatos já nos prospects: {len(existing_prospect_ids)}")
            log_info(f"Candidatos selecionados (sinpre mostrar): {len(selected_prospect_ids)}")
            
            # STEP 1: Busca um POOL GRANDE excluindo apenas prospects NÃO selecionados
            # Candidatos selecionados sinpre aparecin, mas exclui outros já nos prospects
            non_selected_prospects = [pid for pid in existing_prospect_ids if pid not in selected_prospect_ids]
            pool_size = max(1000, limit * 10)  # Garante pool suficiente
            log_info(f"Excluding {len(non_selected_prospects)} non-selected prospects from search")
            log_info(f"Searching pool of {pool_size} candidates for filtering")
            
            base_query, base_params = self._build_base_semantic_query(vaga_id, pool_size, non_selected_prospects)
            
            log_info(f"Executando busca do pool: {base_query}")
            log_info(f"Parameters: {base_params}")
            
            result = self.db.execute(text(base_query), base_params)
            candidates_raw = result.fetchall()
            
            log_info(f"Pool inicial: {len(candidates_raw)} candidatos")
            
            # STEP 2: Processa candidatos in Python
            all_candidates = []
            for candidate in candidates_raw:
                try:
                    candidate_dict = self._process_candidate_row(candidate)
                    all_candidates.append(candidate_dict)
                except Exception as e:
                    log_error(f"Erro ao processar candidato {candidate.id}: {str(e)}")
                    continue
            
            log_info(f"Candidatos processados: {len(all_candidates)}")
            
            # STEP 3: Separa candidatos selecionados ANTES dos filtros
            selected_candidates = []
            non_selected_candidates = []
            
            for candidate in all_candidates:
                if candidate['id'] in selected_prospect_ids:
                    selected_candidates.append(candidate)  # Selecionados sinpre passam
                else:
                    non_selected_candidates.append(candidate)
            
            # Ordena candidatos selecionados por score sinântico DESC (maiores scores primeiro)
            selected_candidates.sort(key=lambda x: x.get('score_semantico', 0.0), reverse=True)
            
            # Log dos scores dos candidatos selecionados
            if selected_candidates:
                log_info(f"Scores dos candidatos selecionados:")
                for i, cand in enumerate(selected_candidates[:5]):  # Mostra só os 5 primeiros
                    log_info(f"  {i+1}. {cand.get('nome', 'N/A')} (ID: {cand.get('id')}) - Score: {cand.get('score_semantico', 0.0):.3f}")
            
            log_info(f"Candidatos selecionados (sem filtros, ordenados por relevância): {len(selected_candidates)}")
            log_info(f"Non-selected candidates for filtering: {len(non_selected_candidates)}")
            
            # STEP 4: Aplica filtros APENAS nos candidatos não selecionados
            filtered_new_candidates = self._apply_python_filters(non_selected_candidates, criteria)
            
            # Ordena candidatos novos por score sinântico DESC (maiores scores primeiro)
            filtered_new_candidates.sort(key=lambda x: x.get('score_semantico', 0.0), reverse=True)
            
            # Log dos scores dos candidatos novos
            if filtered_new_candidates:
                log_info(f"Scores dos candidatos novos (top 10):")
                for i, cand in enumerate(filtered_new_candidates[:10]):
                    log_info(f"  {i+1}. {cand.get('nome', 'N/A')} (ID: {cand.get('id')}) - Score: {cand.get('score_semantico', 0.0):.3f}")
            
            log_info(f"Non-selected candidates after filtering and sorting: {len(filtered_new_candidates)}")
            
            # STEP 5: Candidatos selecionados sempre aparecem + novos até o limite solicitado
            # Selected ones DON'T count in limit - they are EXTRAS
            final_result = selected_candidates + filtered_new_candidates[:limit]
                
            log_info(f"Resultado final: {len(selected_candidates)} selecionados (extras) + {len(filtered_new_candidates[:limit])} novos (limite) = {len(final_result)} total")
            
            return final_result
            
        except Exception as e:
            log_error(f"Erro na busca semântica: {str(e)}")
            return []
    
    def _build_extraction_prompt(self, filter_text: str) -> str:
        """Build simple prompt for criteria extraction by LLM"""
        
        return f"""
Analise esta solicitação de filtro de candidatos e extraia TODOS os critérios mencionados.

Solicitação: "{filter_text}"

REGRAS PARA LIMITE (MUITO IMPORTANTE):
- Se mencionar "me traga X candidatos", "busque X", "filtre X", "quero X candidatos" onde X é um número → use X como INTEGER
- Exinplos: "me traga 6 candidatos" → limite: 6, "busque 10" → limite: 10, "filtre 5" → limite: 5
- Se NÃO mencionar número → use null
- LIMITE deve ser um número inteiro (6, 10, 5), nunca null quando há número explícito

REGRAS PARA FILTROS:
- Tecnologias como AWS, Java, Python, React → vão in "habilidades"
- Idiomas como inglês, espanhol → vão in "idiomas"
  * Para idiomas com level específico: {{"idioma": "inglês", "nivel_minimo": "avançado", "incluir_superiores": true}}
  * Para idiomas sin level: "inglês"
  * Níveis válidos: básico, intermediário, avançado, fluente
- Localizações como São Paulo, Rio → vão in "localizacao"
- SEMPRE use similaridade sinântica (usar_similaridade: true)

EXEMPLOS CORRETOS:
- "me traga 6 candidatos" → limite: 6, filtros: {{}}
- "me traga 7 candidatos" → limite: 7, filtros: {{}}
- "busque 10 candidatos" → limite: 10, filtros: {{}}
- "busque candidatos com AWS" → habilidades: ["AWS"], limite: null
- "5 candidatos com inglês" → habilidades: [], idiomas: ["inglês"], limite: 5
- "candidatos com inglês avançado" → idiomas: [{{"idioma": "inglês", "nivel_minimo": "avançado", "incluir_superiores": true}}], limite: null
- "inglês a partir de intermediário" → idiomas: [{{"idioma": "inglês", "nivel_minimo": "intermediário", "incluir_superiores": true}}], limite: null

Retorne APENAS um JSON válido com esta estrutura:

{{
    "vaga_id": null,
    "usar_similaridade": true,
    "limite": null,
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

ATENÇÃO: Se a solicitação contém um número de candidatos, o "limite" DEVE ser esse número, não null!

JSON:"""
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Extrai e valida JSON da resposta do LLM"""
        # Extrai apenas o JSON da resposta
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            criteria = json.loads(json_str)
            
            # Corrige o formato do limite se necessário
            if 'limite' in criteria:
                limite = criteria['limite']
                if isinstance(limite, list) and limite:
                    # Se é uma lista, pega o primeiro elinento
                    criteria['limite'] = int(limite[0]) if str(limite[0]).isdigit() else None
                elif isinstance(limite, str) and limite.isdigit():
                    # If it's numeric string, convert to int
                    criteria['limite'] = int(limite)
                elif not isinstance(limite, (int, type(None))):
                    # Se não é int nin None, define como None
                    criteria['limite'] = None
            
            log_info(f"LLM extraiu critérios: {criteria}")
            return criteria
        else:
            log_error(f"LLM did not return valid JSON: {response}")
            return {"usar_similaridade": True, "filtros": {}}
    
    def _build_base_semantic_query(self, vaga_id: int, pool_size: int, exclude_prospect_ids: List[int] = None) -> tuple:
        """Constrói consulta SQL base APENAS com similaridade sinântica (sin filtros específicos)"""
        
        query = """SELECT pa.id, pa.nome, pa.email, pa.endereco, pa.nivel_maximo_formacao,
       pa.cv_pt_json, pa.cv_texto_semantico, pa.updated_at,
       pa.cv_embedding_vector <=> v.vaga_embedding_vector AS distancia
FROM processed_applicants pa, vagas v
WHERE v.id = :vaga_id
  AND pa.cv_embedding_vector IS NOT NULL
  AND v.vaga_embedding_vector IS NOT NULL"""
        
        params = {"vaga_id": vaga_id, "pool_size": pool_size}
        
        # Adiciona exclusão de candidatos já nos prospects
        if exclude_prospect_ids:
            placeholders = ','.join([f':exclude_id_{i}' for i in range(len(exclude_prospect_ids))])
            query += f" AND pa.id NOT IN ({placeholders})"
            
            for i, candidate_id in enumerate(exclude_prospect_ids):
                params[f'exclude_id_{i}'] = candidate_id
        
        query += " ORDER BY distancia ASC LIMIT :pool_size"
        
        return query, params

    def _get_existing_prospect_ids(self, workbook_id: str) -> List[int]:
        """Busca IDs dos candidatos que já estão nos match prospects"""
        try:
            from app.models.match_prospect import MatchProspect
            
            prospects = self.db.query(MatchProspect.applicant_id).filter(
                MatchProspect.workbook_id == workbook_id
            ).all()
            
            prospect_ids = [prospect.applicant_id for prospect in prospects]
            log_info(f"Found {len(prospect_ids)} candidatos já nos prospects: {prospect_ids}")
            return prospect_ids
            
        except Exception as e:
            log_error(f"Erro ao buscar prospects existentes: {str(e)}")
            return []

    def _get_selected_prospect_ids(self, workbook_id: str) -> List[int]:
        """Busca IDs dos candidatos que estão selecionados nos match prospects"""
        try:
            from app.models.match_prospect import MatchProspect
            
            prospects = self.db.query(MatchProspect.applicant_id).filter(
                MatchProspect.workbook_id == workbook_id,
                MatchProspect.selecionado == True
            ).all()
            
            prospect_ids = [prospect.applicant_id for prospect in prospects]
            log_info(f"Found {len(prospect_ids)} candidatos selecionados: {prospect_ids}")
            return prospect_ids
            
        except Exception as e:
            log_error(f"Erro ao buscar prospects selecionados: {str(e)}")
            return []

    def _apply_python_filters(self, candidates: List[Dict], criteria: Dict[str, Any]) -> List[Dict]:
        """Aplica filtros específicos in Python sobre a lista de candidatos"""
        filtros = criteria.get('filtros', {})
        filtered = candidates.copy()
        
        # Filtra por idiomas
        if filtros.get('idiomas'):
            filtered = self._filter_by_languages(filtered, filtros['idiomas'])
            
        # Filtra por habilidades
        if filtros.get('habilidades'):
            filtered = self._filter_by_skills(filtered, filtros['habilidades'])
            
        # Filtra por formação
        if filtros.get('formacao'):
            filtered = self._filter_by_education(filtered, filtros['formacao'])
            
        # Filtra por localização
        if filtros.get('localizacao'):
            filtered = self._filter_by_location(filtered, filtros['localizacao'])
            
        # Filtra por sexo
        if filtros.get('sexo'):
            filtered = self._filter_by_gender(filtered, filtros['sexo'])
        
        return filtered

    def _filter_by_languages(self, candidates: List[Dict], language_filters: List) -> List[Dict]:
        """Filtra candidatos por idiomas in Python"""
        if not language_filters:
            return candidates
        
        log_info(f"Filtrando por idiomas: {language_filters}")
        
        # Processa diferentes formatos de entrada
        processed_filters = []
        for lang_filter in language_filters:
            if isinstance(lang_filter, dict) and lang_filter.get('idioma'):
                # Formato correto: {'idioma': 'inglês', 'nivel_minimo': 'intermediário'}
                processed_filters.append(lang_filter)
            elif isinstance(lang_filter, str):
                # Formato simples: 'inglês' ou 'ingles'
                processed_filters.append({
                    'idioma': lang_filter,
                    'nivel_minimo': None,
                    'incluir_superiores': True
                })
        
        if not processed_filters:
            log_info("Nenhum filtro de idioma válido encontrado")
            return candidates
        
        log_info(f"Filters processados: {processed_filters}")
        
        filtered = []
        
        # Hierarquia de níveis
        level_hierarchy = {
            'básico': ['básico', 'intermediário', 'avançado', 'fluente'],
            'basico': ['básico', 'intermediário', 'avançado', 'fluente'],
            'intermediário': ['intermediário', 'avançado', 'fluente'],
            'intermediario': ['intermediário', 'avançado', 'fluente'],
            'avançado': ['avançado', 'fluente'],
            'avancado': ['avançado', 'fluente'],
            'fluente': ['fluente']
        }
        
        for candidate in candidates:
            cv_data = candidate.get('cv_pt', {})
            candidate_languages = cv_data.get('idiomas', [])
            
            # Verifica se atende a PELO MENOS UM dos requisitos de idioma
            meets_language_req = False
            
            for lang_req in processed_filters:
                required_lang = str(lang_req.get('idioma', '')).lower()
                required_level = str(lang_req.get('nivel_minimo', '') or '').lower()
                include_higher = lang_req.get('incluir_superiores', True)
                
                # Mapeia variações do inglês
                if required_lang in ['ingles', 'inglês', 'english']:
                    required_lang = 'inglês'
                
                log_info(f"Checking candidate {candidate.get('nome', 'N/A')} for language '{required_lang}' minimum level '{required_level}'")
                log_info(f"Idiomas do candidato: {candidate_languages}")
                
                for cand_lang in candidate_languages:
                    if not isinstance(cand_lang, dict):
                        continue
                        
                    cand_lang_name = str(cand_lang.get('idioma', '')).lower()
                    cand_lang_level = str(cand_lang.get('nivel', '')).lower()
                    
                    # Normaliza variações do inglês
                    if cand_lang_name in ['ingles', 'inglês', 'english']:
                        cand_lang_name = 'inglês'
                    
                    # Verifica se é o idioma correto
                    if required_lang in cand_lang_name or cand_lang_name in required_lang or required_lang == cand_lang_name:
                        
                        if not required_level:  # Só idioma, sin level
                            meets_language_req = True
                            log_info(f"MATCH: {candidate.get('nome', 'N/A')} has {cand_lang_name}")
                            break
                            
                        # Verifica level
                        if include_higher and required_level in level_hierarchy:
                            accepted_levels = level_hierarchy[required_level]
                            # Verifica se o level do candidato está na lista de níveis aceitos
                            if any(accepted_level.lower() == cand_lang_level.strip().lower() for accepted_level in accepted_levels):
                                meets_language_req = True
                                log_info(f"MATCH: {candidate.get('nome', 'N/A')} has {cand_lang_name} level {cand_lang_level} (accepted for {required_level})")
                                break
                        elif required_level.lower() == cand_lang_level.strip().lower():
                            meets_language_req = True
                            log_info(f"MATCH: {candidate.get('nome', 'N/A')} has {cand_lang_name} level {cand_lang_level} (exato)")
                            break
                        else:
                            log_info(f"REJECT: {candidate.get('nome', 'N/A')} has {cand_lang_name} level '{cand_lang_level}' mas precisa de '{required_level}' ou superior")
                
                if meets_language_req:
                    break
            
            if meets_language_req:
                filtered.append(candidate)
        
        log_info(f"Filter de idiomas: {len(candidates)} candidatos -> {len(filtered)} filtrados")
        return filtered

    def _filter_by_skills(self, candidates: List[Dict], skills: List[str]) -> List[Dict]:
        """Filtra candidatos por habilidades in Python"""
        if not skills:
            return candidates
        
        # Filtra apenas strings válidas
        valid_skills = [skill for skill in skills if isinstance(skill, str) and skill.strip()]
        
        if not valid_skills:
            return candidates
            
        filtered = []
        
        for candidate in candidates:
            cv_data = candidate.get('cv_pt', {})
            candidate_skills = cv_data.get('habilidades', [])
            candidate_skills_text = ' '.join(str(skill) for skill in candidate_skills if skill).lower()
            
            # Verifica se has PELO MENOS UMA das habilidades
            has_skill = False
            for required_skill in valid_skills:
                if required_skill.lower() in candidate_skills_text:
                    has_skill = True
                    break
            
            if has_skill:
                filtered.append(candidate)
        
        return filtered

    def _filter_by_education(self, candidates: List[Dict], education: Dict) -> List[Dict]:
        """Filtra candidatos por formação in Python"""
        if not education:
            return candidates
            
        # Implementar se necessário
        return candidates

    def _filter_by_location(self, candidates: List[Dict], location: str) -> List[Dict]:
        """Filtra candidatos por localização in Python"""
        if not location or not isinstance(location, str):
            return candidates
            
        filtered = []
        location_lower = location.lower()
        
        for candidate in candidates:
            candidate_location = str(candidate.get('endereco', '')).lower()
            if location_lower in candidate_location:
                filtered.append(candidate)
        
        return filtered

    def _filter_by_gender(self, candidates: List[Dict], gender: str) -> List[Dict]:
        """Filtra candidatos por sexo in Python"""
        if not gender or not isinstance(gender, str):
            return candidates
            
        # Implementar se necessário (campo sexo não está no modelo atual)
        return candidates

    # MÉTODOS OBSOLETOS REMOVIDOS:
    # - _build_semantic_query() → substituído por _build_base_semantic_query() + Python filters
    # - _build_language_filters() → substituído por _filter_by_languages()  
    # - _build_skills_filters() → substituído por _filter_by_skills()
    # - _build_education_filters() → substituído por _filter_by_education()
    
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
            'origin': 'semantic_search_service'
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
            
            # Rinove prospects existentes
            self.db.query(MatchProspect).filter(
                MatchProspect.workbook_id == workbook_id
            ).delete()
            
            # Adiciona novos prospects
            for candidate in candidates:
                match_prospect = MatchProspect(
                    workbook_id=workbook_id,
                    applicant_id=candidate['id'],
                    score_semantico=candidate.get('score_semantico', 0.5),
                    origem=candidate.get('origin', 'semantic_search'),
                    selecionado=False
                )
                self.db.add(match_prospect)
            
            self.db.commit()
            log_info(f"Saved {len(candidates)} semantic prospects for workbook {workbook_id}")
            
        except Exception as e:
            log_error(f"Erro ao salvar prospects: {str(e)}")
            self.db.rollback()
