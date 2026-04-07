# Frontend Implementation Prompt: Task-Based Training Feature for New Joiners

## Executive Summary

Implement a task-based learning platform on the frontend that allows new employees to:
1. Browse and discover real-world company scenarios
2. Solve scenarios independently
3. Receive AI-powered feedback comparing their solutions with company approaches
4. Track personal learning progress with metrics
5. View team-wide performance analytics

This feature integrates with the backend API endpoints and provides an engaging onboarding experience.

---

## Feature Overview

### User Roles

**New Employees/Trainees:**
- Browse available scenarios
- View scenario details and challenges
- Submit their solutions
- Receive instant AI feedback with scores
- Track personal progress
- View scenario library and categories

**Managers/HR:**
- Create new scenarios
- View team-wide analytics
- Monitor individual employee progress
- Identify high performers
- Track onboarding effectiveness

### Core User Flows

#### Flow 1: New Employee Learning
```
1. Login/Dashboard
   └─ See "Learning Scenarios" widget
   
2. Browse Scenarios
   └─ Filter by difficulty, category
   └─ View scenario cards with metadata
   
3. Select Scenario
   └─ Read challenge description
   └─ Understand context and challenges
   
4. Solve Scenario
   └─ Write/enter solution
   └─ Fill out approach details
   
5. Submit Solution
   └─ Confirm submission
   └─ Mini loader while AI processes
   
6. View Feedback
   └─ Score (0-100)
   └─ Strengths (highlighted)
   └─ Gaps identified
   └─ Detailed feedback
   └─ Company's approach comparison
   
7. Track Progress
   └─ Dashboard shows updated stats
   └─ Progress bar updated
   └─ Badge/achievement system (optional)
```

#### Flow 2: Manager Analytics
```
1. Manager Dashboard
   └─ Team training section
   
2. View Team Progress
   └─ Total submissions
   └─ Average team score
   └─ Score distribution charts
   
3. View Individual Progress
   └─ Select employee
   └─ See their submission history
   └─ View trend analysis
   └─ Identify struggling employees
   
4. Create Scenarios
   └─ Admin form with all fields
   └─ Rich text editor for descriptions
   └─ Preview before publishing
```

---

## API Integration Points

### Endpoints to Consume

```
1. GET /scenarios
   - Query params: category, difficulty_level, skip, limit
   - Response: List of scenarios with metadata
   
2. GET /scenarios/{scenario_id}
   - Response: Scenario details (without company solution)
   
3. POST /scenarios/create
   - Body: Scenario creation form data
   - Response: Created scenario with ID
   
4. POST /scenarios/{scenario_id}/submit
   - Body: employee_id, employee_name, solution_text
   - Response: Score, feedback, strengths, gaps
   
5. GET /employee/{employee_id}/progress
   - Response: Progress metrics, score distribution
   
6. GET /team/progress
   - Response: Team analytics, top performers
```

---

## UI/UX Requirements

### 1. Scenario Library Page

**Layout:**
```
┌─────────────────────────────────────────────┐
│  Scenario Library                           │
├─────────────────────────────────────────────┤
│                                             │
│  Filters & Search:                          │
│  [Category dropdown] [Difficulty dropdown]  │
│  [Search bar]            [Sort: Newest]     │
│                                             │
├─────────────────────────────────────────────┤
│                                             │
│  Scenario Cards (Grid or List):             │
│                                             │
│  ┌─────────────────────┐                   │
│  │ 📋 Production       │                   │
│  │    Outage           │                   │
│  │                     │                   │
│  │ Category: Technical │                   │
│  │ Level: Hard 🔴      │                   │
│  │ Score: 72.5/100 ⭐  │                   │
│  │ Submissions: 12     │                   │
│  │                     │                   │
│  │   [View & Solve]    │                   │
│  └─────────────────────┘                   │
│                                             │
│                 [Pagination]                │
└─────────────────────────────────────────────┘
```

