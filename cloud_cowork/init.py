#!/usr/bin/env python3
"""
Initialize Cloud Cowork system and test components
"""

import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

def test_imports():
    """Test all backend imports"""
    print("=== Testing Backend Imports ===")
    
    try:
        from backend.models.task import Task, TaskStatus, TaskType
        print("Task models: OK")
    except Exception as e:
        print(f"Task models: ERROR - {e}")
    
    try:
        from backend.models.status import AgentState
        print("Status models: OK")
    except Exception as e:
        print(f"Status models: ERROR - {e}")
    
    try:
        from backend.core.ai_engine import get_hybrid_response, check_model_availability
        print("AI Engine: OK")
    except Exception as e:
        print(f"AI Engine: ERROR - {e}")
    
    try:
        from backend.core.task_scheduler import TaskScheduler
        print("Task Scheduler: OK")
    except Exception as e:
        print(f"Task Scheduler: ERROR - {e}")

def test_ai_engine():
    """Test the AI engine functionality"""
    print("\n=== Testing AI Engine ===")
    
    try:
        from backend.core.ai_engine import get_hybrid_response, check_model_availability
        
        # Check model availability
        llama_available = check_model_availability("llama3.1:8b")
        print(f"LLaMA 3.1 8B available: {llama_available}")
        
        # Test hybrid response
        response, source = get_hybrid_response("What is 2+2?", [])
        print(f"Test response: {response}")
        print(f"Source: {source}")
        
    except Exception as e:
        print(f"AI Engine test failed: {e}")

def test_task_system():
    """Test the task management system"""
    print("\n=== Testing Task System ===")
    
    try:
        from backend.models.task import Task, TaskStatus
        from backend.core.task_scheduler import TaskScheduler
        
        # Create a task scheduler
        scheduler = TaskScheduler()
        print("Task Scheduler created")
        
        # Add a test task
        task = scheduler.add_task(
            title="Test Task",
            description="Calculate 5+3",
            task_type="general",
            priority=1
        )
        print(f"Task created: {task.title}")
        
        # Get status
        status = scheduler.get_status()
        print(f"Scheduler status: {status}")
        
    except Exception as e:
        print(f"Task system test failed: {e}")

def test_reflex_app():
    """Test Reflex app initialization"""
    print("\n=== Testing Reflex App ===")
    
    try:
        import reflex as rx
        print("Reflex imported successfully")
        
        # Try to import the main app
        import cloud_cowork
        print("Cloud Cowork app imported successfully")
        
    except Exception as e:
        print(f"Reflex app test failed: {e}")

if __name__ == "__main__":
    print("Cloud Cowork System Initialization Test")
    print("=" * 50)
    
    test_imports()
    test_ai_engine()
    test_task_system()
    test_reflex_app()
    
    print("\n=== Initialization Complete ===")
    print("To start the dashboard, run: python run.py")
