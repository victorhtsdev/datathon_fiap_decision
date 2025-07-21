from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
import json
import os
from app.core.logging import log_info, log_error


class WorkbookFilterMemory:
    """
    Gerencia array de filtros em memória por workbook.
    Cada workbook mantém uma lista de filtros aplicados sequencialmente.
    Inclui persistência simples em arquivo para desenvolvimento.
    """
    
    def __init__(self):
        # Estrutura: {workbook_id: [filtros]}
        self._memory: Dict[str, List[Dict[str, Any]]] = {}
        self._persistence_file = "filter_memory.json"
        self._load_from_file()
    
    def _load_from_file(self) -> None:
        """Carrega memória de filtros do arquivo"""
        try:
            if os.path.exists(self._persistence_file):
                with open(self._persistence_file, 'r', encoding='utf-8') as f:
                    self._memory = json.load(f)
                log_info(f"Memória de filtros carregada: {len(self._memory)} workbooks")
        except Exception as e:
            log_error(f"Erro ao carregar memória de filtros: {str(e)}")
            self._memory = {}
    
    def _save_to_file(self) -> None:
        """Salva memória de filtros no arquivo"""
        try:
            with open(self._persistence_file, 'w', encoding='utf-8') as f:
                json.dump(self._memory, f, indent=2, ensure_ascii=False)
        except Exception as e:
            log_error(f"Erro ao salvar memória de filtros: {str(e)}")
    
    def add_filter(self, workbook_id: str, filter_data: Dict[str, Any]) -> None:
        """
        Adiciona um novo filtro ao array do workbook.
        
        Args:
            workbook_id: ID do workbook
            filter_data: Dados do filtro extraídos pelo LLM
        """
        try:
            if workbook_id not in self._memory:
                self._memory[workbook_id] = []
            
            # Cria estrutura do filtro
            filter_entry = {
                'id': str(uuid.uuid4()),
                'step': len(self._memory[workbook_id]) + 1,
                'timestamp': datetime.now().isoformat(),
                'original_criteria': filter_data.get('original_criteria', ''),
                'extracted_criteria': filter_data.get('extracted_criteria', {}),
                'filter_type': filter_data.get('filter_type', 'incremental'),
                'candidates_before': filter_data.get('candidates_before', 0),
                'candidates_after': filter_data.get('candidates_after', 0),
                'is_active': True
            }
            
            self._memory[workbook_id].append(filter_entry)
            self._save_to_file()  # Persiste após cada mudança
            
            log_info(f"Filtro adicionado para workbook {workbook_id}: passo {filter_entry['step']}")
            
        except Exception as e:
            log_error(f"Erro ao adicionar filtro: {str(e)}")
    
    def get_filters(self, workbook_id: str) -> List[Dict[str, Any]]:
        """
        Retorna todos os filtros ativos de um workbook.
        
        Args:
            workbook_id: ID do workbook
            
        Returns:
            Lista de filtros ou lista vazia
        """
        try:
            filters = self._memory.get(workbook_id, [])
            # Retorna apenas filtros ativos
            return [f for f in filters if f.get('is_active', True)]
            
        except Exception as e:
            log_error(f"Erro ao buscar filtros: {str(e)}")
            return []
    
    def clear_filters(self, workbook_id: str) -> None:
        """
        Limpa todos os filtros de um workbook.
        
        Args:
            workbook_id: ID do workbook
        """
        try:
            if workbook_id in self._memory:
                self._memory[workbook_id] = []
                self._save_to_file()  # Persiste após limpeza
                log_info(f"Filtros limpos para workbook {workbook_id}")
            
        except Exception as e:
            log_error(f"Erro ao limpar filtros: {str(e)}")
    
    def reset_accumulated_criteria(self, workbook_id: str) -> None:
        """
        Reseta critérios acumulados mantendo apenas o último filtro (se houver).
        Útil para evitar acúmulo excessivo de filtros.
        
        Args:
            workbook_id: ID do workbook
        """
        try:
            if workbook_id in self._memory and self._memory[workbook_id]:
                # Mantém apenas o último filtro
                last_filter = self._memory[workbook_id][-1]
                self._memory[workbook_id] = [last_filter]
                self._save_to_file()
                log_info(f"Critérios acumulados resetados para workbook {workbook_id}")
            
        except Exception as e:
            log_error(f"Erro ao resetar critérios acumulados: {str(e)}")
    
    def get_filter_count(self, workbook_id: str) -> int:
        """
        Retorna quantos filtros ativos existem para um workbook.
        
        Args:
            workbook_id: ID do workbook
            
        Returns:
            Número de filtros ativos
        """
        try:
            return len(self.get_filters(workbook_id))
            
        except Exception as e:
            log_error(f"Erro ao contar filtros: {str(e)}")
            return 0
    
    def get_last_filter(self, workbook_id: str) -> Optional[Dict[str, Any]]:
        """
        Retorna o último filtro aplicado para um workbook.
        
        Args:
            workbook_id: ID do workbook
            
        Returns:
            Último filtro ou None
        """
        try:
            filters = self.get_filters(workbook_id)
            return filters[-1] if filters else None
            
        except Exception as e:
            log_error(f"Erro ao buscar último filtro: {str(e)}")
            return None
    
    def get_filter_history(self, workbook_id: str) -> List[Dict[str, Any]]:
        """
        Retorna histórico completo de filtros aplicados para um workbook.
        
        Args:
            workbook_id: ID do workbook
            
        Returns:
            Lista com histórico de filtros (incluindo inativos)
        """
        try:
            # Retorna todos os filtros, incluindo inativos para histórico completo
            return self._memory.get(workbook_id, [])
            
        except Exception as e:
            log_error(f"Erro ao buscar histórico de filtros: {str(e)}")
            return []
    
    def deactivate_filter(self, workbook_id: str, filter_id: str) -> bool:
        """
        Desativa um filtro específico.
        
        Args:
            workbook_id: ID do workbook
            filter_id: ID do filtro
            
        Returns:
            True se desativado com sucesso
        """
        try:
            if workbook_id not in self._memory:
                return False
            
            for filter_entry in self._memory[workbook_id]:
                if filter_entry.get('id') == filter_id:
                    filter_entry['is_active'] = False
                    log_info(f"Filtro {filter_id} desabilitado para workbook {workbook_id}")
                    return True
            
            return False
            
        except Exception as e:
            log_error(f"Erro ao desativar filtro: {str(e)}")
            return False
    
    def get_accumulated_criteria(self, workbook_id: str) -> Dict[str, Any]:
        """
        Retorna critérios acumulados de todos os filtros ativos.
        Útil para consultas SQL que precisam considerar todos os filtros.
        
        Args:
            workbook_id: ID do workbook
            
        Returns:
            Critérios combinados sem duplicatas
        """
        try:
            filters = self.get_filters(workbook_id)
            
            if not filters:
                return {}
            
            # Combina critérios de todos os filtros (evitando duplicatas)
            accumulated = {
                'usar_similaridade': False,
                'filtros': {},
                'combined_text': [],
                'limite': None
            }
            
            # Sets para evitar duplicatas
            seen_texts = set()
            seen_languages = set()
            seen_skills = set()
            
            for filter_entry in filters:
                criteria = filter_entry.get('extracted_criteria', {})
                
                # Combina texto de busca semântica
                if criteria.get('usar_similaridade'):
                    accumulated['usar_similaridade'] = True
                
                # Preserva limite do primeiro filtro com limite específico (não 999)
                if accumulated['limite'] is None:
                    current_limit = criteria.get('limite')
                    if current_limit and current_limit != 999:
                        accumulated['limite'] = current_limit
                
                # Acumula filtros específicos (evitando duplicatas)
                if 'filtros' in criteria:
                    filtros = criteria['filtros']
                    
                    # Idiomas (evita duplicatas por idioma+nivel)
                    if 'idiomas' in filtros and filtros['idiomas']:
                        if 'idiomas' not in accumulated['filtros']:
                            accumulated['filtros']['idiomas'] = []
                        
                        for idioma in filtros['idiomas']:
                            if isinstance(idioma, dict):
                                lang_key = (
                                    idioma.get('idioma', '').lower(),
                                    idioma.get('nivel_minimo', '').lower()
                                )
                                if lang_key not in seen_languages and lang_key[0]:
                                    accumulated['filtros']['idiomas'].append(idioma)
                                    seen_languages.add(lang_key)
                    
                    # Habilidades (evita duplicatas de strings)
                    if 'habilidades' in filtros and filtros['habilidades']:
                        if 'habilidades' not in accumulated['filtros']:
                            accumulated['filtros']['habilidades'] = []
                        
                        for skill in filtros['habilidades']:
                            skill_clean = str(skill).lower().strip()
                            if skill_clean and skill_clean not in seen_skills:
                                accumulated['filtros']['habilidades'].append(skill)
                                seen_skills.add(skill_clean)
                    
                    # Outros filtros (apenas valores não vazios)
                    for key, value in filtros.items():
                        if key not in ['idiomas', 'habilidades'] and value:
                            # Adiciona apenas se valor não for vazio, None, {}, []
                            if value and value != {} and value != [] and value is not None:
                                accumulated['filtros'][key] = value
                
                # Acumula critério original para busca semântica (evita duplicatas)
                original = filter_entry.get('original_criteria', '').strip()
                if original and original not in seen_texts:
                    accumulated['combined_text'].append(original)
                    seen_texts.add(original)
            
            # Converte texto combinado em string
            if accumulated['combined_text']:
                accumulated['texto_busca'] = ' AND '.join(accumulated['combined_text'])
            
            return accumulated
            
        except Exception as e:
            log_error(f"Erro ao acumular critérios: {str(e)}")
            return {}
    
    def clear_workbook_history(self, workbook_id: str) -> bool:
        """
        Limpa todo o histórico de filtros de um workbook específico.
        
        Args:
            workbook_id: ID do workbook para limpar
            
        Returns:
            True se limpou com sucesso, False caso contrário
        """
        try:
            if workbook_id in self._memory:
                del self._memory[workbook_id]
                self._save_to_file()
                log_info(f"Histórico limpo para workbook {workbook_id}")
                return True
            else:
                log_info(f"Workbook {workbook_id} não tem histórico para limpar")
                return True
                
        except Exception as e:
            log_error(f"Erro ao limpar histórico: {str(e)}")
            return False
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas da memória para debug.
        
        Returns:
            Estatísticas da memória
        """
        try:
            stats = {
                'total_workbooks': len(self._memory),
                'workbooks': {}
            }
            
            for workbook_id, filters in self._memory.items():
                active_filters = [f for f in filters if f.get('is_active', True)]
                stats['workbooks'][workbook_id] = {
                    'total_filters': len(filters),
                    'active_filters': len(active_filters),
                    'last_filter_time': filters[-1]['timestamp'] if filters else None
                }
            
            return stats
            
        except Exception as e:
            log_error(f"Erro ao gerar estatísticas: {str(e)}")
            return {}


# Instância global singleton
_filter_memory_instance = None

def get_filter_memory() -> WorkbookFilterMemory:
    """
    Retorna instância singleton da memória de filtros.
    
    Returns:
        Instância da WorkbookFilterMemory
    """
    global _filter_memory_instance
    if _filter_memory_instance is None:
        _filter_memory_instance = WorkbookFilterMemory()
    return _filter_memory_instance