**Features:**
- Scenario cards showing: Title, Category, Difficulty, Avg Score, Submission Count
- Color-coded difficulty (🟢 Easy, 🟡 Medium, 🔴 Hard)
- Filter/sort options
- Pagination (10 per page default)
- Search functionality
- "Solved" indicator for completed scenarios

### 2. Scenario Detail Page

**Layout:**
```
┌────────────────────────────────────────────────────┐
│  ◄ Back to Library                                │
│                                                    │
│  Production Outage Response                       │
│  Category: Technical  |  Difficulty: Hard  |      │
│                                                    │
├────────────────────────────────────────────────────┤
│                                                    │
│  SCENARIO DESCRIPTION                             │
│  ─────────────────────────────────────────────    │
│  A critical service went down unexpectedly...     │
│                                                    │
│  TECHNICAL CONTEXT                                │
│  ─────────────────────────────────────────────    │
│  Our main API service became unresponsive...      │
│                                                    │
│  CHALLENGES FACED                                 │
│  ─────────────────────────────────────────────    │
│  • Time pressure                                   │
│  • Data consistency concerns                       │
│  • Customer communication                          │
│                                                    │
├────────────────────────────────────────────────────┤
│                                                    │
│  [Solve This Scenario] or [View My Solution]     │
│                                                    │
│  Previous Submissions (if any):                   │
│  └─ Submitted on Apr 5 | Score: 72/100           │
│  └─ Submitted on Mar 28 | Score: 68/100          │
│                                                    │
└────────────────────────────────────────────────────┘
```

**Note:** Do NOT show company solution on this page. Only after submission.

### 3. Solution Submission Page

**Layout:**
```
┌────────────────────────────────────────────────────┐
│  Solving: Production Outage Response               │
│                                                    │
├────────────────────────────────────────────────────┤
│                                                    │
│  Your Approach/Solution:                          │
│                                                    │
│  ┌────────────────────────────────────────────┐  │
│  │ When a critical service goes down, I       │  │
│  │ would:                                      │  │
│  │                                             │  │
│  │ 1. Immediately alert the on-call team     │  │
│  │ 2. Check monitoring dashboards            │  │
│  │ 3. Review recent deployments              │  │
│  │ ...                                         │  │
│  │                                             │  │
│  │                                             │  │
│  │                                             │  │
│  └────────────────────────────────────────────┘  │
│                                                    │
│  Character count: 450 / 5000                      │
│                                                    │
│  [Cancel]                        [Submit Solution]│
│                                                    │
└────────────────────────────────────────────────────┘
```

**Features:**
- Large text area (min 100 chars, max 5000 chars)
- Character counter
- Auto-save draft (optional)
- Spell check (browser native or plugin)
- Clear guidance on what to write
- Cancel/Submit buttons

### 4. Feedback Page

**Layout:**
```
┌────────────────────────────────────────────────────┐
│  ✅ Solution Submitted Successfully!               │
│                                                    │
│  Your Score: 78/100 ⭐⭐⭐                         │
│                                                    │
├────────────────────────────────────────────────────┤
│                                                    │
│  APPROACH ALIGNMENT                               │
│  ─────────────────────────────────────────────    │
│  Your approach covers the essential steps and     │
│  prioritizes immediate communication and          │
│  investigation. However, it misses some critical  │
│  operational details that our company learned...  │
│                                                    │
├────────────────────────────────────────────────────┤
│                                                    │
│  ✓ STRENGTHS                                      │
│  • Good instinct to immediately involve           │
│    stakeholders                                    │
│  • Mentioned data restoration consideration       │
│  • Focused on documentation for prevention        │
│                                                    │
├────────────────────────────────────────────────────┤
│                                                    │
│  ⚠ GAPS IDENTIFIED                                │
│  • Missing specific mention of rollback            │
│    procedures and timelines                       │
│  • Didn't specify testing requirements before     │
│    re-deployment                                  │
│  • Lack of emphasis on preventing issues through  │
│    infrastructure improvements                    │
│                                                    │
├────────────────────────────────────────────────────┤
│                                                    │
│  DETAILED FEEDBACK                                │
│  ─────────────────────────────────────────────    │
│  Your solution demonstrates solid incident        │
│  response thinking. To improve:                   │
│                                                    │
│  (1) Always have pre-tested rollback procedures   │
│      ready - practice them regularly.             │
│  (2) Implement automated migration testing with   │
│      realistic data samples.                      │
│  (3) Use feature flags for gradual rollouts.      │
│  (4) Maintain frequent backups and practice       │
│      recovery procedures.                         │
│                                                    │
│  [View Company's Full Solution] [Try Another]     │
│                                                    │
└────────────────────────────────────────────────────┘
```

