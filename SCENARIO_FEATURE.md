# Scenario-Based Learning Feature

## Overview

The Scenario-Based Learning Feature enables organizations to provide new employees with real-world case studies from their company. Employees solve these scenarios and receive AI-powered feedback comparing their solutions with the company's proven approaches. This feature includes comprehensive task tracking and progress monitoring.

## Key Features

### 1. **Scenario Management**
- Create and store company scenarios/case studies
- Organize scenarios by category and difficulty level
- Tag scenarios for easy filtering
- Track submission metrics per scenario

### 2. **Solution Comparison**
- Employees submit their proposed solutions
- AI (Gemini 1.5 Pro) compares solutions with company-verified approaches
- Provides detailed feedback on:
  - Approach alignment
  - Strengths of the solution
  - Gaps compared to company solution
  - Overall score (0-100)

### 3. **RAG Integration**
- Scenarios are indexed and can be queried using the existing RAG/Vertex AI Search
- Employees can reference company policies and materials when solving scenarios
- Context-aware feedback based on company knowledge base

### 4. **Task Progress Tracking**
- Individual employee progress dashboard
- Team-wide performance analytics
- Top performer rankings
- Score distribution analysis

## Database Schema (Firestore)

### Collections

#### `scenarios`
```json
{
  "scenario_id": "uuid",
  "title": "String",
  "description": "String",
  "technical_context": "String",
  "company_solution": "String",
  "challenges_faced": "String",
  "lessons_learned": "String",
  "difficulty_level": "Easy|Medium|Hard",
  "category": "String",
  "tags": ["String"],
  "created_at": "Timestamp",
  "updated_at": "Timestamp",
  "submission_count": "Number",
  "average_score": "Float"
}
```

#### `submissions`
```json
{
  "submission_id": "uuid",
  "scenario_id": "uuid",
  "employee_id": "String",
  "employee_name": "String",
  "employee_solution": "String",
  "comparison_score": "Float (0-100)",
  "approach_alignment": "String",
  "strengths": ["String"],
  "gaps": ["String"],
  "feedback": "String",
  "submitted_at": "Timestamp",
  "updated_at": "Timestamp"
}
```

## API Endpoints

### 1. Create Scenario
**POST** `/scenarios/create`

Creates a new scenario for employee learning.

**Request Body:**
```json
{
  "title": "Critical Server Outage Response",
  "description": "How to handle and recover from a production server outage",
  "technical_context": "Production server with 5000 concurrent users went down due to memory leak",
  "company_solution": "Immediately switched to backup servers, identified memory leak in service X, patched and deployed hotfix...",
  "challenges_faced": "Time pressure, customer impact, monitoring gaps",
  "lessons_learned": "Implement better monitoring, have tested backup procedures, maintain incident runbook",
  "difficulty_level": "Hard",
  "category": "Technical",
  "tags": ["infrastructure", "incident-response", "devops"]
}
```

**Response:**
```json
{
  "scenario_id": "uuid",
  "title": "Critical Server Outage Response",
  "status": "created",
  "created_at": "2026-04-07T10:30:00Z"
}
```

---

### 2. Get All Scenarios
**GET** `/scenarios?category=Technical&difficulty_level=Hard&skip=0&limit=10`

Retrieves available scenarios with optional filtering.

**Query Parameters:**
- `category` (optional): Filter by category
- `difficulty_level` (optional): Filter by difficulty
- `skip` (optional, default=0): Pagination offset
- `limit` (optional, default=10): Number of results

**Response:**
```json
{
  "scenarios": [
    {
      "scenario_id": "uuid",
      "title": "Critical Server Outage Response",
      "description": "How to handle and recover from outages...",
      "category": "Technical",
      "difficulty_level": "Hard",
      "submission_count": 12,
      "average_score": 72.5,
      "tags": ["infrastructure", "incident-response"]
    }
  ],
  "total_count": 25,
  "skip": 0,
  "limit": 10
}
```

---

### 3. Get Scenario Details
**GET** `/scenarios/{scenario_id}`

Retrieves complete details of a specific scenario (without company solution - employees solve first).

**Response:**
```json
{
  "scenario_id": "uuid",
  "title": "Critical Server Outage Response",
  "description": "How to handle and recover from outages",
  "technical_context": "Production server with 5000 concurrent users went down...",
  "challenges_faced": "Time pressure, customer impact, monitoring gaps",
  "difficulty_level": "Hard",
  "category": "Technical",
  "tags": ["infrastructure", "incident-response"]
}
```

---

### 4. Submit Scenario Solution
**POST** `/scenarios/{scenario_id}/submit`

Submit employee solution and receive AI-powered comparison with company solution.

**Request Body:**
```json
{
  "scenario_id": "uuid",
  "employee_id": "emp_12345",
  "employee_name": "John Doe",
  "solution_text": "First, I would identify the root cause by checking logs and metrics. Then notify the stakeholders. Switch to backup infrastructure temporarily..."
}
```

