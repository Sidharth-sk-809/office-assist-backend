# API Endpoints Reference

All Office Assist API endpoints with quick reference for developers.

## Base URL
```
http://localhost:8000
```

---

## Health & Status

### GET `/`
Health check endpoint
- **Response:** `{"status": "healthy", "service": "Office Assist API"}`

---

## Resume Classification

### POST `/classify`
Classify resume PDF by experience level

**Request:**
```
Content-Type: multipart/form-data
file: <PDF file>
```

**Response:** `200 OK`
```json
{
  "level": "Senior",
  "confidence": 0.85,
  "reasoning": "8+ years experience with leadership..."
}
```

---

## Policy Chat (RAG)

### POST `/chat`
Query company policies using RAG

**Request:** `Content-Type: application/json`
```json
{
  "user_input": "What is the vacation policy?",
  "conversation_id": "optional-uuid"
}
```

**Response:** `200 OK`
```json
{
  "answer": "The company offers 15 days of PTO annually...",
  "sources": [
    {"title": "Employee Handbook", "uri": "gs://..."}
  ],
  "conversation_id": "uuid"
}
```

---

## Task Grading

### POST `/submit-task`
Grade task submission against rubric

**Request:** `Content-Type: multipart/form-data`
```
task_text: "My solution..."  (optional if file provided)
file: <file>                 (optional if task_text provided)
```

**Response:** `200 OK`
```json
{
  "task_id": "uuid",
  "score": 82,
  "feedback": "Good solution with...",
  "timestamp": "2026-04-07T..."
}
```

---

## Material Upload

### POST `/upload-material`
Upload training material to GCS

**Request:** `Content-Type: multipart/form-data`
```
file: <PDF file>
```

**Response:** `200 OK`
```json
{
  "filename": "training.pdf",
  "gcs_uri": "gs://bucket/training.pdf",
  "status": "uploaded",
  "message": "Will be indexed within 10-30 minutes"
}
```

---

## ✨ Scenario-Based Learning (NEW)

### POST `/scenarios/create`
Create new learning scenario

**Request:** `Content-Type: application/json`
```json
{
  "title": "Production Outage Response",
  "description": "How to handle and recover from outage",
  "technical_context": "Production server with 5000 users down...",
  "company_solution": "Company solved by...",
  "challenges_faced": "Time pressure, customer impact...",
  "lessons_learned": "Better monitoring, backup procedures...",
  "difficulty_level": "Hard",
  "category": "Technical",
  "tags": ["incident-response", "devops"]
}
```

**Response:** `200 OK`
```json
{
  "scenario_id": "uuid",
  "title": "Production Outage Response",
  "status": "created",
  "created_at": "2026-04-07T..."
}
```

---

### GET `/scenarios`
List available scenarios with filtering

**Query Parameters:**
- `category` (optional): e.g., "Technical"
- `difficulty_level` (optional): "Easy", "Medium", "Hard"
- `skip` (optional, default=0): Pagination offset
- `limit` (optional, default=10): Results per page

**Example:**
```
GET /scenarios?category=Technical&difficulty_level=Hard&skip=0&limit=10
```

**Response:** `200 OK`
```json
{
  "scenarios": [
    {
      "scenario_id": "uuid",
      "title": "Production Outage Response",
      "description": "How to handle outages...",
      "category": "Technical",
      "difficulty_level": "Hard",
      "submission_count": 12,
      "average_score": 72.5,
      "tags": ["incident-response"]
    }
  ],
  "total_count": 25,
  "skip": 0,
  "limit": 10
}
```

---

### GET `/scenarios/{scenario_id}`
Get specific scenario details

**Path Parameters:**
- `scenario_id`: UUID of scenario

**Response:** `200 OK`
```json
{
  "scenario_id": "uuid",
  "title": "Production Outage Response",
  "description": "How to handle and recover from outage",
  "technical_context": "Production server...",
  "challenges_faced": "Time pressure...",
  "difficulty_level": "Hard",
  "category": "Technical",
  "tags": ["incident-response", "devops"]
}
```

---

### POST `/scenarios/{scenario_id}/submit`
Submit solution and get AI comparison

**Path Parameters:**
- `scenario_id`: UUID of scenario