**Features:**
- Clear score display with star rating
- Color-coded sections (Strengths in green, Gaps in yellow)
- Scrollable detailed feedback
- Link to company solution (optional - can be in separate modal)
- Navigation buttons (Try another scenario, View progress)

### 5. Progress Dashboard

**Layout:**
```
┌────────────────────────────────────────────────────┐
│  My Learning Progress                              │
│                                                    │
├────────────────────────────────────────────────────┤
│                                                    │
│  Progress Overview:                               │
│                                                    │
│  Tasks Completed: 8/20                            │
│  ████████░░░░░░░░░░  40%                          │
│                                                    │
│  Average Score: 74.5/100 ⭐                       │
│                                                    │
├────────────────────────────────────────────────────┤
│                                                    │
│  Score Distribution:                              │
│                                                    │
│  Excellent (90-100):    ██ 1                       │
│  Good (75-89):          ██████ 3                   │
│  Satisfactory (60-74):  ██████ 3                   │
│  Needs Improvement:     ██ 1                       │
│  Insufficient (<40):    0                          │
│                                                    │
├────────────────────────────────────────────────────┤
│                                                    │
│  Recent Submissions:                              │
│                                                    │
│  Production Outage       Apr 7, 2026   78/100 ⭐  │
│  Security Incident       Apr 5, 2026   72/100 ⭐  │
│  Feature Request Crisis  Apr 3, 2026   68/100 ⭐  │
│                                                    │
│  [View All Submissions]                            │
│                                                    │
├────────────────────────────────────────────────────┤
│                                                    │
│  [Continue Learning]  [Share Progress]             │
│                                                    │
└────────────────────────────────────────────────────┘
```

**Features:**
- Overview card with key metrics
- Progress bar
- Score distribution visualization (bar chart or pie chart)
- Recent submissions list
- Links to continue learning

### 6. Manager Analytics Page

**Layout:**
```
┌────────────────────────────────────────────────────┐
│  Team Learning Analytics                           │
│                                                    │
├────────────────────────────────────────────────────┤
│                                                    │
│  TEAM OVERVIEW                                     │
│                                                    │
│  Total Employees: 25                              │
│  Total Submissions: 156                            │
│  Average Team Score: 71.3/100                      │
│                                                    │
├────────────────────────────────────────────────────┤
│                                                    │
│  Team Score Distribution:                         │
│                                                    │
│  [Pie Chart or Bar Chart]                         │
│  Excellent: 12  |  Good: 48  |  Satisfactory: 72  │
│  Needs Imp: 20  |  Insufficient: 4                │
│                                                    │
├────────────────────────────────────────────────────┤
│                                                    │
│  TOP PERFORMERS                                    │
│                                                    │
│  1. 🏆 Alice Johnson      88.5 avg                │
│  2. 🥈 Bob Smith          85.2 avg                │
│  3. 🥉 Carol Davis        82.1 avg                │
│                                                    │
├────────────────────────────────────────────────────┤
│                                                    │
│  Browse Employees:                                 │
│                                                    │
│  [Search] [Sort by Score ▼]                       │
│                                                    │
│  Name              | Score | Completed | Status   │
│  ─────────────────────────────────────────────   │
│  John Doe          | 74.5  | 8/20      | ✓       │
│  Jane Smith        | 71.2  | 6/20      | ◐       │
│  Mike Johnson      | 68.9  | 5/20      | ◐       │
│  Sarah Williams    | 92.1  | 12/20     | ✓       │
│                                                    │
│  [View Details]                                    │
│                                                    │
└────────────────────────────────────────────────────┘
```

