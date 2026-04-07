"""
Scenario Management Service for employee learning.
Handles scenario upload, storage, retrieval, and comparison with Firestore + RAG + Gemini.
"""

from google.cloud import firestore
from google.cloud import storage
from vertexai.generative_models import GenerativeModel
import vertexai
import os
import logging
from typing import Dict, Optional, List
from datetime import datetime
import uuid
import json

logger = logging.getLogger(__name__)

# Initialize Vertex AI and Firestore
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("VERTEX_AI_LOCATION", os.getenv("GCP_LOCATION", "us-central1"))
GCS_BUCKET = os.getenv("GCS_BUCKET_NAME", f"{PROJECT_ID}-office-assist")

# Ensure we use a regional location for Vertex AI (not global)
if LOCATION == "global":
    LOCATION = "us-central1"

if PROJECT_ID:
    vertexai.init(project=PROJECT_ID, location=LOCATION)

# Initialize Firestore and Storage clients
db = firestore.Client(project=PROJECT_ID) if PROJECT_ID else None
storage_client = storage.Client(project=PROJECT_ID) if PROJECT_ID else None


# ==================== SCENARIO CREATION ====================

async def create_scenario(
    title: str,
    description: str,
    technical_context: str,
    company_solution: str,
    challenges_faced: str,
    lessons_learned: str,
    difficulty_level: str = "Medium",  # Easy, Medium, Hard
    category: str = "General",  # Technical, HR, Project Management, etc.
    tags: Optional[List[str]] = None,
) -> Dict:
    """
    Create and store a new scenario for employee learning.
    
    Args:
        title: Scenario title
        description: Brief description
        technical_context: Technical details and background
        company_solution: How the company solved it
        challenges_faced: Challenges encountered
        lessons_learned: Key lessons from the experience
        difficulty_level: Difficulty level (Easy/Medium/Hard)
        category: Category of scenario
        tags: Optional tags for filtering
        
    Returns:
        Dictionary with scenario ID and metadata
    """
    try:
        if not db:
            raise ValueError("Firestore not initialized. Check GCP_PROJECT_ID")
        
        scenario_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        scenario_data = {
            "scenario_id": scenario_id,
            "title": title,
            "description": description,
            "technical_context": technical_context,
            "company_solution": company_solution,
            "challenges_faced": challenges_faced,
            "lessons_learned": lessons_learned,
            "difficulty_level": difficulty_level,
            "category": category,
            "tags": tags or [],
            "created_at": timestamp,
            "updated_at": timestamp,
            "submission_count": 0,
            "average_score": 0.0,
        }
        
        # Store in Firestore
        db.collection("scenarios").document(scenario_id).set(scenario_data)
        
        logger.info(f"Created scenario: {scenario_id} - {title}")
        
        return {
            "scenario_id": scenario_id,
            "title": title,
            "status": "created",
            "created_at": timestamp.isoformat(),
        }
    
    except Exception as e:
        logger.error(f"Error creating scenario: {str(e)}")
        raise


# ==================== RETRIEVE SCENARIOS ====================

async def get_all_scenarios(
    category: Optional[str] = None,
    difficulty_level: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
) -> Dict:
    """
    Retrieve all scenarios with optional filtering.
    
    Args:
        category: Optional category filter
        difficulty_level: Optional difficulty filter
        skip: Number of results to skip (pagination)
        limit: Maximum number of results
        
    Returns:
        Dictionary with scenarios list and total count
    """
    try:
        if not db:
            raise ValueError("Firestore not initialized")
        
        query = db.collection("scenarios")
        
        if category:
            query = query.where("category", "==", category)
        
        if difficulty_level:
            query = query.where("difficulty_level", "==", difficulty_level)
        
        # Order by creation date (newest first)
        query = query.order_by("created_at", direction=firestore.Query.DESCENDING)
        
        # Get total count
        total_count = sum(1 for _ in query.stream())
        
        # Apply pagination
        docs = query.offset(skip).limit(limit).stream()
        
        scenarios = []
        for doc in docs:
            scenario_data = doc.to_dict()
            scenarios.append(
                {
                    "scenario_id": scenario_data.get("scenario_id"),
                    "title": scenario_data.get("title"),
                    "description": scenario_data.get("description"),
                    "category": scenario_data.get("category"),
                    "difficulty_level": scenario_data.get("difficulty_level"),
                    "submission_count": scenario_data.get("submission_count", 0),
                    "average_score": scenario_data.get("average_score", 0.0),
                    "tags": scenario_data.get("tags", []),
                }
            )
        
        return {
            "scenarios": scenarios,
            "total_count": total_count,
            "skip": skip,
            "limit": limit,
        }
    
    except Exception as e:
        logger.error(f"Error retrieving scenarios: {str(e)}")
        raise


