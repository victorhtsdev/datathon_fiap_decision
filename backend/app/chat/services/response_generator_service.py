from typing import Dict, Any, List
from app.llm.factory import get_llm_client
from app.core.logging import log_info, log_error
import json


class ResponseGeneratorService:
    """
    Serviço especializado para gerar respostas inteligentes sobre 
    resultados de busca de candidatos usando LLM.
    """
    
    def __init__(self):
        self.llm_client = get_llm_client()
    
    def generate_candidate_response(
        self, 
        candidates: List[Dict], 
        original_criteria: str,
        extracted_criteria: Dict[str, Any]
    ) -> str:
        """
        Gera resposta inteligente sobre candidatos encontrados
        """
        if not candidates:
            return self._generate_no_candidates_response(original_criteria)
        
        try:
            # Prepara resumo dos candidatos
            candidates_summary = self._prepare_candidates_summary(candidates)
            
            # Gera resposta usando LLM
            prompt = self._build_response_prompt(
                candidates_summary, 
                original_criteria, 
                extracted_criteria,
                len(candidates)
            )
            
            response = self.llm_client.extract_text(prompt)
            return response.strip()
            
        except Exception as e:
            log_error(f"Erro ao gerar resposta com LLM: {str(e)}")
            return self._generate_fallback_response(candidates, extracted_criteria)
    
    def _generate_no_candidates_response(self, criteria: str) -> str:
        """Gera resposta quando nenhum candidato é encontrado"""
        return f"Não encontrei candidatos que atendam aos critérios específicos: '{criteria}'"
    
    def _prepare_candidates_summary(self, candidates: List[Dict]) -> List[Dict]:
        """Prepara resumo dos candidatos para o LLM"""
        summary = []
        
        for i, candidate in enumerate(candidates[:5], 1):
            name = candidate.get('nome', 'N/A')
            location = candidate.get('endereco', 'N/A')
            education = candidate.get('nivel_maximo_formacao', 'N/A')
            score = candidate.get('score_semantico', 0)
            distance = candidate.get('distancia', 0)
            
            # Extrai informações do CV
            cv_data = candidate.get('cv_pt', {})
            
            # Idiomas
            languages = cv_data.get('idiomas', [])
            languages_text = self._format_languages(languages)
            
            # Habilidades
            skills = cv_data.get('habilidades', [])
            skills_text = ', '.join(skills[:5]) if skills else "Não informado"
            
            # Experiências
            experiences = cv_data.get('experiencias', [])
            exp_text = self._format_experiences(experiences)
            
            summary.append({
                'posicao': i,
                'nome': name,
                'localizacao': location,
                'formacao': education,
                'score_semantico': f"{score:.3f}",
                'distancia': f"{distance:.3f}",
                'idiomas': languages_text,
                'habilidades': skills_text,
                'experiencia': exp_text
            })
        
        return summary
    
    def _format_languages(self, languages: List[Dict]) -> str:
        """Formata lista de idiomas"""
        if not languages:
            return "Não informado"
        
        formatted = []
        for lang in languages:
            idioma = lang.get('idioma', '')
            nivel = lang.get('nivel', '')
            if idioma and nivel:
                formatted.append(f"{idioma} ({nivel})")
            elif idioma:
                formatted.append(idioma)
        
        return ', '.join(formatted) if formatted else "Não informado"
    
    def _format_experiences(self, experiences: List[Dict]) -> str:
        """Formata experiências profissionais"""
        if not experiences:
            return "Não informado"
        
        # Pega as 2 experiências mais recentes
        recent_exp = experiences[:2]
        formatted = []
        
        for exp in recent_exp:
            cargo = exp.get('cargo', '')
            empresa = exp.get('empresa', '')
            if cargo and empresa:
                formatted.append(f"{cargo} na {empresa}")
            elif cargo:
                formatted.append(cargo)
        
        return ', '.join(formatted) if formatted else "Não informado"
    
    def _build_response_prompt(
        self, 
        candidates_summary: List[Dict], 
        original_criteria: str,
        extracted_criteria: Dict[str, Any],
        total_candidates: int
    ) -> str:
        """Constrói prompt para geração de resposta"""
        return f"""
Gere uma resposta amigável e profissional sobre os candidatos encontrados para esta solicitação:

Critério original: "{original_criteria}"
Critérios extraídos: {json.dumps(extracted_criteria, indent=2, ensure_ascii=False)}

IMPORTANTE: Esta busca SEMPRE usa similaridade semântica com a vaga como base, garantindo que os candidatos retornados sejam os mais compatíveis. Os filtros específicos são aplicados como critérios adicionais.

Candidatos encontrados ({total_candidates} total):
{json.dumps(candidates_summary, indent=2, ensure_ascii=False)}

Gere uma resposta que:
1. Confirme que encontrou candidatos usando busca semântica otimizada
2. Liste os top 5 candidatos com seus scores de compatibilidade semântica
3. Destaque os critérios específicos que foram aplicados (idiomas, habilidades, formação, etc.)
4. Mencione brevemente as qualificações mais relevantes de cada candidato
5. Informe que a busca foi baseada em similaridade semântica com a vaga
6. Use emojis para deixar mais amigável e legível
7. Mencione que os candidatos foram salvos como prospects
8. Se houver mais de 5 candidatos, mencione quantos foram encontrados no total

Resposta:"""
    
    def _generate_fallback_response(self, candidates: List[Dict], extracted_criteria: Dict[str, Any]) -> str:
        """Gera resposta de fallback quando o LLM falha"""
        filtros = extracted_criteria.get('filtros', {})
        
        response_parts = []
        
        # Cabeçalho
        response_parts.append(f"Encontrei {len(candidates)} candidatos usando busca semântica otimizada:")
        
        # Critérios aplicados
        if filtros and any(filtros.values()):
            criteria_text = self._format_applied_criteria(filtros)
            if criteria_text:
                response_parts.append(f"Filtros aplicados: {', '.join(criteria_text)}")
        
        response_parts.append("")
        
        # Lista candidatos
        for i, candidate in enumerate(candidates[:5], 1):
            name = candidate.get('nome', 'N/A')
            location = candidate.get('endereco', 'N/A')
            education = candidate.get('nivel_maximo_formacao', 'N/A')
            score = candidate.get('score_semantico', 0)
            response_parts.append(f"{i}. {name} - {location} ({education}) - Score: {score:.3f}")
        
        if len(candidates) > 5:
            response_parts.append(f"... e mais {len(candidates) - 5} candidatos.")
        
        response_parts.append("")
        response_parts.append("Busca baseada em similaridade semântica com a vaga")
        response_parts.append("Consulta executada diretamente no banco PostgreSQL")
        response_parts.append("Os candidatos foram encontrados com sucesso.")
        
        return '\n'.join(response_parts)
    
    def _format_applied_criteria(self, filtros: Dict[str, Any]) -> List[str]:
        """Formata critérios aplicados para exibição"""
        criteria_text = []
        
        # Idiomas
        if 'idiomas' in filtros and filtros['idiomas']:
            for idioma in filtros['idiomas']:
                nivel = idioma.get('nivel_minimo', idioma.get('nivel', ''))
                criteria_text.append(f"Idioma: {idioma['idioma']} {nivel}")
        
        # Habilidades
        if 'habilidades' in filtros and filtros['habilidades']:
            skills_text = ', '.join(filtros['habilidades'][:3])  # Máximo 3 para não ficar muito longo
            if len(filtros['habilidades']) > 3:
                skills_text += "..."
            criteria_text.append(f"Habilidades: {skills_text}")
        
        # Formação
        if 'formacao' in filtros and filtros['formacao']:
            formacao = filtros['formacao']
            if formacao.get('nivel'):
                criteria_text.append(f"Formação: {formacao['nivel']}")
            if formacao.get('curso'):
                criteria_text.append(f"Curso: {formacao['curso']}")
        
        # Localização
        if 'localizacao' in filtros:
            criteria_text.append(f"Local: {filtros['localizacao']}")
        
        # Sexo
        if 'sexo' in filtros:
            criteria_text.append(f"Sexo: {filtros['sexo']}")
        
        return criteria_text
    
    def generate_error_response(self, error_message: str) -> str:
        """Gera resposta amigável para erros"""
        return f"Desculpe, ocorreu um problema: {error_message}"
    
    def generate_insufficient_data_response(self, missing_data: str) -> str:
        """Gera resposta quando dados necessários estão faltando"""
        return f"Para realizar a busca, preciso de: {missing_data}"