**Features:**
- Team-wide metrics
- Score distribution charts
- Top performers list
- Employee browsable table
- Links to individual employee progress

---

## Component Structure

### Recommended Component Hierarchy

```
App
├── Layout
│   ├── Header (with navigation)
│   ├── Sidebar (navigation menu)
│   └── MainContent
│       ├── ScenarioLibrary
│       │   ├── FilterBar
│       │   ├── SearchBar
│       │   ├── ScenarioCardGrid
│       │   │   └── ScenarioCard
│       │   └── Pagination
│       │
│       ├── ScenarioDetail
│       │   ├── ScenarioHeader
│       │   ├── ScenarioContent
│       │   └── ActionButtons
│       │
│       ├── SolutionSubmission
│       │   ├── PromptDisplay
│       │   ├── SolutionTextArea
│       │   └── SubmitButton
│       │
│       ├── FeedbackDisplay
│       │   ├── ScoreDisplay
│       │   ├── ApproachAlignment
│       │   ├── StrengthsList
│       │   ├── GapsList
│       │   └── DetailedFeedback
│       │
│       ├── ProgressDashboard
│       │   ├── OverviewCard
│       │   ├── ProgressBar
│       │   ├── ScoreDistribution
│       │   └── RecentSubmissions
│       │
│       └── ManagerAnalytics
│           ├── TeamOverview
│           ├── ScoreCharts
│           ├── TopPerformers
│           └── EmployeeBrowse
```

### Component Responsibilities

**ScenarioLibrary Component:**
- Fetch and display scenario list
- Handle filtering & search
- Pagination logic
- Route to scenario detail

**ScenarioDetail Component:**
- Display scenario context
- Hide company solution initially
- Show submission history if exists
- Route to submission page

**SolutionSubmission Component:**
- Text area for solution
- Character counter
- Draft auto-save (optional)
- Submit handler with loading state
- Error handling

**FeedbackDisplay Component:**
- Show score with visual indicator (stars, color)
- Display structured feedback (strengths, gaps)
- Modal for full company solution (optional)
- Navigation to next scenario

**ProgressDashboard Component:**
- Calculate and display metrics
- Show progress bar
- Display charts (score distribution)
- List recent submissions

**ManagerAnalytics Component:**
- Fetch team statistics
- Display aggregated metrics
- Show top performers
- Allow employee filtering/search

---

## State Management

### Local Component State

```javascript
// ScenarioLibrary
{
  scenarios: [],
  filters: {
    category: null,
    difficulty_level: null,
    search: ''
  },
  pagination: {
    skip: 0,
    limit: 10,
    total: 0
  },
  loading: false,
  error: null
}

// SolutionSubmission
{
  solutionText: '',
  characterCount: 0,
  isSubmitting: false,
  error: null,
  submitted: false
}

// FeedbackDisplay
{
  feedback: null,
  loading: false,
  expandedSections: {
    strengths: true,
    gaps: true,
    fullFeedback: false
  }
}

// ProgressDashboard
{
  progressData: null,
  loading: false,
  error: null,
  timeRange: 'all' // or '30days', '90days'
}
```

### Global State (Redux/Vuex/Context)

