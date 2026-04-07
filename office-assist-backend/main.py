"""
FastAPI application with Vertex AI integration for resume classification,
RAG-based chat, and task grading.
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from services.resume_classifier import classify_resume
from services.chat_service import query_rag
from services.task_grader import grade_task
from services.scenario_service import (
    create_scenario,
    get_all_scenarios,
    get_scenario_detail,
    submit_scenario_solution,
    get_employee_progress,
    get_team_progress,
)
from services.pdf_scenario_service import (
    submit_pdf_scenario_solution,
    get_pdf_scenario,
    list_available_pdf_sources,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Office Assist API",
    description="Backend API for resume classification, policy chat, and task grading",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class ChatRequest(BaseModel):
    user_input: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: Optional[list] = None
    conversation_id: Optional[str] = None


class ClassificationResponse(BaseModel):
    level: str
    confidence: Optional[float] = None
    reasoning: Optional[str] = None


class TaskSubmissionResponse(BaseModel):
    task_id: str
    score: float
    feedback: str
    timestamp: str


class MaterialUploadResponse(BaseModel):
    filename: str
    gcs_uri: Optional[str] = None
    status: str
    message: str


# ==================== SCENARIO MODELS ====================

class CreateScenarioRequest(BaseModel):
    title: str
    description: str
    technical_context: str
    company_solution: str
    challenges_faced: str
    lessons_learned: str
    difficulty_level: Optional[str] = "Medium"
    category: Optional[str] = "General"
    tags: Optional[list] = None


class ScenarioResponse(BaseModel):
    scenario_id: str
    title: str
    description: str
    technical_context: str
    category: str
    difficulty_level: str
    tags: Optional[list] = None


class SubmitScenarioSolutionRequest(BaseModel):
    scenario_id: str
    employee_id: str
    employee_name: str
    solution_text: str


class ScenarioComparisonResponse(BaseModel):
    submission_id: str
    scenario_id: str
    employee_name: str
    score: float
    approach_alignment: str
    strengths: list
    gaps: list
    feedback: str
    submitted_at: str


class EmployeeProgressResponse(BaseModel):
    employee_id: str
    total_tasks_completed: int
    average_score: float
    score_distribution: dict
    progress_percentage: float


class TeamProgressResponse(BaseModel):
    total_employees: int
    total_submissions: int
    average_team_score: float
    team_score_distribution: dict
    top_performers: list


# ==================== PDF SCENARIO MODELS ====================

class SubmitPDFScenarioSolutionRequest(BaseModel):
    pdf_source: str  # e.g., "gs://bucket/Product Document.pdf"
    employee_id: str
    employee_name: str
    employee_solution: str
    scenario_index: Optional[int] = None


class PDFScenarioResponse(BaseModel):
    title: str
    problem: str
    category: str
    difficulty: str
    key_points: list


class PDFScenarioComparisonResponse(BaseModel):
    submission_id: str
    scenario_title: str
    scenario_category: str
    scenario_difficulty: str
    score: float
    alignment_summary: str
    strengths: list
    gaps: list
    references_to_doc: list
    improvement_suggestions: str
    feedback: str
    pdf_solution: str
    submitted_at: str


class PDFSourceResponse(BaseModel):
    pdf_source: str
    total_scenarios: int
    created_at: str
    scenarios_sample: list


# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Office Assist API"}


@app.post("/classify", response_model=ClassificationResponse)
async def classify_resume_endpoint(
    file: UploadFile = File(...)
):
    """
    Classify a resume PDF using Vertex AI to determine experience level.
    
    Args:
        file: PDF file of the resume
        
    Returns:
        Classification result (Junior, Mid, or Senior) with confidence and reasoning
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )
        
        # Read file content
        content = await file.read()
        
        if len(content) == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )
        
        logger.info(f"Processing resume classification for file: {file.filename}")
        
        # Call classification service
        result = await classify_resume(content, file.filename)
        
        return ClassificationResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in resume classification: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to classify resume: {str(e)}"
        )


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint that queries Vertex AI Search data store for company policy answers.
    
    Args:
        request: ChatRequest with user input and optional conversation ID
        
    Returns:
        Answer from RAG system with sources
    """
    try:
        if not request.user_input or len(request.user_input.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="user_input cannot be empty"
            )
        
        logger.info(f"Processing chat request: {request.user_input[:50]}...")
        
        # Call RAG service
        result = await query_rag(
            user_input=request.user_input,
            conversation_id=request.conversation_id
        )
        
        return ChatResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat request: {str(e)}"
        )


@app.post("/submit-task", response_model=TaskSubmissionResponse)
async def submit_task_endpoint(
    task_text: Optional[str] = Form(None),
    employee_id: Optional[str] = Form(None),
    employee_name: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Submit a task for grading using Gemini 1.5 Pro.
    
    Args:
        task_text: Text submission (optional if file provided)
        file: File submission (optional if task_text provided)
        
    Returns:
        Grading result with score and feedback, saved to Firestore
    """
    try:
        # Validate that at least one input is provided
        if not task_text and not file:
            raise HTTPException(
                status_code=400,
                detail="Either task_text or file must be provided"
            )
        
        submission_content = task_text or ""
        file_name = None
        
        # If file is provided, read its content
        if file:
            file_content = await file.read()
            file_name = file.filename
            
            if len(file_content) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="Uploaded file is empty"
                )
            
            # Convert file content to text (basic implementation)
            try:
                submission_content += "\n" + file_content.decode('utf-8')
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="File must contain valid text content"
                )
        
        if len(submission_content.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Submission content cannot be empty"
            )
        
        logger.info(f"Processing task submission (file: {file_name})")
        
        # Call grading service
        result = await grade_task(
            submission_content=submission_content,
            file_name=file_name,
            employee_id=employee_id,
            employee_name=employee_name,
        )
        
        return TaskSubmissionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in task submission: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process task submission: {str(e)}"
        )


