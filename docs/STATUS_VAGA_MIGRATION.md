# Migração do Campo vaga_ativa para status_vaga

## Resumo das Alterações

O campo `vaga_ativa` (Boolean) foi substituído pelo campo `status_vaga` (Enum) para suportar múltiplos estados de uma vaga.

### Novos Status Disponíveis

- **`nao_iniciada`**: Estado inicial da vaga (padrão)
- **`em_andamento`**: Vaga sendo processada/workbook iniciado
- **`finalizada`**: Processamento concluído

## Alterações Implementadas

### 1. Backend

#### Modelo de Dados (`app/models/vaga.py`)
```python
# Antes
vaga_ativa = Column(Boolean, default=True)

# Depois
class StatusVaga(enum.Enum):
    nao_iniciada = "nao_iniciada"
    em_andamento = "em_andamento"
    finalizada = "finalizada"

status_vaga = Column(Enum(StatusVaga), default=StatusVaga.nao_iniciada)
```

#### Schemas (`app/schemas/vaga.py`)
```python
class StatusVaga(str, Enum):
    nao_iniciada = "nao_iniciada"
    em_andamento = "em_andamento"
    finalizada = "finalizada"

# Nos schemas VagaBase, VagaCreate, VagaUpdate, VagaInDB
status_vaga: Optional[StatusVaga] = StatusVaga.nao_iniciada
```

#### Router (`app/routers/vaga.py`)
- Endpoint `/vagas/lista` agora retorna `status_vaga` ao invés de `vaga_ativa`
- Filtro `apenas_ativas=true` agora considera vagas com status `nao_iniciada` e `em_andamento`

#### Orquestrador (`app/services/vaga_processing_orchestrator.py`)
- Atualiza status para `em_andamento` quando inicia processamento
- Atualiza status para `finalizada` quando termina processamento

### 2. Frontend

#### Types (`frontend/src/types/api.ts`)
```typescript
export type StatusVaga = 'nao_iniciada' | 'em_andamento' | 'finalizada';

export interface Vaga {
  id: number;
  informacoes_basicas_titulo_vaga: string;
  status_vaga: StatusVaga;
}
```

#### Componentes (`frontend/src/components/VagaCard.tsx`)
- Exibe badge colorido baseado no status
- Cores: cinza (não iniciada), azul (em andamento), verde (finalizada)

## API - Exemplos de Uso

### Criar Vaga com Status Específico

```bash
# Criar vaga não iniciada (padrão)
curl -X POST "http://localhost:8000/vagas" \
     -H "Content-Type: application/json" \
     -d '{
       "id": 123,
       "informacoes_basicas_titulo_vaga": "Desenvolvedor Full Stack",
       "status_vaga": "nao_iniciada"
     }'

# Criar vaga em andamento
curl -X POST "http://localhost:8000/vagas" \
     -H "Content-Type: application/json" \
     -d '{
       "id": 124,
       "informacoes_basicas_titulo_vaga": "Analista de Dados", 
       "status_vaga": "em_andamento"
     }'
```

### Listar Vagas

```bash
# Listar apenas vagas ativas (nao_iniciada + em_andamento)
curl "http://localhost:8000/vagas/lista?apenas_ativas=true"

# Listar todas as vagas
curl "http://localhost:8000/vagas/lista?apenas_ativas=false"
```

### Resposta da API

```json
[
  {
    "id": 123,
    "informacoes_basicas_titulo_vaga": "Desenvolvedor Full Stack",
    "status_vaga": "nao_iniciada"
  },
  {
    "id": 124,
    "informacoes_basicas_titulo_vaga": "Analista de Dados",
    "status_vaga": "em_andamento"
  }
]
```

## Migração de Dados

### Script de Migração

Execute o script `scripts/migrate_vaga_status.py` para migrar dados existentes:

```bash
python scripts/migrate_vaga_status.py
```

O script:
1. Adiciona a coluna `status_vaga` se não existir
2. Migra dados: `vaga_ativa = true` → `status_vaga = 'nao_iniciada'`
3. Migra dados: `vaga_ativa = false` → `status_vaga = 'finalizada'`
4. Mantém a coluna `vaga_ativa` por segurança (remova manualmente depois)

### Remoção Manual da Coluna Antiga

Após confirmar que tudo funciona, remova a coluna antiga:

```sql
ALTER TABLE vagas DROP COLUMN vaga_ativa;
```

## Testes

Execute o script de testes para validar a funcionalidade:

```bash
python scripts/test_status_vaga.py
```

O script testa:
- Listagem de vagas com novo campo
- Criação de vagas com diferentes status
- Filtros de vagas ativas
- Validação de dados

## Fluxo Automático de Status

1. **Criação**: Vaga criada com `status_vaga = "nao_iniciada"`
2. **Processamento**: Ao iniciar processamento → `status_vaga = "em_andamento"`
3. **Conclusão**: Ao finalizar processamento → `status_vaga = "finalizada"`

## Retrocompatibilidade

⚠️ **BREAKING CHANGE**: O campo `vaga_ativa` não existe mais. 

Aplicações que dependem do campo `vaga_ativa` precisam ser atualizadas para usar `status_vaga`.

## Checklist de Migração

- [x] Atualizar modelo de dados (StatusVaga enum)
- [x] Atualizar schemas (Pydantic)
- [x] Atualizar router (endpoint lista)
- [x] Atualizar orquestrador (controle automático de status)
- [x] Atualizar frontend (types e componentes)
- [x] Criar script de migração de dados
- [x] Criar script de testes
- [x] Atualizar documentação
- [ ] Executar migração em produção
- [ ] Remover coluna vaga_ativa após validação
- [ ] Atualizar outras aplicações dependentes