async def get_scenario_detail(scenario_id: str) -> Dict:
    """
    Get complete scenario details including company solution.
    
    Args:
        scenario_id: ID of the scenario
        
    Returns:
        Dictionary with complete scenario information
    """
    try:
        if not db:
            raise ValueError("Firestore not initialized")
        
        doc = db.collection("scenarios").document(scenario_id).get()
        
        if not doc.exists:
            raise ValueError(f"Scenario {scenario_id} not found")
        
        scenario_data = doc.to_dict()
        
        return {
            "scenario_id": scenario_id,
            "title": scenario_data.get("title"),
            "description": scenario_data.get("description"),
            "technical_context": scenario_data.get("technical_context"),
            "challenges_faced": scenario_data.get("challenges_faced"),
            "difficulty_level": scenario_data.get("difficulty_level"),
            "category": scenario_data.get("category"),
            "tags": scenario_data.get("tags", []),
            # NOTE: Don't include company solution yet - employees solve first
        }
    
    except Exception as e:
        logger.error(f"Error retrieving scenario detail: {str(e)}")
        raise


# ==================== SUBMISSION & COMPARISON ====================

async def submit_scenario_solution(
    scenario_id: str,
    employee_id: str,
    employee_name: str,
    solution_text: str,
) -> Dict:
    """
    Submit employee solution and get comparison with company solution.
    
    Args:
        scenario_id: ID of the scenario
        employee_id: Unique employee identifier
        employee_name: Name of employee
        solution_text: Employee's proposed solution
        
    Returns:
        Dictionary with comparison results and score
    """
    try:
        if not db:
            raise ValueError("Firestore not initialized")
        
        # Get scenario details
        scenario_doc = db.collection("scenarios").document(scenario_id).get()
        if not scenario_doc.exists:
            raise ValueError(f"Scenario {scenario_id} not found")
        
        scenario_data = scenario_doc.to_dict()
        
        # Generate comparison using Gemini
        comparison_result = await _compare_solutions(
            scenario_id=scenario_id,
            scenario_data=scenario_data,
            employee_solution=solution_text,
            employee_name=employee_name,
        )
        
        # Create submission record
        submission_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        submission_data = {
            "submission_id": submission_id,
            "scenario_id": scenario_id,
            "employee_id": employee_id,
            "employee_name": employee_name,
            "employee_solution": solution_text,
            "comparison_score": comparison_result.get("score", 0),
            "approach_alignment": comparison_result.get("approach_alignment", ""),
            "strengths": comparison_result.get("strengths", []),
            "gaps": comparison_result.get("gaps", []),
            "feedback": comparison_result.get("feedback", ""),
            "submitted_at": timestamp,
            "updated_at": timestamp,
        }
        
        # Store submission in Firestore
        db.collection("submissions").document(submission_id).set(submission_data)
        
        # Update scenario submission count and average score
        _update_scenario_stats(scenario_id, comparison_result.get("score", 0))
        
        logger.info(
            f"Submitted scenario solution: {submission_id} "
            f"(Employee: {employee_name}, Score: {comparison_result.get('score')})"
        )
        
        return {
            "submission_id": submission_id,
            "scenario_id": scenario_id,
            "employee_name": employee_name,
            "score": comparison_result.get("score"),
            "approach_alignment": comparison_result.get("approach_alignment"),
            "strengths": comparison_result.get("strengths", []),
            "gaps": comparison_result.get("gaps", []),
            "feedback": comparison_result.get("feedback"),
            "submitted_at": timestamp.isoformat(),
        }
    
    except Exception as e:
        logger.error(f"Error submitting scenario solution: {str(e)}")
        raise


