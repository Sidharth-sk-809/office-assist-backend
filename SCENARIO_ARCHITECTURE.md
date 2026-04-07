# Scenario Feature Architecture & Design

## System Design Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                      NEW EMPLOYEES / HR                             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                   HTTP Requests (FastAPI)
                    ├── /scenarios/create
                    ├── /scenarios
                    ├── /scenarios/{id}
                    ├── /scenarios/{id}/submit
                    ├── /employee/{id}/progress
                    └── /team/progress
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│                       FastAPI Main (main.py)                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ ✓ Request Validation (Pydantic Models)                      │   │
│  │ ✓ Error Handling (HTTPException)                            │   │
│  │ ✓ Logging & Monitoring                                      │   │
│  │ ✓ CORS Support                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                    Async Service Layer
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│            services/scenario_service.py                             │
│                                                                      │
│  Core Functions:                                                    │
│  ├─ create_scenario()                  → Store scenario data       │
│  ├─ get_all_scenarios()                → Query & filter scenarios  │
│  ├─ get_scenario_detail()              → Fetch scenario context   │
│  ├─ submit_scenario_solution()         → Process submission       │
│  ├─ _compare_solutions()               → AI-powered comparison    │
│  ├─ get_employee_progress()            → Calculate metrics        │
│  ├─ get_team_progress()                → Aggregate statistics     │
│  └─ _update_scenario_stats()           → Update averages         │
│                                                                      │
│  External Service Calls:                                            │
│  ├─ Vertex AI Gemini 1.5 Pro                                      │
│  │  └─ Compare solutions with AI analysis                         │
│  └─ Google Cloud Firestore                                        │
│     ├─ scenarios collection                                        │
│     └─ submissions collection                                      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │                                         │
   ┌────▼─────────┐                    ┌────────▼────────┐
   │ Firestore DB │                    │ Vertex AI (GCP) │
   │              │                    │                 │
   │ ├─ scenarios │                    │ ├─ Gemini 1.5   │
   │ └─ submissions│                    │ └─ LLM analysis │
   └──────────────┘                    └─────────────────┘
```

## Data Flow

### 1. Scenario Creation Flow

```
Admin Request
    │
    ▼
[main.py] Validate CreateScenarioRequest
    │
    ▼
[scenario_service.py] create_scenario()
    │
    ├─ Generate unique scenario_id (UUID)
    │
    ├─ Prepare scenario_data with metadata
    │  └─ title, description, company_solution, etc.
    │  └─ difficulty_level, category, tags
    │  └─ submission_count = 0, average_score = 0.0
    │
    ▼
[Firestore] db.collection("scenarios").document(scenario_id).set(scenario_data)
    │
    ▼
Return scenario_id + metadata to Admin
```

### 2. Solution Submission & Comparison Flow

```
Employee submits solution
    │
    ▼
[main.py] Validate SubmitScenarioSolutionRequest
    │ (employee_id, employee_name, solution_text)
    │
    ▼
[scenario_service.py] submit_scenario_solution()
    │
    ├─ Fetch scenario details from Firestore
    │
    ├─ Call _compare_solutions()
    │  │
    │  ├─ Build comparison prompt with:
    │  │  ├─ Scenario details (title, technical context, challenges)
    │  │  ├─ Company solution (lessons learned)
    │  │  └─ Employee solution
    │  │
    │  ▼
    │  [Vertex AI Gemini 1.5 Pro] generate_content(comparison_prompt)
    │  │
    │  │ AI Analysis:
    │  │ ├─ Score alignment (0-100)
    │  │ ├─ Approach assessment
    │  │ ├─ Strengths identification
    │  │ ├─ Gap analysis
    │  │ └─ Constructive feedback
    │  │
    │  ▼
    │  Parse JSON response
    │  │
    │  └─ Return comparison_result
    │
    ├─ Create submission_data record
    │  └─ submission_id (UUID), scores, feedback, timestamp
    │
    ├─ [Firestore] db.collection("submissions").document(submission_id).set(submission_data)
    │
    ├─ Call _update_scenario_stats()
    │  └─ Recalculate average_score and submission_count
    │
    └─ Return submission details to Employee
```

### 3. Progress Tracking Flow

```
GET /employee/{employee_id}/progress
    │
    ▼
[main.py] Validate employee_id
    │
    ▼
[scenario_service.py] get_employee_progress()
    │
    ├─ [Firestore] Query submissions collection
    │  └─ WHERE employee_id == requested_id
    │
    ├─ Aggregate statistics:
    │  ├─ total_scenarios_submitted (count)
    │  ├─ average_score (mean of all scores)
    │  ├─ Score distribution:
    │  │  ├─ Excellent (90-100)
    │  │  ├─ Good (75-89)
    │  │  ├─ Satisfactory (60-74)
    │  │  ├─ Needs Improvement (40-59)
    │  │  └─ Insufficient (<40)
    │  ├─ recent_submissions (last 5)
    │  └─ progress_percentage (submitted / 20 * 100)
    │
    └─ Return aggregated metrics