**Request:** `Content-Type: application/json`
```json
{
  "scenario_id": "uuid",
  "employee_id": "emp_12345",
  "employee_name": "John Doe",
  "solution_text": "I would handle it by..."
}
```

**Response:** `200 OK`
```json
{
  "submission_id": "uuid",
  "scenario_id": "uuid",
  "employee_name": "John Doe",
  "score": 78,
  "approach_alignment": "Good coverage of main steps...",
  "strengths": [
    "Correctly identified failover need",
    "Good stakeholder communication"
  ],
  "gaps": [
    "Missing rollback procedure",
    "No mention of backup verification"
  ],
  "feedback": "Your solution demonstrates solid thinking. Key improvements...",
  "submitted_at": "2026-04-07T11:45:00Z"
}
```

---

### GET `/employee/{employee_id}/progress`
Get individual employee progress

**Path Parameters:**
- `employee_id`: Employee's unique identifier

**Response:** `200 OK`
```json
{
  "employee_id": "emp_12345",
  "total_tasks_completed": 8,
  "average_score": 74.5,
  "score_distribution": {
    "excellent": 1,
    "good": 3,
    "satisfactory": 3,
    "needs_improvement": 1,
    "insufficient": 0
  },
  "recent_submissions": [
    {
      "submission_id": "uuid",
      "scenario_id": "uuid",
      "score": 78,
      "submitted_at": "2026-04-07T11:45:00Z"
    }
  ],
  "progress_percentage": 40
}
```

---

### GET `/team/progress`
Get team-wide performance statistics

**Response:** `200 OK`
```json
{
  "total_employees": 25,
  "total_submissions": 156,
  "average_team_score": 71.3,
  "team_score_distribution": {
    "excellent": 12,
    "good": 48,
    "satisfactory": 72,
    "needs_improvement": 20,
    "insufficient": 4
  },
  "top_performers": [
    {
      "employee_id": "emp_001",
      "name": "Alice Johnson",
      "avg_score": 88.5
    }
  ]
}
```

---

## Error Responses

### 400 Bad Request
```json
{"error": "Scenario title cannot be empty"}
```

### 404 Not Found
```json
{"error": "Scenario abc123 not found"}
```

### 500 Internal Server Error
```json
{"error": "Failed to create scenario: GCP service error"}
```

---

## Quick cURL Examples

### Create Scenario
```bash
curl -X POST http://localhost:8000/scenarios/create \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Scenario",
    "description": "Testing feature",
    "technical_context": "Test context",
    "company_solution": "Test solution",
    "challenges_faced": "Test challenges",
    "lessons_learned": "Test lessons"
  }'
```

### Get All Scenarios
```bash
curl http://localhost:8000/scenarios
```

### Get Scenario Details
```bash
curl http://localhost:8000/scenarios/{scenario_id}
```

### Submit Solution
```bash
curl -X POST http://localhost:8000/scenarios/{scenario_id}/submit \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_id": "{scenario_id}",
    "employee_id": "emp_123",
    "employee_name": "John Doe",
    "solution_text": "My solution approach..."
  }'
```

### Get Employee Progress
```bash
curl http://localhost:8000/employee/emp_123/progress
```

### Get Team Progress
```bash
curl http://localhost:8000/team/progress
```

---

## Status Codes Reference

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error - GCP/Service issue |

---

## Testing

Run the test suite:
```bash
python test_scenarios.py
```

This will test all endpoints and report results.

---

## Documentation

For detailed information:
- [Features & Scoring Rubric](./SCENARIO_FEATURE.md)
- [Quick Start Guide](./SCENARIO_QUICKSTART.md)
- [Architecture & Design](./SCENARIO_ARCHITECTURE.md)
- [Example Scenarios](./SCENARIO_EXAMPLES.md)
- [Implementation Summary](./SCENARIO_IMPLEMENTATION_SUMMARY.md)

---

## Rate Limiting

Currently no rate limiting is implemented. Recommended for production:
- Scenario creation: 10 req/min per user
- Submissions: 5 req/min per user
- Progress queries: 30 req/min per user

---

## Authentication

Currently assumes authentication at API gateway level. Recommended for production:
- Implement JWT token validation
- Add user/employee ID verification
- Implement role-based access control