**Response:**
```json
{
  "submission_id": "uuid",
  "scenario_id": "uuid",
  "employee_name": "John Doe",
  "score": 78,
  "approach_alignment": "The approach is good and covers main incident response steps. However, lacks specific detail about monitoring setup.",
  "strengths": [
    "Correctly identified need for immediate failover",
    "Good communication of incident progress",
    "Thought about long-term prevention"
  ],
  "gaps": [
    "Missing specific monitoring checks before production deployment",
    "Didn't mention rollback plan",
    "Post-incident review process not detailed"
  ],
  "feedback": "Your solution demonstrates solid incident response fundamentals. Key areas to improve: (1) Always have a detailed rollback strategy before deploying any changes, (2) Implement automated health checks for rapid detection, (3) Document incident learnings in a post-mortem. Review company's incident runbook for best practices.",
  "submitted_at": "2026-04-07T11:45:00Z"
}
```

---

### 5. Get Employee Progress
**GET** `/employee/{employee_id}/progress`

Get individual employee's task completion progress and performance metrics.

**Response:**
```json
{
  "employee_id": "emp_12345",
  "total_tasks_completed": 8,
  "average_score": 74.5,
  "score_distribution": {
    "excellent": 1,      // 90-100
    "good": 3,           // 75-89
    "satisfactory": 3,   // 60-74
    "needs_improvement": 1,  // 40-59
    "insufficient": 0    // <40
  },
  "recent_submissions": [
    {
      "submission_id": "uuid",
      "scenario_id": "uuid",
      "score": 78,
      "submitted_at": "2026-04-07T11:45:00Z"
    }
  ],
  "progress_percentage": 40  // (8/20) * 100
}
```

---

### 6. Get Team Progress
**GET** `/team/progress`

Get team-wide performance statistics and top performers.

**Response:**
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
    },
    {
      "employee_id": "emp_002",
      "name": "Bob Smith",
      "avg_score": 85.2
    }
  ]
}
```

---

## Scoring Rubric

Solutions are scored on a 0-100 scale based on alignment with company solution:

| Score Range | Category | Interpretation |
|---|---|---|
| 90-100 | Excellent | Matches or exceeds company solution |
| 75-89 | Good | Covers main points with minor gaps |
| 60-74 | Satisfactory | Addresses core issues but lacks depth |
| 40-59 | Needs Improvement | Missing important aspects |
| <40 | Insufficient | Fundamentally misses key points |

## Usage Examples

### Example 1: Administrator creating a scenario

```bash
curl -X POST "http://localhost:8000/scenarios/create" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Customer Data Breach Response",
    "description": "Handling a discovered security breach in customer data",
    "technical_context": "Database query monitoring detected unusual access patterns to customer PII table",
    "company_solution": "Step 1: Isolate affected database immediately. Step 2: Notify security team and legal. Step 3: Audit all access logs...",
    "challenges_faced": "Time sensitivity, legal implications, customer notification requirements",
    "lessons_learned": "Maintain detailed audit logs, have incident response procedures documented, regular security drills",
    "difficulty_level": "Hard",
    "category": "Security",
    "tags": ["security", "incident-response", "compliance"]
  }'
```

### Example 2: New employee browsing scenarios

```bash
# Get available scenarios
curl "http://localhost:8000/scenarios?category=Technical&difficulty_level=Medium&skip=0&limit=5"

# Get details of a specific scenario
curl "http://localhost:8000/scenarios/{scenario_id}"
```

### Example 3: Employee submitting solution

```bash
curl -X POST "http://localhost:8000/scenarios/{scenario_id}/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_id": "{scenario_id}",
    "employee_id": "emp_456",
    "employee_name": "Sarah Williams",
    "solution_text": "Upon detecting unusual access patterns, I would: 1) Immediately notify the security team, 2) Preserve all audit logs, 3) Assess scope of breach, 4) Begin customer notification process following legal requirements..."
  }'
```

### Example 4: Tracking progress

```bash
# Get individual progress
curl "http://localhost:8000/employee/emp_456/progress"

# Get team progress
curl "http://localhost:8000/team/progress"
```

## Integration with Existing Systems

### RAG/Chat Integration
- Scenarios can be uploaded to Vertex AI Search datastore for discovery
- Employees can reference company policies while solving scenarios via the `/chat` endpoint
- Company materials automatically included in scenario context

### Task Grading Integration
- Submission scoring uses Gemini 1.5 Pro (similar to existing task grading)
- Combines scenario comparison with employment readiness evaluation
- Results stored in Firestore alongside traditional task submissions

## Environment Variables Required

Add to `.env`:
```bash
GCP_PROJECT_ID=your-project-id
VERTEX_AI_LOCATION=us-central1
GCS_BUCKET_NAME=your-bucket-name
```

## Future Enhancements

1. **Multi-round scenarios**: Employees solve step-by-step scenarios with progressive challenges
2. **Peer comparison**: Show how other employees solved the same scenario
3. **Scenario versioning**: Track changes to scenarios over time
4. **Solution annotations**: Allow managers to add notes to employee submissions
5. **Competency mapping**: Link scenarios to specific job competencies
6. **Gamification**: Badges, leaderboards, and achievement tracking
7. **Export reports**: Detailed analytics and performance reports
