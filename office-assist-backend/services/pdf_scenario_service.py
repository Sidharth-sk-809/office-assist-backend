"""
PDF-based Scenario Service for employee learning.
Extracts scenarios from PDFs (like Product Document.pdf, Welcome Aboard.pdf)
and compares user solutions with PDF content using RAG + Gemini.
"""

from google.cloud import firestore
from google.cloud import storage
from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.client_options import ClientOptions
from vertexai.generative_models import GenerativeModel
import vertexai
import os
import logging
from typing import Dict, Optional, List
from datetime import datetime
import uuid
import json
import PyPDF2
import random
import io

logger = logging.getLogger(__name__)

# Initialize Vertex AI and Firestore
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_LOCATION", "us-central1")
GCS_BUCKET = os.getenv("GCS_BUCKET_NAME", f"{PROJECT_ID}-office-assist")
DATA_STORE_ID = os.getenv("VERTEX_SEARCH_DATA_STORE_ID")

if LOCATION == "global":
    LOCATION = "us-central1"

if PROJECT_ID:
    vertexai.init(project=PROJECT_ID, location=LOCATION)

# Initialize clients
db = firestore.Client(project=PROJECT_ID) if PROJECT_ID else None
storage_client = storage.Client(project=PROJECT_ID) if PROJECT_ID else None