async def _compare_solutions(
    scenario_id: str,
    scenario_data: Dict,
    employee_solution: str,
    employee_name: str,
) -> Dict:
    """
    Compare employee solution with company solution using Gemini.
    
    Args:
        scenario_id: Scenario ID
        scenario_data: Scenario details
        employee_solution: Employee's proposed solution
        employee_name: Employee name
        
    Returns:
        Dictionary with comparison analysis
    """
    try:
        model = GenerativeModel("gemini-2.5-pro")
        
        comparison_prompt = f"""
        You are an expert technical evaluator comparing an employee's solution 
        with a company's proven solution to a complex scenario.
        
        SCENARIO DETAILS:
        Title: {scenario_data.get('title')}
        Category: {scenario_data.get('category')}
        Technical Context: {scenario_data.get('technical_context')}
        Challenges Faced: {scenario_data.get('challenges_faced')}
        
        COMPANY'S SOLUTION:
        {scenario_data.get('company_solution')}
        
        LESSONS LEARNED BY COMPANY:
        {scenario_data.get('lessons_learned')}
        
        EMPLOYEE'S SOLUTION (by {employee_name}):
        {employee_solution}
        
        Please provide a detailed comparison analysis in the following JSON format:
        {{
            "score": <0-100 score based on alignment with company solution>,
            "approach_alignment": "<description of how well the approach aligns>",
            "strengths": [
                "<strength 1>",
                "<strength 2>",
                ...
            ],
            "gaps": [
                "<gap 1: what was missed>",
                "<gap 2: what was missed>",
                ...
            ],
            "feedback": "<detailed constructive feedback for improvement>"
        }}
        
        Scoring guidelines (0-100):
        - 90-100: Excellent - Matches or exceeds company solution
        - 75-89: Good - Covers main points with minor gaps
        - 60-74: Satisfactory - Addresses core issues but lacks depth
        - 40-59: Needs Improvement - Missing important aspects
        - Below 40: Insufficient - Fundamentally misses key points
        """
        
        response = model.generate_content(comparison_prompt)
        result_text = response.text
        
        # Parse JSON from response
        try:
            # Extract JSON from markdown code blocks if present
            if "```json" in result_text:
                json_str = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                json_str = result_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = result_text
            
            comparison_result = json.loads(json_str)
        except (json.JSONDecodeError, IndexError):
            logger.warning(f"Could not parse JSON from Gemini response. Raw: {result_text}")
            # Fallback to structured response
            comparison_result = {
                "score": 50,
                "approach_alignment": "Unable to parse detailed response",
                "strengths": [],
                "gaps": ["Full analysis unavailable"],
                "feedback": result_text[:500],
            }
        
        return comparison_result
    
    except Exception as e:
        logger.error(f"Error comparing solutions: {str(e)}")
        raise


def _update_scenario_stats(scenario_id: str, new_score: float) -> None:
    """
    Update scenario statistics after a new submission.
    
    Args:
        scenario_id: ID of scenario
        new_score: Score from new submission
    """
    try:
        if not db:
            return
        
        scenario_doc = db.collection("scenarios").document(scenario_id).get()
        if scenario_doc.exists:
            scenario_data = scenario_doc.to_dict()
            submission_count = scenario_data.get("submission_count", 0)
            old_average = scenario_data.get("average_score", 0.0)
            
            # Calculate new average
            new_average = (
                (old_average * submission_count + new_score) / (submission_count + 1)
            )
            
            db.collection("scenarios").document(scenario_id).update(
                {
                    "submission_count": submission_count + 1,
                    "average_score": new_average,
                    "updated_at": datetime.utcnow(),
                }
            )
    
    except Exception as e:
        logger.error(f"Error updating scenario stats: {str(e)}")


# ==================== TASK PROGRESS TRACKING ====================