```

## Database Schema Details

### Collection: `scenarios`

**Purpose:** Store scenario definitions and metadata

```firestore
scenarios/
├── <scenario_id>
│   ├── scenario_id: string (UUID)
│   ├── title: string
│   ├── description: string (brief intro)
│   ├── technical_context: string (detailed background)
│   ├── company_solution: string (full company solution - NOT shown to employees initially)
│   ├── challenges_faced: string  
│   ├── lessons_learned: string
│   ├── difficulty_level: string (enum: "Easy", "Medium", "Hard")
│   ├── category: string (e.g., "Technical", "HR", "Project Management")
│   ├── tags: array of strings
│   ├── created_at: timestamp
│   ├── updated_at: timestamp
│   ├── submission_count: number (total submissions received)
│   └── average_score: number (running average of all submission scores)
```

**Indices needed:**
- Composite: `(category, created_at DESC)`
- Composite: `(difficulty_level, created_at DESC)`

### Collection: `submissions`

**Purpose:** Store employee solution submissions and comparison results

```firestore
submissions/
├── <submission_id>
│   ├── submission_id: string (UUID)
│   ├── scenario_id: string (FK → scenarios)
│   ├── employee_id: string (organizationally unique)
│   ├── employee_name: string
│   ├── employee_solution: string (full submission text)
│   ├── comparison_score: number (0-100)
│   ├── approach_alignment: string (AI assessment of alignment)
│   ├── strengths: array of strings (AI-identified strengths)
│   ├── gaps: array of strings (AI-identified gaps)
│   ├── feedback: string (detailed AI feedback)
│   ├── submitted_at: timestamp
│   └── updated_at: timestamp
```

**Indices needed:**
- Single: `employee_id`
- Single: `scenario_id`
- Composite: `(employee_id, submitted_at DESC)`
- Composite: `(scenario_id, comparison_score DESC)`

## Error Handling Strategy

```
Request
    │
    ▼
[FastAPI Validation]
    │
    ├─ ✗ Invalid format/missing fields
    │  └─ → 400 Bad Request
    │
    ├─ ✗ Unauthorized/missing auth
    │  └─ → 401 Unauthorized (future enhancement)
    │
    └─ ✓ Valid request
        │
        ▼
    [Service Layer Processing]
        │
        ├─ ✗ Resource not found (scenario_id doesn't exist)
        │  └─ → 404 Not Found
        │
        ├─ ✗ GCP service error (Firestore down, Gemini API error)
        │  └─ → 500 Internal Server Error (with details)
        │
        ├─ ✗ Validation error (invalid employee_id format)
        │  └─ → 400 Bad Request
        │
        └─ ✓ Success
            └─ → 200 OK + response body
```

## Scoring Algorithm

The Gemini-based comparison uses this rubric:

```
Score Determination (0-100 scale):

1. Problem Understanding (20 points)
   - Does employee understand the scenario context?
   - Are root causes identified correctly?

2. Solution Approach (30 points)
   - How similar is approach to company solution?
   - Are critical steps included?
   - Is the sequence logical?

3. Depth & Completeness (25 points)
   - Are details specific or vague?
   - What about edge cases, error scenarios?
   - Post-incident/follow-up actions?

4. Best Practices (15 points)
   - Does solution align with company values?
   - Are lessons learned from past incorporated?
   - Scalability, sustainability?

5. Communication (10 points)
   - Is explanation clear and well-organized?
   - Realistic timeline and dependencies?
```

## Performance Considerations

### Read Performance
- **Scenario listings:** Indexed by category + created_at
- **Employee progress:** Single employee_id index (typically <50 submissions per employee)
- **Team progress:** Full collection scan (acceptable, run async/nightly)

### Write Performance
- **Scenario creation:** Single document write
- **Submission:** 2-3 document writes (submission + scenario update)
- **Stats update:** Eventual consistency acceptable

### Query Optimization
```
// Good (indexed)
db.collection("submissions")
  .where("employee_id", "==", "emp_123")
  .orderBy("submitted_at", "DESC")

// Avoid (requires full scan)
db.collection("submissions")
  .where("comparison_score", ">", 75)
  .orderBy("employee_id")
```

## Integration Points

### With Existing Systems

#### 1. RAG Chat (`/chat` endpoint)
- Scenarios can reference company materials in chat
- Employees can ask clarifying questions about policies
- Example: "What's our incident response SLA?" while solving scenario

#### 2. Task Grading (`/submit-task` endpoint)
- Similar grading paradigm
- Can combine scenario scores with task scores for holistic view
- Reuses Firestore storage

#### 3. Resume Classification (`/classify` endpoint)
- Can recommend scenario difficulty based on resume level
- Junior employees → Easy/Medium scenarios first

## Future Extensibility

### Planned Enhancements

1. **Multi-round Scenarios**
   - Scenario evolves based on employee decision
   - Branching decision trees
   - "Choose your own adventure" style learning

2. **Peer Comparisons**
   - Show how other employees solved same scenario
   - Learn from peer approaches
   - Community best practices

3. **Department-specific Scenarios**
   - Filter by department/team
   - Role-based difficulty recommendations

4. **Time-based Metrics**
   - Track solution development time
   - Identify struggling employees for support

5. **Continuous Learning Path**
   - Prerequisite scenarios
   - Learning outcomes mapping
   - Competency tracking

## Security Considerations

### Current Implementation
- Assumes authentication at API gateway level
- No per-user access control on scenarios (all employees see all scenarios)

### Recommended Future Enhancements
```python
# Validate employee authorization
@app.get("/scenarios/{scenario_id}/submit")
async def submit_solution(scenario_id: str, current_user: User = Depends(get_current_user)):
    # Verify user is active employee
    if not is_active_employee(current_user.id):
        raise HTTPException(403, "Only active employees")
    # ... rest
```

### Data Privacy
- Employee solutions stored in Firestore (not exposed to other employees by default)
- Aggregate metrics don't show individual names unless in top performers view
- Comply with data retention policies (e.g., delete after employee departure)

## Deployment Checklist

- [ ] Firestore collections created with proper indexes
- [ ] Vertex AI Gemini API enabled in GCP
- [ ] Service account has required permissions
- [ ] `.env` variables set correctly
- [ ] Error handling tested for GCP outages
- [ ] Load testing for concurrent submissions
- [ ] Backup strategy for Firestore data
- [ ] Monitoring and alerting configured
- [ ] API documentation deployed
