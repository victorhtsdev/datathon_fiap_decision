from typing import Dict, List, Any, Optional
import uuid
import json
import os
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import text
import numpy as np
import pandas as pd
from pathlib import Path

from app.core.database import SessionLocal
from app.core.logging import log_info, log_error, log_warning
from app.core.exceptions import APIExceptions


class SemanticPerformanceService:
    """Serviço para análise de performance da busca semântica"""
    
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
        self.cache_dir = Path("temp_cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "semantic_performance_cache.json"
    
    def _is_cache_valid(self) -> bool:
        """Verifica se o cache é válido (mesmo dia)"""
        if not self.cache_file.exists():
            return False
        
        # Lê a data do cache
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                cache_date = datetime.fromisoformat(cache_data.get('generated_at', ''))
                return cache_date.date() == date.today()
        except Exception as e:
            log_warning(f"Erro ao verificar cache: {e}")
            return False
    
    def _save_cache(self, data: Dict[str, Any]) -> None:
        """Salva dados no cache"""
        try:
            cache_data = {
                'generated_at': datetime.now().isoformat(),
                'data': data
            }
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            log_info("Cache de performance semântica atualizado")
        except Exception as e:
            log_error(f"Erro ao salvar cache: {e}")
    
    def _load_cache(self) -> Optional[Dict[str, Any]]:
        """Carrega dados do cache"""
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                return cache_data.get('data')
        except Exception as e:
            log_error(f"Erro ao carregar cache: {e}")
            return None
    
    def get_performance_analysis(self) -> Dict[str, Any]:
        """
        Retorna análise de performance da busca semântica.
        Usa cache se disponível e válido, senão recalcula.
        """
        # Verifica cache primeiro
        if self._is_cache_valid():
            cached_data = self._load_cache()
            if cached_data:
                log_info("Retornando dados do cache de performance")
                return cached_data
        
        # Recalcula os dados
        log_info("Recalculando dados de performance semântica")
        performance_data = self._calculate_performance_metrics()
        
        # Salva no cache
        self._save_cache(performance_data)
        
        return performance_data
    
    def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calcula métricas de performance da busca semântica"""
        try:
            # Status considerados como positivos (aprovados)
            status_positivos = (
                'Contratado como Hunting', 'Contratado pela Decision',
                'Documentação PJ', 'Aprovado', 'Proposta Aceita'
            )
            
            # 1. Buscar vagas com ao menos 1 candidato aprovado
            query_vagas = f"""
            SELECT DISTINCT vaga_id 
            FROM prospects 
            WHERE situacao_candidado IN {status_positivos}
            """
            
            vagas_result = self.db.execute(text(query_vagas)).fetchall()
            vaga_ids = [row[0] for row in vagas_result]
            
            if not vaga_ids:
                log_warning("Nenhuma vaga com candidatos aprovados encontrada")
                return self._empty_response()
            
            log_info(f"Analisando {len(vaga_ids)} vagas com candidatos aprovados")
            
            # 2. Para cada vaga, analisar ranking dos aprovados
            resultados = []
            
            for vaga_id in vaga_ids:
                vaga_results = self._analyze_vaga_performance(vaga_id, status_positivos)
                resultados.extend(vaga_results)
                if vaga_results:
                    log_info(f"Vaga {vaga_id}: {len(vaga_results)} candidatos aprovados encontrados")
            
            log_info(f"Total de resultados coletados: {len(resultados)} candidatos aprovados")
            
            if not resultados:
                log_warning("Nenhum resultado de análise encontrado")
                return self._empty_response()
            
            # 3. Calcular métricas agregadas
            return self._calculate_aggregate_metrics(resultados)
            
        except Exception as e:
            log_error(f"Erro ao calcular métricas de performance: {str(e)}")
            raise APIExceptions.internal_error("Erro ao calcular métricas de performance")
    
    def _analyze_vaga_performance(self, vaga_id: int, status_positivos: tuple) -> List[Dict]:
        """
        Analisa performance de uma vaga específica.
        
        Metodologia (conforme notebook de análise):
        1. Verifica se há mais de um candidato COM embedding válido
        2. Para cada vaga com candidatos aprovados, busca todos os candidatos 
           com embeddings válidos que se candidataram à vaga
        3. Ranqueia por similaridade semântica
        4. Verifica quais desses candidatos foram aprovados
        5. Registra a posição (rank) de cada aprovado no ranking semântico
        
        Isso mede se o algoritmo semântico consegue ranquear corretamente
        os candidatos que se candidataram, colocando os aprovados nas primeiras posições.
        """
        try:
            # Verificar se há mais de um candidato COM embedding (em processed_applicants)
            query_verificacao = """
            SELECT COUNT(*) 
            FROM prospects p
            JOIN processed_applicants pa ON pa.id = p.codigo::bigint
            WHERE p.vaga_id = :vaga_id
              AND pa.cv_embedding_vector IS NOT NULL
            """
            
            qtd_validos_result = self.db.execute(
                text(query_verificacao), 
                {"vaga_id": vaga_id}
            ).fetchone()
            
            qtd_validos = qtd_validos_result[0] if qtd_validos_result else 0
            
            if qtd_validos < 2:
                return []  # pula essa vaga se tem menos de 2 candidatos válidos
        
            # Consulta dos candidatos válidos para análise semântica
            query_candidatos = """
            SELECT 
                pa.id,
                pa.nome,
                pa.cv_embedding_vector <=> v.vaga_embedding_vector AS distancia
            FROM 
                processed_applicants pa
            JOIN 
                prospects p ON pa.id = p.codigo::bigint
            JOIN 
                vagas v ON v.id = p.vaga_id
            WHERE 
                v.id = :vaga_id
                AND pa.cv_embedding_vector IS NOT NULL
                AND v.vaga_embedding_vector IS NOT NULL
            ORDER BY 
                pa.cv_embedding_vector <=> v.vaga_embedding_vector ASC
            """
            
            candidatos_result = self.db.execute(
                text(query_candidatos), 
                {"vaga_id": vaga_id}
            ).fetchall()
            
            if not candidatos_result:
                return []

            # Adicionar rank (1-based)
            candidatos_com_rank = []
            for idx, row in enumerate(candidatos_result, 1):
                candidatos_com_rank.append({
                    'id': row[0],
                    'nome': row[1],
                    'distancia': float(row[2]),
                    'rank': idx
                })
            
            # Buscar status de TODOS os candidatos desta vaga
            query_status = """
            SELECT codigo::bigint AS id, situacao_candidado
            FROM prospects
            WHERE vaga_id = :vaga_id
            """
            
            status_result = self.db.execute(
                text(query_status), 
                {"vaga_id": vaga_id}
            ).fetchall()
            
            # Criar mapping de status
            status_map = {row[0]: row[1] for row in status_result}
            
            # Unir candidatos com status e filtrar apenas os aprovados
            resultados = []
            for candidato in candidatos_com_rank:
                status = status_map.get(candidato['id'])
                if status and status in status_positivos:
                    resultados.append({
                        "vaga_id": vaga_id,
                        "candidato_id": candidato['id'],
                        "candidato_nome": candidato['nome'],
                        "rank": candidato['rank'],
                        "distancia": candidato['distancia'],
                        "status": status
                    })
            
            return resultados
            
        except Exception as e:
            log_error(f"Erro ao analisar vaga {vaga_id}: {str(e)}")
            return []
    
    def _calculate_aggregate_metrics(self, resultados: List[Dict]) -> Dict[str, Any]:
        """Calcula métricas agregadas dos resultados"""
        if not resultados:
            return self._empty_response()
        
        df = pd.DataFrame(resultados)
        
        # Métricas básicas
        total_aprovados = len(df)
        media_posicao = df['rank'].mean()
        mediana_posicao = df['rank'].median()
        desvio_padrao = df['rank'].std()
        
        # Calcular vagas analisadas corretamente - baseado no notebook
        # qtd_vagas_usadas = df_resultados["vaga_id"].nunique()
        # Conta apenas as vagas que efetivamente geraram resultados (que passaram pelos filtros)
        qtd_vagas_usadas = df['vaga_id'].nunique()
        
        # Distribuição por top positions
        top_positions = {}
        for top_n in [1, 3, 5, 10, 20]:
            qtd = (df['rank'] <= top_n).sum()
            pct = (qtd / total_aprovados * 100) if total_aprovados > 0 else 0
            top_positions[f'top_{top_n}'] = {
                'quantidade': int(qtd),
                'percentual': round(float(pct), 1)
            }
        
        # Histograma para gráfico
        hist_data = df['rank'].value_counts().sort_index()
        histogram = [
            {'posicao': int(pos), 'quantidade': int(qtd)} 
            for pos, qtd in hist_data.items()
        ]
        
        # Distribuição por status
        status_distribution = df['status'].value_counts().to_dict()
        status_data = [
            {'status': status, 'quantidade': int(qtd)}
            for status, qtd in status_distribution.items()
        ]
        
        return {
            "metricas_gerais": {
                "total_aprovados": total_aprovados,
                "media_posicao": round(float(media_posicao), 2),
                "mediana_posicao": float(mediana_posicao),
                "desvio_padrao": round(float(desvio_padrao), 2),
                "vagas_analisadas": qtd_vagas_usadas,  # Baseado no notebook: df_resultados["vaga_id"].nunique()
                "vagas_com_ranking_semantico": qtd_vagas_usadas  # Mesmo valor - vagas que puderam ser ranqueadas semanticamente
            },
            "distribuicao_top_positions": top_positions,
            "histogram_data": histogram,
            "status_distribution": status_data,
            "pgvector_info": {
                "operador_usado": "<=>",
                "tipo_distancia": "Distância de Cosseno",
                "interpretacao": "Menor valor = maior similaridade semântica",
                "range_tipico": "0.0 (idêntico) a 2.0 (opostos)",
                "ordenacao": "ASC (menores distâncias primeiro)"
            },
            "mensagem_interpretacao": self._generate_interpretation_message(
                total_aprovados, media_posicao, mediana_posicao, top_positions
            ),
            "interpretacao_estruturada": self._generate_structured_interpretation(
                total_aprovados, media_posicao, mediana_posicao, top_positions
            ),
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_interpretation_message(self, total: int, media: float, mediana: float, top_pos: Dict) -> str:
        """Gera mensagem de interpretação dos resultados"""
        return f"""## 📊 Interpretação dos Resultados

### 📈 Visão Geral
- **{total:,} candidatos aprovados** analisados na base de dados
- **Performance da busca semântica** para identificar os melhores candidatos

### 🎯 Métricas de Precisão
- **Posição média dos aprovados:** {media:.1f}º lugar
- **Metade dos aprovados aparece até a {int(mediana)}ª posição**
- **{top_pos['top_1']['percentual']:.0f}% dos aprovados** foram os mais recomendados semanticamente
- **{top_pos['top_10']['percentual']:.0f}% dos aprovados** aparecem entre os 10 primeiros

### 🔍 Análise Detalhada
| Top N | Quantidade | Percentual | Interpretação |
|-------|------------|------------|---------------|
| **Top 1** | {top_pos['top_1']['quantidade']} | **{top_pos['top_1']['percentual']}%** | Candidatos que foram a primeira recomendação |
| **Top 3** | {top_pos['top_3']['quantidade']} | **{top_pos['top_3']['percentual']}%** | Candidatos entre os 3 primeiros |
| **Top 5** | {top_pos['top_5']['quantidade']} | **{top_pos['top_5']['percentual']}%** | Candidatos entre os 5 primeiros |
| **Top 10** | {top_pos['top_10']['quantidade']} | **{top_pos['top_10']['percentual']}%** | Candidatos entre os 10 primeiros |

� **Conclusão:** A busca semântica demonstra {'alta' if media <= 10 else 'moderada' if media <= 20 else 'baixa'} precisão, com média de posição {media:.1f} para candidatos aprovados."""
    
    def _empty_response(self) -> Dict[str, Any]:
        """Retorna resposta vazia quando não há dados"""
        return {
            "metricas_gerais": {
                "total_aprovados": 0,
                "media_posicao": 0,
                "mediana_posicao": 0,
                "desvio_padrao": 0,
                "vagas_analisadas": 0,
                "vagas_com_ranking_semantico": 0
            },
            "distribuicao_top_positions": {},
            "histogram_data": [],
            "status_distribution": [],
            "pgvector_info": {
                "operador_usado": "<=>",
                "tipo_distancia": "Distância de Cosseno",
                "interpretacao": "Menor valor = maior similaridade semântica",
                "range_tipico": "0.0 (idêntico) a 2.0 (opostos)",
                "ordenacao": "ASC (menores distâncias primeiro)"
            },
            "mensagem_interpretacao": "## 📊 Nenhum Dado Disponível\n\nNão foram encontrados candidatos aprovados para análise.",
            "interpretacao_estruturada": {
                "titulo": "Nenhum Dado Disponível",
                "visao_geral": {
                    "total_candidatos": {"valor": 0, "descricao": "candidatos aprovados encontrados"},
                    "objetivo": "Análise não pôde ser realizada"
                },
                "metricas_precisao": [],
                "analise_detalhada": [],
                "conclusao": {
                    "nivel_precisao": "indefinido",
                    "cor": "gray",
                    "texto": "Não foram encontrados dados suficientes para análise.",
                    "recomendacao": "Verifique se existem candidatos aprovados no sistema."
                }
            },
            "generated_at": datetime.now().isoformat()
        }
    
    def clear_cache(self) -> bool:
        """Remove o cache forçando recálculo na próxima chamada"""
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
                log_info("Cache de performance removido")
                return True
            return False
        except Exception as e:
            log_error(f"Erro ao remover cache: {e}")
            return False
    
    def _generate_structured_interpretation(self, total: int, media: float, mediana: float, top_pos: Dict) -> Dict[str, Any]:
        """Gera interpretação estruturada dos resultados para melhor visualização no frontend"""
        # Determinar nível de precisão
        if media <= 10:
            nivel_precisao = "alta"
            cor_precisao = "green"
        elif media <= 20:
            nivel_precisao = "moderada"
            cor_precisao = "yellow"
        else:
            nivel_precisao = "baixa"
            cor_precisao = "red"
        
        return {
            "titulo": "Interpretação dos Resultados",
            "visao_geral": {
                "total_candidatos": {
                    "valor": total,
                    "descricao": "candidatos aprovados analisados na base de dados"
                },
                "objetivo": "Performance da busca semântica para identificar os melhores candidatos"
            },
            "metricas_precisao": [
                {
                    "label": "Posição média dos aprovados",
                    "valor": f"{media:.1f}º lugar",
                    "tipo": "posicao"
                },
                {
                    "label": "Mediana das posições",
                    "valor": f"{int(mediana)}ª posição",
                    "descricao": "Metade dos aprovados aparece até esta posição"
                },
                {
                    "label": "Top 1 - Primeira recomendação",
                    "valor": f"{top_pos['top_1']['percentual']:.0f}%",
                    "descricao": "dos aprovados foram os mais recomendados semanticamente"
                },
                {
                    "label": "Top 10 - Entre os 10 primeiros",
                    "valor": f"{top_pos['top_10']['percentual']:.0f}%",
                    "descricao": "dos aprovados aparecem entre os 10 primeiros"
                }
            ],
            "analise_detalhada": [
                {
                    "categoria": "Top 1",
                    "quantidade": top_pos['top_1']['quantidade'],
                    "percentual": top_pos['top_1']['percentual'],
                    "interpretacao": "Candidatos que foram a primeira recomendação",
                    "cor": "#10B981"  # green-500
                },
                {
                    "categoria": "Top 3",
                    "quantidade": top_pos['top_3']['quantidade'],
                    "percentual": top_pos['top_3']['percentual'],
                    "interpretacao": "Candidatos entre os 3 primeiros",
                    "cor": "#3B82F6"  # blue-500
                },
                {
                    "categoria": "Top 5",
                    "quantidade": top_pos['top_5']['quantidade'],
                    "percentual": top_pos['top_5']['percentual'],
                    "interpretacao": "Candidatos entre os 5 primeiros",
                    "cor": "#8B5CF6"  # violet-500
                },
                {
                    "categoria": "Top 10",
                    "quantidade": top_pos['top_10']['quantidade'],
                    "percentual": top_pos['top_10']['percentual'],
                    "interpretacao": "Candidatos entre os 10 primeiros",
                    "cor": "#F59E0B"  # amber-500
                }
            ],
            "conclusao": {
                "nivel_precisao": nivel_precisao,
                "cor": cor_precisao,
                "texto": f"A busca semântica demonstra {nivel_precisao} precisão, com média de posição {media:.1f} para candidatos aprovados.",
                "recomendacao": self._get_recommendation(nivel_precisao, media)
            }
        }
    
    def _get_recommendation(self, nivel: str, media: float) -> str:
        """Gera recomendação baseada no nível de precisão"""
        if nivel == "alta":
            return "Excelente performance! O algoritmo está funcionando muito bem para identificar candidatos qualificados."
        elif nivel == "moderada":
            return "Performance boa, mas há espaço para melhorias. Considere ajustar os embeddings ou critérios de matching."
        else:
            return "Performance abaixo do esperado. Recomenda-se revisar o processo de geração de embeddings e os critérios de similaridade."