async def get_employee_progress(employee_id: str) -> Dict:
    """
    Get task completion progress for an employee.
    
    Args:
        employee_id: Employee's unique identifier
        
    Returns:
        Dictionary with progress statistics
    """
    try:
        if not db:
            raise ValueError("Firestore not initialized")
        
        # Get scenario submissions for this employee
        submissions = (
            db.collection("submissions")
            .where("employee_id", "==", employee_id)
            .stream()
        )

        submission_list = [doc.to_dict() for doc in submissions]
        total_scenarios_submitted = len(submission_list)

        # Get standard task submissions for this employee
        task_docs = (
            db.collection("task_submissions")
            .where("employee_id", "==", employee_id)
            .stream()
        )
        task_list = [doc.to_dict() for doc in task_docs]
        total_standard_tasks_completed = len(task_list)
        total_tasks_completed = total_scenarios_submitted + total_standard_tasks_completed
        
        # Calculate statistics
        scores = [s.get("comparison_score", 0) for s in submission_list]
        average_score = sum(scores) / len(scores) if scores else 0
        
        # Get score distribution
        excellent = sum(1 for s in scores if s >= 90)
        good = sum(1 for s in scores if 75 <= s < 90)
        satisfactory = sum(1 for s in scores if 60 <= s < 75)
        needs_improvement = sum(1 for s in scores if 40 <= s < 60)
        insufficient = sum(1 for s in scores if s < 40)
        
        # Get recent submissions
        recent_submissions = sorted(
            submission_list,
            key=lambda x: x.get("submitted_at", datetime.utcnow()),
            reverse=True,
        )[:5]
        
        recent_task_submissions = sorted(
            task_list,
            key=lambda x: x.get("timestamp", ""),
            reverse=True,
        )[:5]

        return {
            "employee_id": employee_id,
            "total_tasks_completed": total_tasks_completed,
            "scenario_tasks_completed": total_scenarios_submitted,
            "standard_tasks_completed": total_standard_tasks_completed,
            "average_score": round(average_score, 2),
            "score_distribution": {
                "excellent": excellent,  # 90-100
                "good": good,  # 75-89
                "satisfactory": satisfactory,  # 60-74
                "needs_improvement": needs_improvement,  # 40-59
                "insufficient": insufficient,  # <40
            },
            "recent_submissions": [
                {
                    "submission_id": s.get("submission_id"),
                    "scenario_id": s.get("scenario_id"),
                    "score": s.get("comparison_score"),
                    "submitted_at": s.get("submitted_at").isoformat()
                    if s.get("submitted_at")
                    else None,
                }
                for s in recent_submissions
            ],
            "recent_task_submissions": [
                {
                    "task_id": t.get("task_id"),
                    "score": t.get("score"),
                    "submitted_at": t.get("timestamp"),
                }
                for t in recent_task_submissions
            ],
            "progress_percentage": min(
                (total_tasks_completed / 20) * 100, 100
            ),  # Assuming 20 scenarios for 100%
        }
    
    except Exception as e:
        logger.error(f"Error getting employee progress: {str(e)}")
        raise


async def get_team_progress() -> Dict:
    """
    Get team-wide progress statistics.
    
    Returns:
        Dictionary with team statistics
    """
    try:
        if not db:
            raise ValueError("Firestore not initialized")
        
        # Get all submissions
        all_submissions = db.collection("submissions").stream()
        
        submission_list = [doc.to_dict() for doc in all_submissions]
        
        if not submission_list:
            return {
                "total_employees": 0,
                "total_submissions": 0,
                "average_team_score": 0,
                "team_score_distribution": {},
                "top_performers": [],
            }
        
        # Get all unique employees
        unique_employees = set()
        for submission in submission_list:
            unique_employees.add(submission.get("employee_id"))
        
        # Calculate statistics
        scores = [s.get("comparison_score", 0) for s in submission_list]
        average_score = sum(scores) / len(scores) if scores else 0
        
        # Get top performers
        employee_avg_scores = {}
        for submission in submission_list:
            emp_id = submission.get("employee_id")
            emp_name = submission.get("employee_name")
            score = submission.get("comparison_score", 0)
            
            if emp_id not in employee_avg_scores:
                employee_avg_scores[emp_id] = {
                    "name": emp_name,
                    "scores": [],
                }
            employee_avg_scores[emp_id]["scores"].append(score)
        
        # Calculate average per employee and sort
        top_employees = []
        for emp_id, data in employee_avg_scores.items():
            avg = sum(data["scores"]) / len(data["scores"])
            top_employees.append(
                {"employee_id": emp_id, "name": data["name"], "avg_score": round(avg, 2)}
            )
        
        top_employees.sort(key=lambda x: x["avg_score"], reverse=True)
        top_performers = top_employees[:5]  # Top 5
        
        return {
            "total_employees": len(unique_employees),
            "total_submissions": len(submission_list),
            "average_team_score": round(average_score, 2),
            "team_score_distribution": {
                "excellent": sum(1 for s in scores if s >= 90),
                "good": sum(1 for s in scores if 75 <= s < 90),
                "satisfactory": sum(1 for s in scores if 60 <= s < 75),
                "needs_improvement": sum(1 for s in scores if 40 <= s < 60),
                "insufficient": sum(1 for s in scores if s < 40),
            },
            "top_performers": top_performers,
        }
    
    except Exception as e:
        logger.error(f"Error getting team progress: {str(e)}")
        raise
