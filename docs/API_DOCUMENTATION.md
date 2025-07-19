# API Documentation

## Table of Contents
1. [Architecture & Standards](#architecture--standards)
2. [Authentication](#authentication)
3. [Endpoints](#endpoints)
   - [Workbooks](#workbooks)
   - [Match Prospects](#match-prospects)
   - [Vagas](#vagas)
   - [Applicants](#applicants)

## Architecture & Standards

### Schema Patterns
All entities follow a consistent schema pattern:

```python
# Base schema with common fields
class EntityBase(BaseModel):
    field1: str
    field2: Optional[str] = None

# Creation schema (inherits from Base)
class EntityCreate(EntityBase):
    pass

# Update schema (all fields optional for partial updates)
class EntityUpdate(BaseModel):
    field1: Optional[str] = None
    field2: Optional[str] = None

# Response schema (includes ID and timestamps)
class EntityResponse(EntityBase):
    id: int  # or UUID
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
```

### HTTP Status Codes
- `200 OK` - Successful GET, PUT requests
- `201 Created` - Successful POST requests
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict (e.g., already exists)
- `422 Unprocessable Entity` - Validation errors
- `500 Internal Server Error` - Server errors

---

## Endpoints

### Workbooks

#### List Workbooks
```http
GET /workbook
```

**Response:**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "vaga_id": 1,
    "criado_em": "2025-07-10T10:30:00",
    "fechado_em": null,
    "status": "aberto",
    "criado_por": "user@example.com"
  }
]
```

#### Create Workbook
```http
POST /workbook
```

**Request:**
```json
{
  "vaga_id": 1,
  "criado_por": "user@example.com"
}
```

#### Get Workbook
```http
GET /workbook/{workbook_id}
```

#### Update Workbook
```http
PUT /workbook/{workbook_id}
```

**Request:**
```json
{
  "status": "fechado",
  "fechado_em": "2025-07-10T15:30:00"
}
```

---

### Match Prospects

#### Update Match Prospects
```http
POST /workbook/{workbook_id}/match-prospects
```

Updates all match prospects for a workbook. This operation overwrites existing prospects.

**Request:**
```json
{
  "prospects": [
    {
      "applicant_id": 1001,
      "score_semantico": 0.85,
      "origem": "semantic_search", 
      "selecionado": false,
      "observacoes": "Strong technical background"
    },
    {
      "applicant_id": 1002,
      "score_semantico": 0.78,
      "origem": "manual_search",
      "selecionado": true,
      "observacoes": "Good cultural fit"
    }
  ]
}
```

**Response:**
```json
{
  "message": "Successfully updated 2 match prospects for workbook 123e4567-e89b-12d3-a456-426614174000",
  "workbook_id": "123e4567-e89b-12d3-a456-426614174000",
  "prospects_count": 2
}
```

#### Get Match Prospects
```http
GET /workbook/{workbook_id}/match-prospects
```

**Response:**
```json
[
  {
    "workbook_id": "123e4567-e89b-12d3-a456-426614174000",
    "applicant_id": 1001,
    "score_semantico": 0.85,
    "origem": "semantic_search",
    "selecionado": false,
    "data_entrada": "2025-07-10T10:30:00",
    "observacoes": "Strong technical background"
  }
]
```

**Important Notes:**
- The POST endpoint completely overwrites existing match prospects
- All fields except `applicant_id` are optional
- The `data_entrada` field is automatically set to the current timestamp

---

### Vagas

#### List Vagas
```http
GET /vagas/lista
```

#### Get Vaga Details
```http
GET /vagas/{vaga_id}
```

#### Process Vaga
```http
POST /vagas
```

---

### Applicants

#### Process Applicant
```http
POST /process_applicant/
```

#### List Processed Applicants
```http
GET /processed-applicants?skip=0&limit=100
```

#### Get Processed Applicant
```http
GET /processed-applicants/{applicant_id}
```

#### Update Processed Applicant
```http
PUT /processed-applicants/{applicant_id}
```

#### Search Applicants by Name
```http
GET /processed-applicants/search/by-name?name=João
```

#### Search Applicants by Education
```http
GET /processed-applicants/search/by-education?education_level=graduação
```

---

## Development Guidelines

### Error Handling
All endpoints return consistent error responses:

```json
{
  "detail": "Error message here"
}
```

### Validation
- Use Pydantic schemas for request/response validation
- Field validation with appropriate constraints
- Custom validators for business rules

### Testing
- Unit tests for services and repositories
- Integration tests for endpoints
- Use dependency injection for mocking

---

## Examples

### Complete Workflow: Creating a Workbook with Match Prospects

1. **Create Workbook:**
```bash
curl -X POST "http://localhost:8000/workbook" \
  -H "Content-Type: application/json" \
  -d '{
    "vaga_id": 1,
    "criado_por": "recruiter@company.com"
  }'
```

2. **Add Match Prospects:**
```bash
curl -X POST "http://localhost:8000/workbook/{workbook_id}/match-prospects" \
  -H "Content-Type: application/json" \
  -d '{
    "prospects": [
      {
        "applicant_id": 1001,
        "score_semantico": 0.85,
        "origem": "semantic_search",
        "selecionado": false,
        "observacoes": "Strong match"
      }
    ]
  }'
```

3. **Get Match Prospects:**
```bash
curl "http://localhost:8000/workbook/{workbook_id}/match-prospects"
```
