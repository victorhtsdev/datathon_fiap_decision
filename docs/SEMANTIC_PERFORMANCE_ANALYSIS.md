# Análise de Performance da Busca Semântica

## Visão Geral

Este módulo implementa uma análise detalhada da performance do algoritmo de busca semântica utilizado no sistema. A análise mede a eficácia do matching entre candidatos e vagas baseado na similaridade de vetores embeddings usando pgvector.

## Funcionamento

### 1. Coleta de Dados
- Identifica vagas que tiveram candidatos com status positivo (aprovados)
- Para cada vaga, busca os 50 candidatos mais similares semanticamente
- Utiliza o operador `<=>` do pgvector (distância de cosseno)

### 2. Análise de Ranking
- Ranqueia candidatos por similaridade (menor distância = maior similaridade)
- Verifica em que posições estavam os candidatos efetivamente aprovados
- Calcula métricas de performance baseadas no ranking

### 3. Métricas Calculadas

#### Métricas Gerais
- **Total de aprovados**: Quantidade de candidatos aprovados analisados
- **Média de posição**: Posição média dos aprovados no ranking semântico
- **Mediana**: Posição mediana dos aprovados
- **Desvio padrão**: Variabilidade das posições
- **Vagas analisadas**: Quantidade de vagas com dados válidos

#### Distribuição por Top Positions
- **Top 1**: Percentual de aprovados que foram o candidato mais similar
- **Top 3**: Percentual de aprovados entre os 3 primeiros
- **Top 5**: Percentual de aprovados entre os 5 primeiros
- **Top 10**: Percentual de aprovados entre os 10 primeiros
- **Top 20**: Percentual de aprovados entre os 20 primeiros

#### Dados para Visualização
- **Histograma**: Distribuição das posições dos aprovados
- **Status**: Distribuição por tipo de aprovação

## Otimização de Performance

### Sistema de Cache
- Cache diário em arquivo JSON (`temp_cache/semantic_performance_cache.json`)
- Validação por data: se já calculado hoje, retorna do cache
- Reduz tempo de resposta de minutos para milissegundos
- Cache pode ser limpo forçadamente via API

### Consultas Otimizadas
- Uso de índices no PostgreSQL para operações com vetores
- Limitação a 50 candidatos por vaga para performance
- Filtragem eficiente usando JOINs

## Endpoints da API

### `GET /api/analytics/semantic-performance`
Retorna análise completa de performance da busca semântica.

**Resposta:**
```json
{
  "metricas_gerais": {
    "total_aprovados": 1182,
    "media_posicao": 2.77,
    "mediana_posicao": 1.0,
    "desvio_padrao": 3.45,
    "vagas_analisadas": 156
  },
  "distribuicao_top_positions": {
    "top_1": {"quantidade": 693, "percentual": 58.6},
    "top_3": {"quantidade": 941, "percentual": 79.6},
    "top_5": {"quantidade": 1032, "percentual": 87.3},
    "top_10": {"quantidade": 1122, "percentual": 94.9},
    "top_20": {"quantidade": 1150, "percentual": 97.3}
  },
  "histogram_data": [
    {"posicao": 1, "quantidade": 693},
    {"posicao": 2, "quantidade": 124},
    {"posicao": 3, "quantidade": 124}
  ],
  "status_distribution": [
    {"status": "Contratado pela Decision", "quantidade": 450},
    {"status": "Aprovado", "quantidade": 380}
  ],
  "pgvector_info": {
    "operador_usado": "<=>",
    "tipo_distancia": "Distância de Cosseno",
    "interpretacao": "Quanto menor o valor, maior a similaridade semântica",
    "range_tipico": "0 (idênticos) a 2 (opostos)",
    "ordenacao": "ASC (menor distância = maior similaridade)"
  },
  "mensagem_interpretacao": "📊 Análise dos Resultados...",
  "generated_at": "2025-01-20T10:30:00"
}
```

### `DELETE /api/analytics/semantic-performance/cache`
Remove cache forçando recálculo na próxima consulta.

### `GET /api/analytics/semantic-performance/info`
Retorna informações sobre a análise sem executar cálculos.

## Interpretação dos Resultados

### Indicadores de Boa Performance
- **Média baixa** (< 3): Aprovados aparecem nas primeiras posições
- **Top 1 alto** (> 50%): Muitos aprovados são os mais similares
- **Top 10 alto** (> 90%): Sistema consistente até 10ª posição

### Sobre o pgvector
- **Operador `<=>`**: Calcula distância de cosseno entre vetores
- **Valores baixos**: Indicam alta similaridade semântica
- **Ordenação ASC**: Para obter candidatos mais similares primeiro
- **Range típico**: 0 (idênticos) a 2 (completamente diferentes)

## Arquivos Envolvidos

### Serviços
- `app/services/semantic_performance_service.py`: Lógica principal
- `app/routers/semantic_performance.py`: Endpoints da API
- `app/schemas/semantic_performance.py`: Modelos de dados

### Dependências
- **pandas**: Análise de dados e cálculos estatísticos
- **numpy**: Operações numéricas
- **sqlalchemy**: Consultas ao banco PostgreSQL
- **pgvector**: Extensão PostgreSQL para operações com vetores

### Cache
- **Localização**: `backend/temp_cache/`
- **Arquivo**: `semantic_performance_cache.json`
- **Estrutura**: `{generated_at: ISO_DATE, data: ANALYSIS_RESULT}`

## Configuração no Frontend

Para visualizar os dados no frontend, use os endpoints acima para:

1. **Métricas em cards**: Use `metricas_gerais`
2. **Gráfico de barras**: Use `distribuicao_top_positions`
3. **Histograma**: Use `histogram_data`
4. **Gráfico de pizza**: Use `status_distribution`
5. **Texto explicativo**: Use `mensagem_interpretacao`

## Monitoramento

### Logs
- Todas as operações são logadas via `app.core.logging`
- Inclui timestamps, erros e status do cache

### Métricas de Sistema
- Tempo de resposta (cache vs recálculo)
- Tamanho do cache em disco
- Número de vagas/candidatos processados

## Considerações Técnicas

### Performance
- Consulta inicial pode levar 2-5 minutos (primeira execução)
- Com cache: resposta em < 100ms
- Consumo de memória: ~50MB durante cálculo

### Escalabilidade
- Limitado pelo tamanho da base de dados
- Consultas otimizadas para grandes volumes
- Cache evita recálculos desnecessários

### Manutenção
- Cache renovado automaticamente diariamente
- Logs para debugging e monitoramento
- APIs de administração para controle manual
