# Nova Estrutura de Chat - Documentação

## Estrutura Criada

```
backend/app/chat/
├── __init__.py
├── models/
│   └── chat_session.py          # Modelos de sessão e mensagens
├── services/
│   ├── chat_service.py          # Service principal (facade)
│   ├── chat_orchestrator.py     # Orquestrador central
│   └── intent_classifier.py     # Classificação de intenções
└── handlers/
    ├── base_handler.py          # Classe base para handlers
    ├── vaga_handler.py          # Handler para perguntas sobre vagas
    ├── candidate_handler.py     # Handler para perguntas sobre candidatos
    ├── filter_handler.py        # Handler para filtros de candidatos
    └── generic_handler.py       # Handler para conversação genérica
```

## Arquivos Removidos (redundantes)

**Arquivos de Chat Antigos:**
- `app/services/chat_service.py` (antigo)
- `app/services/chat_handlers.py` (antigo)  
- `app/services/chat_intent_classifier.py` (antigo)

**Handlers de Filtro Antigos/Não Utilizados:**
- `app/services/candidate_filter_handler.py` (768 linhas, não usado)
- `app/services/candidate_filter_langchain_handler.py` (402 linhas, não usado)

## Arquivos Mantidos em `app/services/`

Estes foram mantidos pois contêm lógica específica que não é exclusiva do chat:

- `candidate_filter_llm_handler.py` (lógica de filtros LLM)
- `filter_history_service.py` (serviço de histórico)
- `criteria_extraction_service.py` (extração de critérios)
- `query_builder_service.py` (construção de queries)
- `response_formatter_service.py` (formatação de respostas)

## Como Funciona a Nova Arquitetura

1. **Router** (`app/routers/chat.py`) → usa `ChatService`
2. **ChatService** → facade que delega para `ChatOrchestrator`
3. **ChatOrchestrator** → classifica intenção e direciona para handlers
4. **IntentClassifier** → classifica a intenção do usuário
5. **Handlers específicos** → processam cada tipo de solicitação
6. **ChatSession** → mantém estado da conversa

## Benefícios

- ✅ **Separação clara de responsabilidades**
- ✅ **Modularidade e testabilidade**
- ✅ **Suporte a sessões persistentes**
- ✅ **Classificação inteligente de intenções**
- ✅ **Fácil extensão para novos tipos de intent**
- ✅ **Remoção de código duplicado**

## Próximos Passos

1. Implementar testes para os novos módulos
2. Integrar com frontend
3. Adicionar persistência de sessões (Redis/DB)
4. Documentar APIs atualizadas
