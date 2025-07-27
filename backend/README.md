**API Backend DataThon Decision**

> **API de Backend para Sistema de Correspondência de Candidatos e Vagas**

---

## 📋 Descrição

Esta aplicação fornece um conjunto de **endpoints RESTful** que compõem o backend de uma solução inteligente de recrutamento desenvolvida para o desafio **Datathon FIAP**.

O sistema automatiza etapas críticas do processo de recrutamento da empresa **Decision**, desde o recebimento de dados brutos até a análise semântica para match inteligente entre candidatos e vagas.

Principais funcionalidades:

- **Normalização de Currículos e Vagas com LLMs**: Recebimento de dados brutos em texto livre e transformação em estruturas JSON padronizadas, extraindo informações como experiências, formações, habilidades e requisitos da vaga.
- **Geração de Texto Semântico e Embeddings**: A partir do JSON padronizado, o sistema gera um texto descritivo semântico usado para criar embeddings vetoriais com modelos como OpenAI, DeepSeek e Ollama.
- **Match Semântico de Perfis com Vagas**: Comparação vetorial entre perfis de candidatos e descrições de vagas usando similaridade de embeddings, ranqueando os melhores matches.
- **Gerenciamento de Workbooks**: Agrupamento de candidatos processados por vaga ou processo seletivo, permitindo curadoria e visualização dos perfis selecionados.
- **Chat com LLM Integrado**: Permite conversas com um modelo de linguagem para apoiar análise, triagem e recomendações, com histórico de sessões.
- **Análise Contínua de Performance Semântica**: Exposição de métricas e dados analíticos via API para avaliação da eficácia dos matches gerados, com visualização feita no frontend.
- **Serviço de Dados para Frontend**: Todos os dados estruturados são expostos via API para integração com a interface visual do sistema (frontend em React/Vite).

O objetivo é apoiar o fluxo de recrutamento da empresa Decision, desde o recebimento e processamento de currículos, até a análise semântica e correspondência de prospects.

---

## ⚙️ Uso

A aplicação expõe endpoints organizados por módulos. A seguir, lista dos principais.

### 📁 workbook.py

| Método | Endpoint                                  | Descrição                               |
| ------ | ----------------------------------------- | --------------------------------------- |
| GET    | `/workbook`                               | Lista todos os workbooks                |
| POST   | `/workbook`                               | Cria um novo workbook                   |
| GET    | `/workbook/{workbook_id}`                 | Consulta um workbook específico         |
| PUT    | `/workbook/{workbook_id}`                 | Atualiza um workbook existente          |
| DELETE | `/workbook/{workbook_id}`                 | Remove um workbook                      |
| POST   | `/workbook/{workbook_id}/match-prospects` | Atualiza match prospects de um workbook |
| GET    | `/workbook/{workbook_id}/match-prospects` | Lista match prospects do workbook       |

### 📁 vaga.py

| Método | Endpoint           | Descrição                                                                    |
| ------ | ------------------ | ---------------------------------------------------------------------------- |
| GET    | `/vagas/lista`     | Lista todas as vagas                                                         |
| GET    | `/vagas/abertas`   | Lista apenas vagas com status aberta                                         |
| GET    | `/vagas/{vaga_id}` | Consulta detalhes de uma vaga específica                                     |
| POST   | `/vagas`           | Cria ou atualiza vaga, normaliza dados e gera embedding para busca semântica |

### 📁 semantic\_performance.py

| Método | Endpoint                      | Descrição                                     |
| ------ | ----------------------------- | --------------------------------------------- |
| GET    | `/semantic-performance`       | Consulta métricas de performance semântica    |
| DELETE | `/semantic-performance/cache` | Limpa o cache de performance                  |
| GET    | `/semantic-performance/info`  | Retorna informações estáticas sobre a análise |

### 📁 prospects\_match.py

| Método | Endpoint                                     | Descrição                                             |
| ------ | -------------------------------------------- | ----------------------------------------------------- |
| GET    | `/prospects-match/by-workbook/{workbook_id}` | Busca prospects vinculados a um workbook              |
| GET    | `/prospects-match/by-vaga/{vaga_id}`         | Busca prospects associados a uma vaga                 |
| GET    | `/prospects-match/search/by-name`            | Busca prospects por trecho de nome                    |
| GET    | `/prospects-match/workbooks/summary`         | Retorna resumo de workbooks com prospects disponíveis |

### 📁 processed\_applicant.py

| Método | Endpoint                                    | Descrição                                       |
| ------ | ------------------------------------------- | ----------------------------------------------- |
| GET    | `/processed-applicants`                     | Lista candidatos processados (paginado)         |
| GET    | `/processed-applicants/{applicant_id}`      | Consulta detalhes de um candidato processado    |
| PUT    | `/processed-applicants/{applicant_id}`      | Atualiza informações de um candidato processado |
| GET    | `/processed-applicants/search/by-name`      | Busca candidatos por nome (partial match)       |
| GET    | `/processed-applicants/search/by-education` | Busca candidatos por nível de formação          |

### 📁 chat.py