# ==================== PDF PROCESSING ====================

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path: Path to PDF file (GCS URI or local path)
        
    Returns:
        Extracted text content
    """
    try:
        if pdf_path.startswith("gs://"):
            # Handle GCS URI
            bucket_name = pdf_path.split("/")[2]
            blob_name = "/".join(pdf_path.split("/")[3:])
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            pdf_content = blob.download_as_bytes()
        else:
            # Handle local file
            with open(pdf_path, "rb") as f:
                pdf_content = f.read()
        
        # Extract text using PyPDF2
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        extracted_text = ""
        
        for page in pdf_reader.pages:
            extracted_text += page.extract_text() + "\n"
        
        logger.info(f"Extracted {len(pdf_reader.pages)} pages from PDF")
        return extracted_text
    
    except Exception as e:
        logger.error(f"Error extracting PDF text: {str(e)}")
        raise


def extract_scenarios_from_pdf_text(pdf_text: str, num_scenarios: int = 5) -> List[Dict]:
    """
    Use Gemini to extract scenario problems and solutions from PDF text.
    
    Args:
        pdf_text: Full text extracted from PDF
        num_scenarios: Number of scenarios to extract
        
    Returns:
        List of scenario dictionaries with problem and solution
    """
    try:
        model = GenerativeModel("gemini-2.5-pro")
        
        # Limit PDF text to avoid token limits
        pdf_text_limited = pdf_text[:10000]
        
        extraction_prompt = f"""
        Analyze the following document text and identify {num_scenarios} key scenarios or case studies that:
        1. Represent real-world challenges or problems
        2. Include or imply a solution or best practice
        3. Would be valuable learning opportunities for new employees
        
        Document Text:
        {pdf_text_limited}
        
        For each scenario identified, provide response in JSON format:
        {{
            "scenarios": [
                {{
                    "title": "Scenario Title",
                    "problem": "What is the challenge or problem described?",
                    "solution": "What is the recommended solution or approach?",
                    "category": "Technical|HR|Project Management|Security|Other",
                    "difficulty": "Easy|Medium|Hard",
                    "key_points": ["point1", "point2", "point3"]
                }}
            ]
        }}
        
        If fewer than {num_scenarios} distinct scenarios are found, return only what you find.
        Ensure all scenarios are directly extractable from the document.
        """
        
        response = model.generate_content(extraction_prompt)
        result_text = response.text
        
        # Parse JSON response
        try:
            if "```json" in result_text:
                json_str = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                json_str = result_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = result_text
            
            parsed = json.loads(json_str)
            scenarios = parsed.get("scenarios", [])
            
            logger.info(f"Extracted {len(scenarios)} scenarios from PDF")
            return scenarios
        
        except json.JSONDecodeError:
            logger.warning(f"Could not parse Gemini response: {result_text[:200]}")
            return []
    
    except Exception as e:
        logger.error(f"Error extracting scenarios: {str(e)}")
        raise


async def create_scenario_from_pdf(
    pdf_source: str,  # GCS URI or local path
    scenario_index: Optional[int] = None,  # Specific scenario, or None for random
) -> Dict:
    """
    Create a scenario from PDF content or retrieve existing one.
    
    Args:
        pdf_source: Path to PDF file
        scenario_index: Optional index of which scenario to retrieve
        
    Returns:
        Scenario dictionary with all details
    """
    try:
        if not db:
            raise ValueError("Firestore not initialized")
        
        # Check if we've already processed this PDF
        pdf_hash = hash(pdf_source)
        existing = db.collection("pdf_scenarios").document(str(pdf_hash)).get()
        
        if existing.exists:
            scenarios_data = existing.to_dict()
            scenarios = scenarios_data.get("scenarios", [])
            
            if not scenarios:
                raise ValueError("No scenarios found in PDF")
            
            # Select random or specific scenario
            if scenario_index is not None and 0 <= scenario_index < len(scenarios):
                selected = scenarios[scenario_index]
            else:
                selected = random.choice(scenarios)
            
            logger.info(f"Using cached scenario from PDF: {selected.get('title')}")
            return selected
        
        # First time processing this PDF - extract scenarios
        logger.info(f"Processing PDF for first time: {pdf_source}")
        
        pdf_text = extract_text_from_pdf(pdf_source)
        extracted_scenarios = extract_scenarios_from_pdf_text(pdf_text)
        
        if not extracted_scenarios:
            raise ValueError("Could not extract scenarios from PDF")
        
        # Cache scenarios in Firestore
        db.collection("pdf_scenarios").document(str(pdf_hash)).set({
            "pdf_source": pdf_source,
            "scenarios": extracted_scenarios,
            "created_at": datetime.utcnow(),
            "total_scenarios": len(extracted_scenarios),
        })
        
        # Return random scenario from extracted set
        selected = random.choice(extracted_scenarios)
        logger.info(f"Created {len(extracted_scenarios)} scenarios from PDF")
        
        return selected
    
    except Exception as e:
        logger.error(f"Error creating scenario from PDF: {str(e)}")
        raise


# ==================== SOLUTION COMPARISON ====================

async def compare_solution_with_pdf(
    pdf_source: str,
    pdf_scenario: Dict,
    employee_solution: str,
    employee_name: str,
) -> Dict:
    """
    Compare employee solution with solution in PDF using RAG + Gemini.
    
    Args:
        pdf_source: Path to PDF source
        pdf_scenario: The scenario extracted from PDF
        employee_solution: Employee's proposed solution
        employee_name: Employee name
        
    Returns:
        Comparison results with score and feedback
    """
    try:
        # Get full PDF text for context
        pdf_text = extract_text_from_pdf(pdf_source)
        
        # Use RAG to find relevant content for comparison
        rag_context = await _query_rag_for_context(
            pdf_scenario.get("problem", ""),
            pdf_scenario.get("solution", "")
        )
        
        # Compare using Gemini
        model = GenerativeModel("gemini-2.5-pro")
        
        comparison_prompt = f"""
        You are an expert evaluator comparing an employee's solution with a documented solution
        found in company materials.
        
        DOCUMENTED PROBLEM:
        {pdf_scenario.get('problem', '')}
        
        DOCUMENTED SOLUTION FROM PDF:
        {pdf_scenario.get('solution', '')}
        
        KEY POINTS FROM DOCUMENTATION:
        {', '.join(pdf_scenario.get('key_points', []))}
        
        ADDITIONAL CONTEXT FROM PDF:
        {rag_context[:2000]}
        
        EMPLOYEE'S SOLUTION (by {employee_name}):
        {employee_solution}
        
        Please provide a detailed comparison analysis in this JSON format:
        {{
            "score": <0-100 score based on alignment with documented solution>,
            "alignment_summary": "<How well does approach align with documentation>",
            "strengths": [
                "<strength 1>",
                "<strength 2>"
            ],
            "gaps": [
                "<gap 1: what was missed from documentation>",
                "<gap 2>"
            ],
            "references_to_doc": [
                "<How employee's point relates to documentation>"
            ],
            "improvement_suggestions": "<Specific improvements based on documented approach>",
            "feedback": "<Actionable feedback for improvement>"
        }}
        
        Scoring guidelines:
        - 90-100: Excellent - Incorporates all key documented points
        - 75-89: Good - Covers most documented approach
        - 60-74: Satisfactory - Contains some documented points
        - 40-59: Needs Improvement - Misses several from documentation
        - Below 40: Insufficient - Fundamentally different from documented solution
        """
        
        response = model.generate_content(comparison_prompt)
        result_text = response.text
        
        # Parse response
        try:
            if "```json" in result_text:
                json_str = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                json_str = result_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = result_text
            
            comparison = json.loads(json_str)
        except json.JSONDecodeError:
            logger.warning("Could not parse comparison JSON")
            comparison = {
                "score": 50,
                "alignment_summary": "Unable to parse detailed comparison",
                "strengths": [],
                "gaps": ["Full analysis unavailable"],
                "improvement_suggestions": result_text[:500],
                "feedback": result_text[:1000],
            }
        
        return comparison
    
    except Exception as e:
        logger.error(f"Error comparing solution: {str(e)}")
        raise


async def _query_rag_for_context(problem: str, solution: str) -> str:
    """
    Query Vertex AI Search (RAG) for additional context on the problem/solution.
    Uses existing RAG setup for policy documents.
    
    Args:
        problem: Problem statement
        solution: Solution statement
        
    Returns:
        Additional context from RAG
    """
    try:
        if not DATA_STORE_ID or not PROJECT_ID:
            return ""
        
        client_options = ClientOptions(
            api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com"
        )
        client = discoveryengine.SearchServiceClient(client_options=client_options)
        
        serving_config = (
            f"projects/{PROJECT_ID}/locations/{LOCATION}/"
            f"collections/default_collection/dataStores/{DATA_STORE_ID}/"
            f"servingConfigs/default_search"
        )
        
        query = f"{problem} {solution}"
        
        request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query=query,
            page_size=3,
        )
        
        response = client.search(request)
        
        context = ""
        for result in response.results:
            if hasattr(result, 'document') and result.document.struct_data:
                for key, value in result.document.struct_data.items():
                    context += f"{key}: {value}\n"
        
        return context
    
    except Exception as e:
        logger.warning(f"RAG context query failed: {str(e)}")
        return ""


# ==================== API WRAPPER ====================

async def submit_pdf_scenario_solution(
    pdf_source: str,
    employee_id: str,
    employee_name: str,
    employee_solution: str,
    scenario_index: Optional[int] = None,  # For specific scenarios
) -> Dict:
    """
    Complete flow: Get PDF scenario, receive solution, compare with PDF content.
    
    Args:
        pdf_source: Path to PDF (e.g., "gs://bucket/Product Document.pdf")
        employee_id: Employee identifier
        employee_name: Employee name
        employee_solution: Employee's proposed solution
        scenario_index: Optional specific scenario index
        
    Returns:
        Complete submission with feedback
    """
    try:
        if not employee_solution or len(employee_solution.strip()) < 50:
            raise ValueError("Solution must be at least 50 characters")
        
        # Get scenario from PDF (or random if not cached)
        pdf_scenario = await create_scenario_from_pdf(pdf_source, scenario_index)
        
        # Compare solution with PDF content
        comparison = await compare_solution_with_pdf(
            pdf_source=pdf_source,
            pdf_scenario=pdf_scenario,
            employee_solution=employee_solution,
            employee_name=employee_name,
        )
        
        # Store submission in Firestore
        submission_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        submission_data = {
            "submission_id": submission_id,
            "pdf_source": pdf_source,
            "scenario_title": pdf_scenario.get("title", ""),
            "employee_id": employee_id,
            "employee_name": employee_name,
            "employee_solution": employee_solution,
            "comparison_score": comparison.get("score", 0),
            "alignment_summary": comparison.get("alignment_summary", ""),
            "strengths": comparison.get("strengths", []),
            "gaps": comparison.get("gaps", []),
            "references_to_doc": comparison.get("references_to_doc", []),
            "improvement_suggestions": comparison.get("improvement_suggestions", ""),
            "feedback": comparison.get("feedback", ""),
            "pdf_solution": pdf_scenario.get("solution", ""),
            "submitted_at": timestamp,
        }
        
        db.collection("pdf_submissions").document(submission_id).set(submission_data)
        
        logger.info(
            f"PDF Submission created: {submission_id} "
            f"(Employee: {employee_name}, Score: {comparison.get('score')})"
        )
        
        return {
            "submission_id": submission_id,
            "scenario_title": pdf_scenario.get("title", ""),
            "scenario_category": pdf_scenario.get("category", ""),
            "scenario_difficulty": pdf_scenario.get("difficulty", ""),
            "score": comparison.get("score"),
            "alignment_summary": comparison.get("alignment_summary"),
            "strengths": comparison.get("strengths", []),
            "gaps": comparison.get("gaps", []),
            "references_to_doc": comparison.get("references_to_doc", []),
            "improvement_suggestions": comparison.get("improvement_suggestions"),
            "feedback": comparison.get("feedback"),
            "pdf_solution": pdf_scenario.get("solution", ""),
            "submitted_at": timestamp.isoformat(),
        }
    
    except Exception as e:
        logger.error(f"Error submitting PDF scenario solution: {str(e)}")
        raise


async def get_pdf_scenario(pdf_source: str, scenario_index: Optional[int] = None) -> Dict:
    """
    Get a scenario from PDF without submitting a solution yet.
    Useful for displaying scenario to employee before they solve it.
    
    Args:
        pdf_source: Path to PDF
        scenario_index: Optional specific scenario
        
    Returns:
        Scenario details (without solution initially)
    """
    try:
        scenario = await create_scenario_from_pdf(pdf_source, scenario_index)
        
        return {
            "title": scenario.get("title", ""),
            "problem": scenario.get("problem", ""),
            "category": scenario.get("category", ""),
            "difficulty": scenario.get("difficulty", ""),
            "key_points": scenario.get("key_points", []),
            # Note: Solution intentionally NOT included until comparison
        }
    
    except Exception as e:
        logger.error(f"Error getting PDF scenario: {str(e)}")
        raise


async def list_available_pdf_sources() -> List[Dict]:
    """
    List all available PDFs that contain scenarios (e.g., Product Document.pdf, Welcome Aboard.pdf).
    
    Returns:
        List of available PDF sources with metadata
    """
    try:
        if not db:
            raise ValueError("Firestore not initialized")
        
        # Query cached PDF scenarios
        docs = db.collection("pdf_scenarios").stream()
        
        pdf_sources = []
        for doc in docs:
            data = doc.to_dict()
            pdf_sources.append({
                "pdf_source": data.get("pdf_source", ""),
                "total_scenarios": data.get("total_scenarios", 0),
                "created_at": data.get("created_at", "").isoformat() if data.get("created_at") else "",
                "scenarios_sample": [
                    s.get("title", "") for s in data.get("scenarios", [])[:3]
                ],
            })
        
        return pdf_sources
    
    except Exception as e:
        logger.error(f"Error listing PDF sources: {str(e)}")
        raise
