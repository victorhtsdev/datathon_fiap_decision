from typing import Dict, Any, List

class ResponseFormatterService:
    """
    Service responsável por formatar respostas dos filtros de candidatos
    """
    
    def format_search_response(
        self, 
        candidates: List[Dict], 
        original_criteria: str,
        extracted_criteria: Dict[str, Any],
        mode: str = 'incremental'
    ) -> str:
        """
        Formata resposta estruturada dos candidatos encontrados
        
        Args:
            candidates: Lista de candidatos encontrados
            original_criteria: Critério original do usuário
            extracted_criteria: Critérios extraídos pelo LLM
            mode: Modo do filtro ('incrinental' ou 'reset')
            
        Returns:
            Resposta formatada para o usuário
        """
        if not candidates:
            return self._format_no_results_response(original_criteria)
        
        filtros = extracted_criteria.get('filtros', {})
        mode_info = self._get_mode_description(mode)
        
        # Monta resposta estruturada
        response_parts = []
        response_parts.append(f"🔎 {mode_info}")
        response_parts.append(f"📊 Filters aplicados: {self._format_applied_filters(filtros)}")
        response_parts.append(f"[OK] Total de {len(candidates)} candidatos encontrados")
        response_parts.append("")
        response_parts.append("👥 **Candidatos mais compatíveis:**")
        response_parts.append("")
        
        # Lista candidatos
        for i, candidate in enumerate(candidates[:10], 1):
            name = candidate.get('nome', 'N/A')
            score = candidate.get('score_semantico', 0)
            score_percent = f"{score * 100:.1f}%"
            response_parts.append(f"**{i}.** {name} – Compatibilidade: {score_percent}")
        
        # Rodapé informativo
        if len(candidates) > 10:
            response_parts.append(f"\n📋 ... e mais {len(candidates) - 10} candidatos")
        
        response_parts.append("")
        response_parts.append("💡 **Próximos passos:**")
        response_parts.append("• Veja os detalhes completos nos cards ao lado")
        response_parts.append("• Use filtros adicionais para refinar ainda mais")
        response_parts.append("• Digite 'nova busca' para recomeçar do zero")
        
        return '\n'.join(response_parts)
    
    def format_filter_history_response(self, filter_steps: List[Dict]) -> str:
        """
        Formata resposta com histórico de filtros aplicados
        
        Args:
            filter_steps: Lista de steps de filtros aplicados
            
        Returns:
            Resposta formatada com histórico
        """
        if not filter_steps:
            return "📝 Nenhum filtro foi aplicado ainda."
        
        response_parts = []
        response_parts.append("📚 **Histórico de Filters Aplicados:**")
        response_parts.append("")
        
        for step in filter_steps:
            step_num = step.get('step', 0)
            criteria = step.get('criteria', 'N/A')
            count_before = step.get('count_before', 0)
            count_after = step.get('count_after', 0)
            
            response_parts.append(f"**Step {step_num}:** {criteria}")
            response_parts.append(f"  └─ {count_before} → {count_after} candidatos")
            response_parts.append("")
        
        return '\n'.join(response_parts)
    
    def _format_no_results_response(self, original_criteria: str) -> str:
        """Formata resposta quando nenhum candidato é encontrado"""
        return f"""❌ **Nenhum candidato encontrado**

🔍 Critério aplicado: "{original_criteria}"

💡 **Sugestões:**
• Tente critérios menos restritivos
• Use 'nova busca' para recomeçar
• Verifique se os termos estão corretos
• Considere usar sinônimos ou termos mais gerais"""
    
    def _get_mode_description(self, mode: str) -> str:
        """Retorna descrição do modo de busca"""
        if mode == 'incrinental':
            return "Refinamento aplicado sobre candidatos já filtrados"
        elif mode == 'reset':
            return "Nova busca completa realizada"
        else:
            return "Busca realizada"
    
    def _format_applied_filters(self, filtros: Dict[str, Any]) -> str:
        """
        Formata os filtros aplicados in texto legível
        
        Args:
            filtros: Dicionário com filtros aplicados
            
        Returns:
            String formatada com os filtros
        """
        if not filtros or not any(filtros.values()):
            return "busca sinântica geral"
        
        criteria_parts = []
        
        # Idiomas
        if 'idiomas' in filtros and filtros['idiomas']:
            idiomas_list = []
            for idioma in filtros['idiomas']:
                idioma_nome = idioma.get('idioma', '')
                nivel = idioma.get('nivel_minimo', '')
                if idioma_nome and nivel:
                    idiomas_list.append(f"{idioma_nome} {nivel}+")
                elif idioma_nome:
                    idiomas_list.append(idioma_nome)
            
            if idiomas_list:
                criteria_parts.append(f"**Idiomas:** {', '.join(idiomas_list)}")
        
        # Habilidades
        if 'habilidades' in filtros and filtros['habilidades']:
            habilidades = filtros['habilidades']
            if len(habilidades) <= 3:
                criteria_parts.append(f"**Habilidades:** {', '.join(habilidades)}")
            else:
                first_three = ', '.join(habilidades[:3])
                criteria_parts.append(f"**Habilidades:** {first_three} (+{len(habilidades)-3} mais)")
        
        # Formação
        if 'formacao' in filtros and filtros['formacao']:
            formacao = filtros['formacao']
            if formacao.get('nivel') and formacao.get('curso'):
                criteria_parts.append(f"**Formação:** {formacao['nivel']} in {formacao['curso']}")
            elif formacao.get('nivel'):
                criteria_parts.append(f"**Formação:** {formacao['nivel']}")
            elif formacao.get('curso'):
                criteria_parts.append(f"**Curso:** {formacao['curso']}")
        
        # Localização
        if 'localizacao' in filtros and filtros['localizacao']:
            criteria_parts.append(f"**Local:** {filtros['localizacao']}")
        
        # Sexo
        if 'sexo' in filtros and filtros['sexo']:
            criteria_parts.append(f"**Sexo:** {filtros['sexo']}")
        
        # Experiência
        if 'experiencia' in filtros and filtros['experiencia']:
            exp = filtros['experiencia']
            if exp.get('anos_minimos'):
                years = exp['anos_minimos']
                area = exp.get('area', '')
                if area:
                    criteria_parts.append(f"**Experiência:** {years}+ anos in {area}")
                else:
                    criteria_parts.append(f"**Experiência:** {years}+ anos")
        
        return ' | '.join(criteria_parts) if criteria_parts else "busca sinântica geral"
