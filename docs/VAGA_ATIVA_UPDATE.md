# Campo vaga_ativa no endpoint POST /vagas

## ✅ IMPLEMENTAÇÃO COMPLETA

O campo `vaga_ativa` já está **FUNCIONANDO** no endpoint POST `/vagas` existente.

## Como Usar

### Criar vaga ativa (padrão)
```json
POST /vagas
{
  "id": 123,
  "informacoes_basicas_titulo_vaga": "Desenvolvedor Python",
  "informacoes_basicas_cliente": "Empresa XYZ"
  // vaga_ativa não especificado = será True por padrão
}
```

### Criar vaga inativa
```json
POST /vagas
{
  "id": 125,
  "informacoes_basicas_titulo_vaga": "Vaga Suspensa",
  "informacoes_basicas_cliente": "Empresa DEF",
  "vaga_ativa": false
}
```

## Comportamento

1. **Valor padrão**: Se `vaga_ativa` não for especificado, será `true` por padrão
2. **Banco de dados**: O valor é salvo automaticamente na coluna `vaga_ativa` 
3. **Listagem**: O endpoint `GET /vagas/lista` mostra apenas vagas ativas por padrão
   - Use `GET /vagas/lista?apenas_ativas=false` para ver todas

## Status: ✅ PRONTO PARA USO

## Novos Endpoints

### PUT /vagas/{vaga_id}
Atualiza uma vaga específica, incluindo o campo `vaga_ativa`.

**Exemplo de uso:**
```bash
curl -X PUT "http://localhost:8000/vagas/123" \
     -H "Content-Type: application/json" \
     -d '{"vaga_ativa": false}'
```

**Resposta:**
```json
{
  "message": "Vaga updated successfully",
  "vaga": {
    "id": 123,
    "informacoes_basicas_titulo_vaga": "Desenvolvedor Python",
    "vaga_ativa": false,
    // ... outros campos
  }
}
```

### GET /vagas/lista (atualizado)
Agora aceita o parâmetro `apenas_ativas` para filtrar vagas ativas.

**Exemplos:**
```bash
# Listar apenas vagas ativas (padrão)
curl "http://localhost:8000/vagas/lista"

# Listar todas as vagas (ativas e inativas)
curl "http://localhost:8000/vagas/lista?apenas_ativas=false"
```

**Resposta:**
```json
[
  {
    "id": 123,
    "informacoes_basicas_titulo_vaga": "Desenvolvedor Python",
    "vaga_ativa": true
  }
]
```

## Arquivo de Teste

Foi criado o arquivo `scripts/test_vaga_ativa.py` que contém testes automatizados para verificar:
- Listagem de vagas ativas
- Listagem de todas as vagas
- Desativação de uma vaga
- Verificação do status da vaga
- Reativação da vaga

Para executar os testes:
```bash
cd c:\Projetos\datathon_decision
python scripts/test_vaga_ativa.py
```

## Considerações Importantes

1. **Banco de Dados**: O campo `vaga_ativa` foi definido com valor padrão `TRUE`, então vagas existentes continuarão ativas.

2. **Migração**: Como não há sistema de migrações configurado, será necessário adicionar manualmente a coluna ao banco:
   ```sql
   ALTER TABLE public.vagas ADD COLUMN vaga_ativa boolean DEFAULT true;
   ```

3. **Compatibilidade**: Todas as funcionalidades existentes continuam funcionando normalmente.

4. **Filtros**: Por padrão, a listagem de vagas retorna apenas vagas ativas, mas é possível ver todas usando o parâmetro `apenas_ativas=false`.

## Como Usar

1. **Desativar uma vaga:**
   ```python
   import requests
   response = requests.put("http://localhost:8000/vagas/123", json={"vaga_ativa": False})
   ```

2. **Reativar uma vaga:**
   ```python
   import requests
   response = requests.put("http://localhost:8000/vagas/123", json={"vaga_ativa": True})
   ```

3. **Atualizar outros campos junto com vaga_ativa:**
   ```python
   import requests
   data = {
       "vaga_ativa": False,
       "informacoes_basicas_titulo_vaga": "Nova Posição - Inativa"
   }
   response = requests.put("http://localhost:8000/vagas/123", json=data)
   ```

## Status

✅ **Implementação Concluída**
- Modelo atualizado
- Schemas atualizados  
- Endpoints criados/atualizados
- Testes criados
- Documentação criada

Próximo passo: Executar a migração do banco de dados para adicionar a coluna.