```javascript
{
  auth: {
    user: { id, name, role, email },
    isAuthenticated: boolean
  },
  scenarios: {
    currentScenario: { id, title, description, ... },
    allScenarios: [],
    selectedScenarioId: null
  },
  submissions: {
    userSubmissions: [],
    currentSubmission: null,
    feedback: null
  },
  progress: {
    employeeProgress: { tasksCompleted, avgScore, ... },
    teamProgress: { totalEmployees, avgScore, ... }
  },
  ui: {
    currentPage: 'scenarios' | 'scenario-detail' | 'submit' | 'feedback' | 'progress' | 'analytics',
    loading: boolean,
    error: null
  }
}
```

---

## API Integration Details

### Request/Response Examples

**Fetch Scenarios:**
```javascript
// Request
GET /scenarios?category=Technical&difficulty_level=Hard&skip=0&limit=10

// Response
{
  "scenarios": [
    {
      "scenario_id": "uuid",
      "title": "Production Outage Response",
      "description": "How to handle outages",
      "category": "Technical",
      "difficulty_level": "Hard",
      "submission_count": 12,
      "average_score": 72.5,
      "tags": ["incident-response", "devops"]
    }
  ],
  "total_count": 25,
  "skip": 0,
  "limit": 10
}
```

**Submit Solution:**
```javascript
// Request
POST /scenarios/{scenario_id}/submit
Body: {
  "scenario_id": "uuid",
  "employee_id": "emp_123",
  "employee_name": "John Doe",
  "solution_text": "I would handle it by..."
}

// Response (takes 5-10 seconds for AI processing)
{
  "submission_id": "uuid",
  "scenario_id": "uuid",
  "employee_name": "John Doe",
  "score": 78,
  "approach_alignment": "Good approach...",
  "strengths": ["Point 1", "Point 2"],
  "gaps": ["Gap 1", "Gap 2"],
  "feedback": "Detailed feedback...",
  "submitted_at": "2026-04-07T..."
}
```

**Get Employee Progress:**
```javascript
// Request
GET /employee/{employee_id}/progress

// Response
{
  "employee_id": "emp_123",
  "total_tasks_completed": 8,
  "average_score": 74.5,
  "score_distribution": {
    "excellent": 1,
    "good": 3,
    "satisfactory": 3,
    "needs_improvement": 1,
    "insufficient": 0
  },
  "recent_submissions": [...],
  "progress_percentage": 40
}
```

---

## Key Features & Requirements

### Feature 1: Scenario Browsing
✅ Display scenarios in grid or list format  
✅ Filter by category, difficulty level  
✅ Search by title/keywords  
✅ Sort options (newest, most solved, trending)  
✅ Pagination (10-20 per page)  
✅ Show scenario metadata (category, difficulty, avg score, submission count)  
✅ Color-code difficulty levels  
✅ Show if user has already solved that scenario  

### Feature 2: Solution Submission
✅ Large text area for solution entry  
✅ Character counter (100-5000 chars)  
✅ Real-time auto-save to local storage (optional)  
✅ Submit button with validation  
✅ Loading indicator during submission  
✅ Confirmation before final submission  
✅ Error handling and retry logic  

### Feature 3: Feedback Display
✅ Clear score display (0-100 with visual indicator)  
✅ Structured feedback sections (alignment, strengths, gaps)  
✅ Expandable/collapsible sections  
✅ Company solution display (in modal or separate page)  
✅ Actionable improvement suggestions  
✅ Navigation to try another scenario  
✅ Share/export feedback (optional)  

### Feature 4: Progress Tracking
✅ Overall progress percentage  
✅ Average score display  
✅ Score distribution visualization  
✅ Recent submissions list  
✅ Trend analysis (optional)  
✅ Comparison with team average (optional)  
✅ Export progress report (optional)  

### Feature 5: Manager Analytics
✅ Team overview with key metrics  
✅ Top performers leaderboard  
✅ Score distribution charts  
✅ Employee browsing with search/sort  
✅ Individual employee details view  
✅ Identify at-risk employees (low scores)  
✅ Export team analytics (optional)  

---

