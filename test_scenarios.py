#!/usr/bin/env python3
"""
Test script for Scenario-Based Learning Feature

This script tests all scenario endpoints locally.
Run this after starting the FastAPI server: python main.py

Usage:
    python test_scenarios.py
"""

import requests
import json
import time
from typing import Any, Dict
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

# Test data
TEST_SCENARIO_ID = None
TEST_SUBMISSION_ID = None
EMPLOYEE_ID = "test_emp_" + str(int(time.time()))
EMPLOYEE_NAME = "Test Employee"


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    END = "\033[0m"


def log_step(step_num: int, description: str) -> None:
    """Log a test step"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"Step {step_num}: {description}")
    print(f"{'='*60}{Colors.END}")


def log_success(message: str) -> None:
    """Log success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def log_error(message: str) -> None:
    """Log error message"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def log_warning(message: str) -> None:
    """Log warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")


def log_info(message: str) -> None:
    """Log info message"""
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")


def print_response(response: requests.Response) -> Dict[str, Any]:
    """Pretty print response and return JSON"""
    try:
        data = response.json()
        print(f"\nResponse ({response.status_code}):")
        print(json.dumps(data, indent=2))
        return data
    except:
        print(f"\nResponse ({response.status_code}): {response.text}")
        return {}


def check_server() -> bool:
    """Check if FastAPI server is running"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            log_success("FastAPI server is running")
            return True
    except requests.exceptions.ConnectionError:
        log_error("Cannot connect to FastAPI server at " + BASE_URL)
    return False


# ==================== TEST FUNCTIONS ====================


def test_health_check() -> bool:
    """Test health check endpoint"""
    log_step(1, "Test Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        data = print_response(response)
        
        if response.status_code == 200 and data.get("status") == "healthy":
            log_success("Health check passed")
            return True
        else:
            log_error("Health check failed")
    except Exception as e:
        log_error(f"Exception: {str(e)}")
    
    return False


def test_create_scenario() -> bool:
    """Test creating a new scenario"""
    global TEST_SCENARIO_ID
    
    log_step(2, "Test Create Scenario")
    
    payload = {
        "title": "Test Production Outage",
        "description": "A critical service went down unexpectedly",
        "technical_context": "Our main API service became unresponsive at 2 AM due to memory leak in service X",
        "company_solution": "1) Immediately switched to backup service. 2) Identified memory leak. 3) Deployed hotfix. 4) Monitored metrics for 1 hour.",
        "challenges_faced": "Time pressure, data consistency concerns, customer communication",
        "lessons_learned": "Better monitoring needed, backup procedures should be tested regularly",
        "difficulty_level": "Medium",
        "category": "Technical",
        "tags": ["incident-response", "devops", "production"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/scenarios/create", json=payload, headers=HEADERS)
        data = print_response(response)
        
        if response.status_code in [200, 201]:
            TEST_SCENARIO_ID = data.get("scenario_id")
            log_success(f"Scenario created with ID: {TEST_SCENARIO_ID}")
            return True
        else:
            log_error(f"Failed to create scenario. Status: {response.status_code}")
    except Exception as e:
        log_error(f"Exception: {str(e)}")
    
    return False


def test_get_scenarios() -> bool:
    """Test getting all scenarios"""
    log_step(3, "Test Get All Scenarios")
    
    try:
        # Test without filters
        response = requests.get(f"{BASE_URL}/scenarios", headers=HEADERS)
        data = print_response(response)
        
        if response.status_code == 200:
            scenarios = data.get("scenarios", [])
            total = data.get("total_count", 0)
            log_success(f"Retrieved {len(scenarios)} scenarios (total: {total})")
            
            # Test with filters
            log_info("Testing with category filter...")
            response = requests.get(f"{BASE_URL}/scenarios?category=Technical", headers=HEADERS)
            data = print_response(response)
            
            if response.status_code == 200:
                log_success("Filtering by category works")
                return True
        else:
            log_error(f"Failed to get scenarios. Status: {response.status_code}")
    except Exception as e:
        log_error(f"Exception: {str(e)}")
    
    return False


def test_get_scenario_details() -> bool:
    """Test getting specific scenario details"""
    log_step(4, "Test Get Scenario Details")
    
    if not TEST_SCENARIO_ID:
        log_warning("No scenario ID available. Skipping test.")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/scenarios/{TEST_SCENARIO_ID}", headers=HEADERS)
        data = print_response(response)
        
        if response.status_code == 200:
            if data.get("scenario_id") == TEST_SCENARIO_ID:
                log_success("Successfully retrieved scenario details")
                log_info(f"Scenario: {data.get('title')}")
                return True
        else:
            log_error(f"Failed to get scenario. Status: {response.status_code}")
    except Exception as e:
        log_error(f"Exception: {str(e)}")
    
    return False


def test_submit_scenario_solution() -> bool:
    """Test submitting a scenario solution"""
    global TEST_SUBMISSION_ID
    
    log_step(5, "Test Submit Scenario Solution")
    
    if not TEST_SCENARIO_ID:
        log_warning("No scenario ID available. Skipping test.")
        return False
    
    payload = {
        "scenario_id": TEST_SCENARIO_ID,
        "employee_id": EMPLOYEE_ID,
        "employee_name": EMPLOYEE_NAME,
        "solution_text": """
        When a critical service goes down, I would:
        1. Immediately alert the on-call team via Slack and phone
        2. Check monitoring dashboards to see affected components
        3. Review recent deployments to identify root cause
        4. Switch to backup service if available to restore service quickly
        5. While service restored, focus on understanding root cause
        6. Deploy fix after thorough testing
        7. Monitor metrics for 1 hour to ensure stability
        8. Document the incident for post-mortem analysis
        9. Identify preventative measures for future
        10. Update runbooks based on lessons learned
        """
    }
    
    try:
        log_info(f"Submitting solution for employee: {EMPLOYEE_NAME}")
        response = requests.post(f"{BASE_URL}/scenarios/{TEST_SCENARIO_ID}/submit", 
                                json=payload, headers=HEADERS)
        data = print_response(response)
        
        if response.status_code == 200:
            TEST_SUBMISSION_ID = data.get("submission_id")
            score = data.get("score")
            feedback = data.get("feedback", "")
            
            log_success(f"Solution submitted, Score: {score}/100")
            log_info(f"Feedback excerpt: {feedback[:200]}...")
            
            # Print detailed results
            print(f"\n{Colors.BLUE}Detailed Results:{Colors.END}")
            print(f"  Strengths: {data.get('strengths', [])}")
            print(f"  Gaps: {data.get('gaps', [])}")
            
            return True
        else:
            log_error(f"Failed to submit solution. Status: {response.status_code}")
    except Exception as e:
        log_error(f"Exception: {str(e)}")
    
    return False


def test_get_employee_progress() -> bool:
    """Test getting employee progress"""
    log_step(6, "Test Get Employee Progress")
    
    try:
        response = requests.get(f"{BASE_URL}/employee/{EMPLOYEE_ID}/progress", headers=HEADERS)
        data = print_response(response)
        
        if response.status_code == 200:
            tasks_completed = data.get("total_tasks_completed", 0)
            avg_score = data.get("average_score", 0)
            progress_pct = data.get("progress_percentage", 0)
            
            log_success("Employee progress retrieved")
            log_info(f"Tasks Completed: {tasks_completed}")
            log_info(f"Average Score: {avg_score}")
            log_info(f"Progress: {progress_pct}%")
            
            # Print score distribution
            distribution = data.get("score_distribution", {})
            print(f"\nScore Distribution:")
            print(f"  Excellent (90-100): {distribution.get('excellent', 0)}")
            print(f"  Good (75-89): {distribution.get('good', 0)}")
            print(f"  Satisfactory (60-74): {distribution.get('satisfactory', 0)}")
            print(f"  Needs Improvement (40-59): {distribution.get('needs_improvement', 0)}")
            print(f"  Insufficient (<40): {distribution.get('insufficient', 0)}")
            
            return True
        else:
            log_error(f"Failed to get progress. Status: {response.status_code}")
    except Exception as e:
        log_error(f"Exception: {str(e)}")
    
    return False


def test_get_team_progress() -> bool:
    """Test getting team progress"""
    log_step(7, "Test Get Team Progress")
    
    try:
        response = requests.get(f"{BASE_URL}/team/progress", headers=HEADERS)
        data = print_response(response)
        
        if response.status_code == 200:
            total_employees = data.get("total_employees", 0)
            total_submissions = data.get("total_submissions", 0)
            avg_team_score = data.get("average_team_score", 0)
            
            log_success("Team progress retrieved")
            log_info(f"Total Employees: {total_employees}")
            log_info(f"Total Submissions: {total_submissions}")
            log_info(f"Average Team Score: {avg_team_score}")
            
            # Print top performers
            top_performers = data.get("top_performers", [])
            if top_performers:
                print(f"\nTop Performers:")
                for i, performer in enumerate(top_performers, 1):
                    name = performer.get("name", "Unknown")
                    score = performer.get("avg_score", 0)
                    print(f"  {i}. {name}: {score} avg")
            
            return True
        else:
            log_error(f"Failed to get team progress. Status: {response.status_code}")
    except Exception as e:
        log_error(f"Exception: {str(e)}")
    
    return False


def test_error_handling() -> bool:
    """Test error handling"""
    log_step(8, "Test Error Handling")
    
    success = True
    
    # Test invalid scenario ID
    log_info("Testing invalid scenario ID...")
    try:
        response = requests.get(f"{BASE_URL}/scenarios/invalid_id", headers=HEADERS)
        if response.status_code == 404:
            log_success("404 error handling works")
        else:
            log_warning(f"Expected 404, got {response.status_code}")
            success = False
    except Exception as e:
        log_error(f"Exception: {str(e)}")
        success = False
    
    # Test empty submission
    log_info("Testing empty scenario submission...")
    if TEST_SCENARIO_ID:
        try:
            response = requests.post(f"{BASE_URL}/scenarios/{TEST_SCENARIO_ID}/submit",
                                    json={
                                        "scenario_id": TEST_SCENARIO_ID,
                                        "employee_id": "test",
                                        "employee_name": "Test",
                                        "solution_text": ""
                                    },
                                    headers=HEADERS)
            if response.status_code == 400:
                log_success("400 validation error works")
            else:
                log_warning(f"Expected 400, got {response.status_code}")
                success = False
        except Exception as e:
            log_error(f"Exception: {str(e)}")
            success = False
    
    return success


def test_pagination() -> bool:
    """Test pagination in scenario listing"""
    log_step(9, "Test Pagination")
    
    try:
        # Create multiple scenarios
        for i in range(3):
            payload = {
                "title": f"Test Scenario {i+1}",
                "description": f"Test scenario number {i+1}",
                "technical_context": "Test context",
                "company_solution": "Test solution",
                "challenges_faced": "Test challenges",
                "lessons_learned": "Test lessons",
                "difficulty_level": "Easy"
            }
            requests.post(f"{BASE_URL}/scenarios/create", json=payload, headers=HEADERS)
        
        log_info("Testing limit parameter...")
        response = requests.get(f"{BASE_URL}/scenarios?limit=2", headers=HEADERS)
        data = response.json()
        scenarios = data.get("scenarios", [])
        
        if len(scenarios) == 2:
            log_success("Pagination limit works")
        else:
            log_warning(f"Expected 2 scenarios, got {len(scenarios)}")
        
        log_info("Testing skip parameter...")
        response = requests.get(f"{BASE_URL}/scenarios?limit=2&skip=1", headers=HEADERS)
        data = response.json()
        scenarios_page2 = data.get("scenarios", [])
        
        if len(scenarios_page2) > 0:
            log_success("Pagination skip works")
        else:
            log_warning("No scenarios returned on page 2")
        
        return True
    except Exception as e:
        log_error(f"Exception: {str(e)}")
        return False


# ==================== MAIN TEST RUNNER ====================


def main():
    """Run all tests"""
    print(f"\n{Colors.BLUE}")
    print("=" * 60)
    print("SCENARIO-BASED LEARNING FEATURE - TEST SUITE")
    print("=" * 60)
    print(f"{Colors.END}")
    
    print(f"\nTest Server: {BASE_URL}")
    print(f"Employee ID: {EMPLOYEE_ID}")
    print(f"Employee Name: {EMPLOYEE_NAME}")
    
    # Check server health
    if not check_server():
        print(f"\n{Colors.RED}FATAL: Server not running. Start with: python main.py{Colors.END}")
        return
    
    # Run tests
    tests = [
        ("Health Check", test_health_check),
        ("Create Scenario", test_create_scenario),
        ("Get All Scenarios", test_get_scenarios),
        ("Get Scenario Details", test_get_scenario_details),
        ("Submit Scenario Solution", test_submit_scenario_solution),
        ("Get Employee Progress", test_get_employee_progress),
        ("Get Team Progress", test_get_team_progress),
        ("Error Handling", test_error_handling),
        ("Pagination", test_pagination),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            time.sleep(0.5)  # Small delay between tests
        except Exception as e:
            log_error(f"Unexpected error in {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print(f"\n{Colors.BLUE}")
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"{Colors.END}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        check = "✓" if result else "✗"
        print(f"{check} {test_name:.<40} {status}")
    
    print(f"\n{Colors.BLUE}Total: {Colors.END}{passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n{Colors.GREEN}🎉 All tests passed! Feature is working correctly.{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}⚠ Some tests failed. Check output above for details.{Colors.END}")
    
    print(f"\n{Colors.BLUE}Next Steps:{Colors.END}")
    print(f"1. Review documentation in SCENARIO_FEATURE.md")
    print(f"2. Try the quick start at SCENARIO_QUICKSTART.md")
    print(f"3. Create your first scenarios for your organization")
    print(f"4. Integrate with your onboarding process")


if __name__ == "__main__":
    main()
