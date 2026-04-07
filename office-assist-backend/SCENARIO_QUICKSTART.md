# Quick Start Guide: Scenario-Based Learning Feature

## Getting Started

### Prerequisites
- FastAPI server running (see QUICKSTART.md)
- Firestore enabled in GCP project
- Vertex AI Gemini 1.5 Pro access

### Step 1: Create Your First Scenario

```bash
curl -X POST "http://localhost:8000/scenarios/create" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Production Deployment Gone Wrong",
    "description": "A critical feature deployment caused data loss in production",
    "technical_context": "We were deploying version 2.1.0 to production at 3 PM EST. The migration script had a bug that deleted historical records instead of archiving them.",
    "company_solution": "1. Immediately rolled back deployment to previous version. 2. Restored from backup taken 4 hours prior (30 min data loss). 3. Fixed migration script and tested thoroughly. 4. Re-deployed with additional validation checks. 5. Implemented automated rollback triggers for future deployments.",
    "challenges_faced": "Time-sensitive decision making, customer communication during incident, data integrity concerns, team pressure",
    "lessons_learned": "Always test migrations with real data samples. Implement dry-run mode for migrations. Have automated rollback procedures. Schedule deployments during lower traffic periods. Maintain regular backup cadence.",
    "difficulty_level": "Hard",
    "category": "Technical",
    "tags": ["deployment", "database", "incident-response", "devops"]
  }'
```

**Response:**
```json
{
  "scenario_id": "abc123-uuid-here",
  "title": "Production Deployment Gone Wrong",
  "status": "created",
  "created_at": "2026-04-07T10:30:00Z"
}
```

Save the `scenario_id` for the next steps.

---

### Step 2: View Scenario for New Employee

New employee browses available scenarios:

```bash
curl "http://localhost:8000/scenarios?category=Technical"
```

Employee gets scenario details:

```bash
curl "http://localhost:8000/scenarios/abc123-uuid-here"
```

**Note:** Company solution is NOT returned at this stage. The employee only sees:
- Title
- Description
- Technical context
- Challenges faced
- Difficulty level
- Category

---

### Step 3: Employee Submits Their Solution

Employee develops their approach and submits:

```bash
curl -X POST "http://localhost:8000/scenarios/abc123-uuid-here/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_id": "abc123-uuid-here",
    "employee_id": "emp_john_doe",
    "employee_name": "John Doe",
    "solution_text": "When a deployment causes issues, I would: 1) Immediately inform the team and stakeholders that there is an incident. 2) Start investigating what went wrong by checking logs. 3) Look at the recent changes deployed. 4) If the issue is critical, roll back the deployment. 5) Fix the code and re-test before deploying again. 6) Consider if we need to restore data or just going forward is fine. 7) Document what went wrong so we can prevent similar issues."
  }'
```

**Response:**
```json
{
  "submission_id": "sub_xyz789",
  "scenario_id": "abc123-uuid-here",
  "employee_name": "John Doe",
  "score": 72,
  "approach_alignment": "Your approach covers the essential incident response steps and prioritizes immediate communication and investigation. However, it misses some critical operational details that our company learned through experience.",
  "strengths": [
    "Good instinct to immediately involve stakeholders",
    "Mentioned data restoration consideration",
    "Focused on documentation for future prevention"
  ],
  "gaps": [
    "Missing specific mention of rollback procedures and rollback time objectives",
    "Didn't specify testing requirements before re-deployment",
    "Lack of emphasis on preventing similar issues through infrastructure",
    "Didn't mention backup strategies that were critical to recovery"
  ],
  "feedback": "Your solution demonstrates solid incident response thinking. To improve: (1) Always have pre-tested rollback procedures ready - practice them regularly. (2) Implement automated migration testing with realistic data samples. (3) Use feature flags for gradual rollouts instead of big-bang deployments. (4) Maintain frequent backups and practice recovery procedures. (5) Establish automated health checks that can trigger rollbacks. Review the company's deployment playbook and incident response guidelines for detailed procedures.",
  "submitted_at": "2026-04-07T11:45:00Z"
}
```

---

### Step 4: Track Employee Progress

After employee has completed several scenarios, check their progress:

```bash
curl "http://localhost:8000/employee/emp_john_doe/progress"
```

**Response:**
```json
{
  "employee_id": "emp_john_doe",
  "total_tasks_completed": 3,
  "average_score": 70.67,
  "score_distribution": {
    "excellent": 0,
    "good": 1,
    "satisfactory": 2,
    "needs_improvement": 0,
    "insufficient": 0
  },
  "recent_submissions": [
    {
      "submission_id": "sub_xyz789",
      "scenario_id": "abc123-uuid-here",
      "score": 72,
      "submitted_at": "2026-04-07T11:45:00Z"
    }
  ],
  "progress_percentage": 15
}
```

---

### Step 5: View Team Performance