## Design Specifications

### Color Scheme
```
Primary: #007AFF (Blue) - Action buttons, links
Secondary: #5AC8FA (Light Blue) - Secondary actions
Success: #34C759 (Green) - Strengths, positive indicators
Warning: #FF9500 (Orange) - Gaps, warnings
Error: #FF3B30 (Red) - Errors, insufficient scores
Neutral: #8E8E93 (Gray) - Neutral text, dividers

Difficulty Colors:
Easy: #34C759 (Green)
Medium: #FF9500 (Orange)
Hard: #FF3B30 (Red)

Score Colors:
90-100: #34C759 (Green) - Excellent
75-89: #34C759-ish (Light Green) - Good
60-74: #FF9500 (Orange) - Satisfactory
40-59: #FF9500-ish (Darker Orange) - Needs Improvement
<40: #FF3B30 (Red) - Insufficient
```

### Typography
```
Headings: Bold, sans-serif (16-24px)
Body: Regular, sans-serif (14-16px)
Metadata: Light gray, smaller (12-13px)
Code: Monospace (if showing code examples)
```

### Spacing
```
Card padding: 16px or 20px
Section spacing: 24px
Small spacing: 8px, 12px
Large spacing: 32px
```

### Responsive Design
```
Mobile (< 640px):
- Single column layout
- Full-width cards
- Stacked filters
- Simplified charts

Tablet (640px - 1024px):
- Two-column layout where possible
- Side-by-side sections
- Collapsible sidebar

Desktop (> 1024px):
- Full multi-column layout
- Expanded visualizations
- Persistent sidebar
```

---

## Error Handling & Edge Cases

### Error Scenarios

**API Error (500):**
```javascript
{
  title: "Oops! Something went wrong",
  message: "We encountered an error. Please try again.",
  action: "Retry"
}
```

**Validation Error (400):**
```javascript
{
  title: "Invalid Input",
  message: "Your solution must be between 100-5000 characters.",
  action: "Edit"
}
```

**Network Error:**
```javascript
{
  title: "Connection Lost",
  message: "Check your internet connection and try again.",
  action: "Retry"
}
```

**Timeout (Only for AI Comparison):**
```javascript
{
  title: "Feedback Taking Longer",
  message: "AI is processing your solution. This may take up to 30 seconds.",
  showProgress: true,
  timeoutMessage: "If this continues, please refresh and try again."
}
```

### Edge Cases to Handle

1. **Empty scenarios list** - Show empty state with message
2. **User submits empty solution** - Validation error
3. **User tries to submit twice** - Disable button during submission
4. **Solution submission times out** - Show retry option
5. **No progress data** - Show "Get started" message
6. **Slow network** - Show loading skeletons
7. **User has no employee_id** - Graceful error handling
8. **Firestore offline** - Show offline message

---

## Loading States & Skeletons

### Skeleton Loading
```
Scenario Card Skeleton:
┌─────────────────────┐
│ ▓▓▓▓▓▓▓ (title)     │
│ ▓▓▓▓ (category)     │
│                     │
│ ▓▓▓▓▓▓ (metadata)   │
└─────────────────────┘
```

### Loading Indicators
- Spinner/loader during API calls
- Pulse animation for skeletons
- Progress bar for solution submission delay
- Toast notifications for success messages

---

## Accessibility Requirements

✅ Semantic HTML (headings, lists, buttons)  
✅ ARIA labels for buttons and interactive elements  
✅ Keyboard navigation support (Tab, Enter, Escape)  
✅ Color not as sole indicator (use icons/text too)  
✅ Sufficient contrast ratios (WCAG AA+)  
✅ Form labels properly associated  
✅ Error messages linked to form fields  
✅ Focus indicators visible  
✅ Skip to main content link  

---

## Performance Considerations

