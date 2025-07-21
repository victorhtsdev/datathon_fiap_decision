# Backend - Datathon Decision

Este backend foi desenvolvido em Python utilizando FastAPI e SQLAlchemy, com foco em processamento de currículos, gestão de vagas, análise semântica e integração com LLMs.

## Principais APIs

- **Applicant**: Processamento e registro de candidatos.
- **Chat**: Interface conversacional com LLM para análise e filtragem de candidatos.
- **Processed Applicant**: Consulta e detalhamento de candidatos processados.
- **Prospects Match**: Associação de candidatos a vagas e workbooks.
- **Semantic Performance**: Análise de performance semântica dos algoritmos de busca.
- **Vaga**: Cadastro, atualização e processamento de vagas.
- **Workbook**: Gerenciamento de workbooks para agrupamento de vagas e candidatos.
- **Workbook Filters**: Filtros aplicados a workbooks.

## Instalação

1. Crie um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate    # Windows
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure o arquivo `.env` com as variáveis necessárias.
4. Execute o backend:
   ```bash
   uvicorn app.main:app --reload
   ```

## Estrutura de Pastas

- `app/routers/`: Endpoints das APIs
- `app/models/`: Modelos ORM
- `app/services/`: Lógica de negócio
- `app/schemas/`: Schemas Pydantic
- `app/core/`: Configurações, banco e utilitários
- `app/chat/`: Serviços de chat e integração LLM

## Exemplos de Uso

- Para consultar candidatos processados:
  ```http
  GET /processed-applicants
  ```
- Para conversar com o LLM:
  ```http
  POST /chat
  {
    "message": "Quais candidatos têm experiência em Python?"
  }
  ```

## Dependências
- Python 3.11+
- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn
- Outros (ver `requirements.txt`)

## Testes
Execute os testes com:
```bash
pytest
```

## Documentação
Acesse `/docs` para a documentação Swagger gerada automaticamente.