@app.post("/upload-material", response_model=MaterialUploadResponse)
async def upload_material_endpoint(
    file: UploadFile = File(...)
):
    """
    Upload a training material PDF to Google Cloud Storage and trigger import to Vertex AI Search.
    
    Args:
        file: PDF file to upload
        
    Returns:
        Upload status and GCS URI
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )
        
        # Validate file size (10 MB limit)
        content = await file.read()
        file_size_mb = len(content) / (1024 * 1024)
        
        if file_size_mb > 10:
            raise HTTPException(
                status_code=400,
                detail=f"File size ({file_size_mb:.2f} MB) exceeds 10 MB limit"
            )
        
        if len(content) == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )
        
        logger.info(f"Uploading material: {file.filename} ({file_size_mb:.2f} MB)")
        
        # Import the upload service
        from services.material_uploader import upload_to_gcs
        
        # Upload to GCS
        result = await upload_to_gcs(content, file.filename)
        
        logger.info(f"Material uploaded successfully: {result.get('gcs_uri')}")
        
        return MaterialUploadResponse(
            filename=file.filename,
            gcs_uri=result.get('gcs_uri'),
            status="uploaded",
            message="Material uploaded successfully. It will be indexed within 10-30 minutes."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading material: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload material: {str(e)}"
        )


# ==================== SCENARIO MANAGEMENT ENDPOINTS ====================

@app.post("/scenarios/create")
async def create_scenario_endpoint(request: CreateScenarioRequest):
    """
    Create a new scenario for employee learning.
    
    Args:
        request: CreateScenarioRequest with scenario details
        
    Returns:
        Created scenario with ID
    """
    try:
        if not request.title or len(request.title.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Scenario title cannot be empty"
            )
        
        if not request.description or len(request.description.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Scenario description cannot be empty"
            )
        
        logger.info(f"Creating scenario: {request.title}")
        
        result = await create_scenario(
            title=request.title,
            description=request.description,
            technical_context=request.technical_context,
            company_solution=request.company_solution,
            challenges_faced=request.challenges_faced,
            lessons_learned=request.lessons_learned,
            difficulty_level=request.difficulty_level or "Medium",
            category=request.category or "General",
            tags=request.tags or [],
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating scenario: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create scenario: {str(e)}"
        )


@app.get("/scenarios")
async def get_scenarios_endpoint(
    category: Optional[str] = None,
    difficulty_level: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
):
    """
    Get all available scenarios with optional filtering.
    
    Args:
        category: Optional category filter
        difficulty_level: Optional difficulty level filter
        skip: Number of results to skip (pagination)
        limit: Maximum number of results
        
    Returns:
        List of scenarios with metadata
    """
    try:
        if skip < 0 or limit < 1:
            raise HTTPException(
                status_code=400,
                detail="Invalid pagination parameters"
            )
        
        logger.info(f"Fetching scenarios (skip={skip}, limit={limit})")
        
        result = await get_all_scenarios(
            category=category,
            difficulty_level=difficulty_level,
            skip=skip,
            limit=limit,
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching scenarios: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch scenarios: {str(e)}"
        )


@app.get("/scenarios/{scenario_id}")
async def get_scenario_endpoint(scenario_id: str):
    """
    Get complete details of a specific scenario.
    
    Args:
        scenario_id: ID of the scenario
        
    Returns:
        Scenario details and context
    """
    try:
        if not scenario_id or len(scenario_id.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Scenario ID cannot be empty"
            )
        
        logger.info(f"Fetching scenario: {scenario_id}")
        
        result = await get_scenario_detail(scenario_id)
        
        return result
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Scenario not found: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error fetching scenario details: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch scenario: {str(e)}"
        )


@app.post("/scenarios/{scenario_id}/submit")
async def submit_scenario_solution_endpoint(
    scenario_id: str,
    request: SubmitScenarioSolutionRequest,
):
    """
    Submit employee solution for a scenario and get comparison with company solution.
    
    Args:
        scenario_id: ID of the scenario
        request: SubmitScenarioSolutionRequest with employee details and solution
        
    Returns:
        Comparison results with score and feedback
    """
    try:
        if not scenario_id or len(scenario_id.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Scenario ID cannot be empty"
            )
        
        if not request.employee_id or len(request.employee_id.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Employee ID cannot be empty"
            )
        
        if not request.employee_name or len(request.employee_name.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Employee name cannot be empty"
            )
        
        if not request.solution_text or len(request.solution_text.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Solution cannot be empty"
            )
        
        logger.info(
            f"Submitting scenario solution: {request.employee_name} "
            f"for scenario {scenario_id}"
        )
        
        result = await submit_scenario_solution(
            scenario_id=scenario_id,
            employee_id=request.employee_id,
            employee_name=request.employee_name,
            solution_text=request.solution_text,
        )
        
        return result
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Invalid scenario: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error submitting scenario solution: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit solution: {str(e)}"
        )


@app.get("/employee/{employee_id}/progress")
async def get_employee_progress_endpoint(employee_id: str):
    """
    Get task completion progress for an employee.
    
    Args:
        employee_id: Employee's unique identifier
        
    Returns:
        Employee's progress statistics and completed tasks
    """
    try:
        if not employee_id or len(employee_id.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Employee ID cannot be empty"
            )
        
        logger.info(f"Fetching progress for employee: {employee_id}")
        
        result = await get_employee_progress(employee_id)
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching employee progress: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch employee progress: {str(e)}"
        )


@app.get("/team/progress")
async def get_team_progress_endpoint():
    """
    Get team-wide progress and performance statistics.
    
    Returns:
        Team progress with aggregated statistics and top performers
    """
    try:
        logger.info("Fetching team-wide progress")
        
        result = await get_team_progress()
        
        return result
    
    except Exception as e:
        logger.error(f"Error fetching team progress: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch team progress: {str(e)}"
        )


# ==================== PDF-BASED SCENARIO ENDPOINTS ====================

@app.get("/pdf-sources")
async def list_pdf_sources_endpoint():
    """
    List all available PDF sources that contain scenarios.
    
    Examples: Product Document.pdf, Welcome Aboard.pdf
    
    Returns:
        List of available PDF sources with scenario metadata
    """
    try:
        logger.info("Fetching available PDF sources")
        
        result = await list_available_pdf_sources()
        
        return {
            "pdf_sources": result,
            "total_sources": len(result),
        }
    
    except Exception as e:
        logger.error(f"Error listing PDF sources: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list PDF sources: {str(e)}"
        )


@app.get("/pdf-scenarios/{pdf_source}")
async def get_pdf_scenario_endpoint(
    pdf_source: str,
    scenario_index: Optional[int] = None,
):
    """
    Get a scenario from a PDF file.
    
    Args:
        pdf_source: PDF file path (e.g., "gs://bucket/Product Document.pdf" or "Welcome Aboard.pdf")
        scenario_index: Optional specific scenario index, else returns random scenario
        
    Returns:
        Scenario details (problem, category, difficulty, key points)
        Note: Solution is NOT returned until employee submits their solution
    """
    try:
        if not pdf_source or len(pdf_source.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="PDF source cannot be empty"
            )
        
        logger.info(f"Fetching PDF scenario from: {pdf_source}")
        
        result = await get_pdf_scenario(pdf_source, scenario_index)
        
        return result
    
    except ValueError as e:
        logger.warning(f"PDF scenario not found: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error fetching PDF scenario: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch PDF scenario: {str(e)}"
        )


@app.post("/pdf-scenarios/submit")
async def submit_pdf_scenario_solution_endpoint(
    request: SubmitPDFScenarioSolutionRequest,
):
    """
    Submit employee solution for a PDF-based scenario and get comparison.
    
    This endpoint:
    1. Gets the scenario from PDF (or retrieves cached version)
    2. Compares employee solution with solution in PDF
    3. Returns score and feedback based on PDF content
    
    Args:
        request: PDF source, employee details, and solution
        
    Returns:
        Comparison results with score, strengths, gaps, and feedback
    """
    try:
        if not request.pdf_source or len(request.pdf_source.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="PDF source cannot be empty"
            )
        
        if not request.employee_id or len(request.employee_id.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Employee ID cannot be empty"
            )
        
        if not request.employee_name or len(request.employee_name.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Employee name cannot be empty"
            )
        
        if not request.employee_solution or len(request.employee_solution.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Solution must be at least 50 characters"
            )
        
        logger.info(
            f"Submitting PDF scenario solution: {request.employee_name} "
            f"from PDF: {request.pdf_source}"
        )
        
        result = await submit_pdf_scenario_solution(
            pdf_source=request.pdf_source,
            employee_id=request.employee_id,
            employee_name=request.employee_name,
            employee_solution=request.employee_solution,
            scenario_index=request.scenario_index,
        )
        
        return result
    
    except ValueError as e:
        logger.warning(f"Invalid PDF scenario submission: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting PDF scenario solution: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit solution: {str(e)}"
        )


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