✅ Lazy load scenarios (infinite scroll or pagination)  
✅ Debounce search input (300ms)  
✅ Memoize expensive computations  
✅ Optimize re-renders (React.memo, useMemo, useCallback)  
✅ Code splitting for different views  
✅ Compress images/assets  
✅ Cache API responses (localStorage for list, shorter TTL for progress)  
✅ Minimize bundle size  

---

## Testing Requirements

### Unit Tests
- Filter logic
- Score calculation/distribution
- Progress percentage calculation
- Form validation
- Character counter

### Integration Tests
- Fetch scenarios and display
- Submit solution and get feedback
- Calculate and display progress
- Filter and search scenarios
- Navigate between pages

### E2E Tests
- Complete user flow (browse → solve → feedback → progress)
- Manager analytics flow
- Error scenarios and recovery
- Responsive design on different devices

---

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions (macOS & iOS)
- Mobile browsers: Latest versions

---

## Implementation Timeline Recommendation

**Phase 1 (Week 1):**
- Set up project structure & components
- Implement ScenarioLibrary & ScenarioDetail pages
- Basic filtering & pagination

**Phase 2 (Week 2):**
- Implement SolutionSubmission flow
- Connect to API endpoints
- Error handling & validation

**Phase 3 (Week 3):**
- Implement FeedbackDisplay component
- Build ProgressDashboard
- State management

**Phase 4 (Week 4):**
- Manager Analytics page
- Testing & refinement
- Performance optimization
- Accessibility audit

---

## Success Metrics

- [ ] All 6 main features implemented
- [ ] 100% test coverage on critical paths
- [ ] PageSpeed Insights score > 85
- [ ] Zero accessibility errors
- [ ] Support all target browsers
- [ ] Mobile responsive (passes responsive test)
- [ ] User satisfaction survey > 4.2/5
- [ ] Scenario completion rate > 70% for new hires

---

## Dependencies & Libraries (Suggestions)

**Frontend Framework:**
- React 18+ with Hooks
- Vue 3.x with Composition API
- Angular 15+

**State Management:**
- Redux / Redux Toolkit
- Zustand or Pinia
- Recoil

**UI Components:**
- Material-UI (MUI)
- Tailwind CSS + custom components
- Chakra UI
- Shadcn/ui with Tailwind

**Charts & Visualization:**
- Recharts
- Chart.js
- ApexCharts

**Forms & Validation:**
- React Hook Form
- Yup or Zod for validation

**API Client:**
- Axios
- React Query / TanStack Query
- SWR

**Date/Time:**
- date-fns
- Day.js

**Utilities:**
- Lodash or just native JS
- classnames (for conditional CSS)

---

## API Documentation Reference

For complete API details, see:
- [SCENARIO_FEATURE.md](./SCENARIO_FEATURE.md) - Complete feature docs
- [API_ENDPOINTS_REFERENCE.md](./API_ENDPOINTS_REFERENCE.md) - Quick API reference
- Backend repo: [services/scenario_service.py](./services/scenario_service.py)

---

## Questions to Answer Before Starting

1. **Which framework?** React, Vue, Angular?
2. **State management?** Redux, Context, Zustand?
3. **UI library?** Material-UI, Tailwind, Chakra?
4. **Mobile first?** Yes - design for mobile first
5. **Authentication?** How will employee_id be sent?
6. **Hosting?** This affects build optimization
7. **Analytics?** Track user interactions?
8. **Notifications?** In-app only or push?

---

## Contact & Support

**Backend API Documentation:**
See SCENARIO_FEATURE.md and API_ENDPOINTS_REFERENCE.md

**Architecture Questions:**
See SCENARIO_ARCHITECTURE.md

**Example Scenarios:**
See SCENARIO_EXAMPLES.md

---

## Appendix: Mockup ASCII Diagrams

All major page layouts have been provided in the "UI/UX Requirements" section above with ASCII mockups.

---

**Prompt Version:** 1.0  
**Date:** April 7, 2026  
**Status:** Ready for Frontend Development