| Método | Endpoint                     | Descrição                             |
| ------ | ---------------------------- | ------------------------------------- |
| POST   | `/chat`                      | Envia mensagem ao LLM                 |
| GET    | `/chat/history/{session_id}` | Obtém histórico de uma sessão de chat |
| DELETE | `/chat/session/{session_id}` | Encerra sessão de chat                |

### 📁 applicant.py

| Método | Endpoint                                  | Descrição                                                                             |
| ------ | ----------------------------------------- | ------------------------------------------------------------------------------------- |
| POST   | `/process_applicant/`                     | Processa ou atualiza candidato, normaliza dados e gera embedding para busca semântica |
| GET    | `/get_processed_applicant/{applicant_id}` | Consulta candidato processado                                                         |
| POST   | `/get_applicants_by_ids`                  | Busca múltiplos candidatos por IDs                                                    |
| GET    | `/get_processed_applicant/{applicant_id}` | Consulta candidato processado                                                         |
| POST   | `/get_applicants_by_ids`                  | Busca múltiplos candidatos por IDs                                                    |

## 🖥️ Endpoints usados no Frontend

Os métodos (endpoints) do backend utilizados no frontend são:

- GET `/workbook`
- POST `/workbook`
- GET `/workbook/{workbook_id}`
- PUT `/workbook/{workbook_id}`
- DELETE `/workbook/{workbook_id}`
- POST `/workbook/{workbook_id}/match-prospects`
- GET `/workbook/{workbook_id}/match-prospects`
- GET `/prospects-match/by-workbook/{workbook_id}`
- GET `/prospects-match/by-vaga/{vaga_id}`
- GET `/prospects-match/search/by-name`
- GET `/prospects-match/workbooks/summary`
- GET `/vagas/{vaga_id}`
- POST `/get_applicants_by_ids`
- GET `/semantic-performance`
- DELETE `/semantic-performance/cache`
- GET `/semantic-performance/info`
- POST `/chat`

---

## 📦 Estrutura de Pastas

```
backend/
├── app/
│   ├── chat/            # Serviços e integrações de chat/LLM
│   ├── core/            # Configurações, banco de dados, logging, utilitários
│   ├── dependencies.py  # Dependências injetáveis do FastAPI
│   ├── llm/             # Integração com modelos de linguagem (LLM)
│   ├── models/          # Modelos ORM (SQLAlchemy)
│   ├── repositories/    # Repositórios de acesso a dados
│   ├── routers/         # Endpoints da API (FastAPI)
│   ├── schemas/         # Schemas Pydantic (validação e serialização)
│   ├── services/        # Lógica de negócio e serviços auxiliares
│   └── main.py          # Ponto de entrada da aplicação FastAPI
├── data/                # Dados de entrada (JSON, ZIP, etc)
├── temp_cache/          # Arquivos de cache temporário
├── tests/               # Testes automatizados do backend
├── requirements.txt     # Dependências Python do backend
├── Dockerfile           # Dockerfile para o backend
└── README.md            # Documentação do backend
```

---

## 🛠️ Tecnologias

- **Python 3.11+**
- **FastAPI** (framework web)
- **SQLAlchemy** (ORM)
- **Pydantic** (validação de dados)
- **Uvicorn** (ASGI server)
- **PostgreSQL** (banco de dados relacional)
- **Pandas e NumPy** (manipulação e análise de dados)
- **Requests e HTTPX** (requisições HTTP síncronas e assíncronas)
- **OpenAI, DeepSeek, Gemma 3, Ollama** (integração com LLMs)
- **Docker** (containerização)
- **Pytest** (testes automatizados)
- **python-dotenv** (gerenciamento de variáveis de ambiente)

---

## 📑 Requisitos

Pacotes necessários:

```
fastapi==0.115.14
sqlalchemy==2.0.41
psycopg2-binary==2.9.10
python-dotenv==1.1.1
pytest==8.4.1
pydantic-settings==2.10.1
openai==1.93.0
pandas==2.2.3
numpy==2.3.1
requests==2.32.3
uvicorn==0.35.0
ollama==0.5.1
```

---

## 🔧 Variáveis de Ambiente

Defina as seguintes variáveis no arquivo `.env` ou no ambiente, sem expor valores sensíveis:

```
LLM_BACKEND        # Backend de LLM (e.g., ollama, openai)
OLLAMA_MODEL       # Modelo Ollama (e.g., gemma3:4b-it-qat)
DEEPSEEK_API_KEY   # Chave de API DeepSeek
DATABASE_URL       # URL de conexão com PostgreSQL
CHUNK_SIZE         # Tamanho de chunk para processamento de texto
DEBUG              # Modo debug (true/false)
SAVE_LOGS          # Salvar logs em arquivo (true/false)
APP_LOG_ENABLED    # Ativar registro de logs da aplicação (true/false)
APP_LOG_LEVEL      # Nível de log (e.g., INFO, DEBUG)
APP_LOG_FILE       # Caminho para o arquivo de log
LLM_LOG            # Ativar logs do LLM (true/false)
OPENAI_API_KEY     # Chave de API OpenAI
OPENAI_MODEL       # Modelo Open AI 
```

## 📄 Licença

Este projeto está licenciado sob a **MIT License**. Por favor, consulte o arquivo `LICENSE` para mais detalhes.