HR manager views team-wide analytics:

```bash
curl "http://localhost:8000/team/progress"
```

**Response:**
```json
{
  "total_employees": 12,
  "total_submissions": 28,
  "average_team_score": 71.43,
  "team_score_distribution": {
    "excellent": 2,
    "good": 9,
    "satisfactory": 12,
    "needs_improvement": 5,
    "insufficient": 0
  },
  "top_performers": [
    {
      "employee_id": "emp_sarah_smith",
      "name": "Sarah Smith",
      "avg_score": 86.5
    },
    {
      "employee_id": "emp_mike_johnson",
      "name": "Mike Johnson",
      "avg_score": 81.0
    }
  ]
}
```

---

## Real-World Workflow

### Week 1: Onboarding New Engineers

**Monday:**
1. Admin creates 3-5 key scenarios reflecting real situations company has faced
2. New hires get access to scenario library
3. New hires complete 1-2 easy scenarios on day 1

**Tuesday-Thursday:**
1. New hires work through medium-difficulty scenarios
2. Daily check-ins on their progress
3. Mentors can see scores and gaps to address in 1:1s

**Friday:**
1. New hires complete 1 hard scenario as capstone
2. Team reviews progress report
3. Areas for improvement identified

### Scenarios to Create

Based on your organization, create scenarios for:

1. **Technical Crises**
   - Production outage response
   - Security incident handling
   - Data corruption recovery
   - Deployment failures

2. **Project Management**
   - Scope creep management
   - Deadline pressure handling
   - Resource conflicts
   - Stakeholder management

3. **HR/Operations**
   - Conflict resolution
   - Performance issues
   - Compliance requirements
   - Budget constraints

4. **Customer Situations**
   - Difficult customer escalations
   - SLA violations
   - Feature request overload
   - Support ticket surge

---

## Testing the Feature Locally

### Quick Test Script

```bash
#!/bin/bash

# Set base URL
BASE_URL="http://localhost:8000"

# 1. Create a scenario
echo "Creating scenario..."
SCENARIO=$(curl -s -X POST "$BASE_URL/scenarios/create" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Scenario",
    "description": "Testing the feature",
    "technical_context": "This is a test",
    "company_solution": "Company did X, Y, and Z",
    "challenges_faced": "Time pressure",
    "lessons_learned": "Always test thoroughly",
    "difficulty_level": "Easy"
  }')

SCENARIO_ID=$(echo $SCENARIO | grep -o '"scenario_id":"[^"]*' | cut -d'"' -f4)
echo "Created scenario: $SCENARIO_ID"

# 2. Get scenarios
echo -e "\n\nGetting all scenarios..."
curl -s "$BASE_URL/scenarios" | python -m json.tool | head -30

# 3. Get scenario details
echo -e "\n\nGetting scenario details..."
curl -s "$BASE_URL/scenarios/$SCENARIO_ID" | python -m json.tool

# 4. Submit solution
echo -e "\n\nSubmitting solution..."
curl -s -X POST "$BASE_URL/scenarios/$SCENARIO_ID/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_id": "'$SCENARIO_ID'",
    "employee_id": "test_emp_001",
    "employee_name": "Test Employee",
    "solution_text": "I would handle it by doing A, then B, then C."
  }' | python -m json.tool

# 5. Check progress
echo -e "\n\nChecking employee progress..."
curl -s "$BASE_URL/employee/test_emp_001/progress" | python -m json.tool

# 6. Check team progress
echo -e "\n\nChecking team progress..."
curl -s "$BASE_URL/team/progress" | python -m json.tool
```

Save as `test_scenarios.sh`, make executable, and run:
```bash
chmod +x test_scenarios.sh
./test_scenarios.sh
```

---

## Troubleshooting

### Scenario Creation Fails
**Issue:** Error creating scenario: GCP_PROJECT_ID not set

**Solution:** Ensure `.env` file has:
```
GCP_PROJECT_ID=your-actual-project-id
```

### Submissions Not Appearing
**Issue:** Submitted solutions aren't returned in progress

**Solution:**
1. Verify Firestore is enabled in your GCP project
2. Check that `employee_id` values are consistent
3. Review firestore rules allow read/write to `submissions` collection

### Gemini API Errors
**Issue:** Error comparing solutions: API not available

**Solution:**
1. Ensure Gemini API is enabled in GCP project
2. Check service account has `Vertex AI` permissions
3. Verify `VERTEX_AI_LOCATION` in .env is set correctly

---

## Next Steps

1. **Create scenarios** from your real company experiences
2. **Set up for new hires** by adding scenarios to onboarding process
3. **Monitor progress** through the employee/team progress endpoints
4. **Refine scenarios** based on employee feedback and gaps observed
5. **Expand** with more categories and difficulty levels

See [SCENARIO_FEATURE.md](./SCENARIO_FEATURE.md) for complete API documentation.
