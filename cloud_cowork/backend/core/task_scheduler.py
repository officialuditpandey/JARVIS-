import asyncio
import json
import os
import threading
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from backend.models.task import Task, TaskStatus
from backend.models.status import AgentState
from backend.core.ai_engine import get_hybrid_response_async

class TaskScheduler:
    """Persistent task manager with background agent loop."""
    
    def __init__(self):
        self.tasks: List[Task] = []
        self.agent_state = AgentState()
        self.running = False
        self.agent_thread: Optional[threading.Thread] = None
        self.task_queue = []
        self.load_tasks()
    
    def load_tasks(self):
        """Load tasks from persistent storage."""
        try:
            with open("static/data/tasks.json", "r") as f:
                tasks_data = json.load(f)
                self.tasks = [Task.from_dict(task) for task in tasks_data]
                self.task_queue = [task for task in self.tasks if task.status == TaskStatus.PENDING]
        except FileNotFoundError:
            self.tasks = []
            self.task_queue = []
        except Exception as e:
            print(f"Error loading tasks: {e}")
            self.tasks = []
            self.task_queue = []
    
    def save_tasks(self):
        """Save tasks to persistent storage."""
        try:
            os.makedirs("static/data", exist_ok=True)
            with open("static/data/tasks.json", "w") as f:
                # Convert tasks to JSON-serializable format
                tasks_data = []
                for task in self.tasks:
                    task_dict = task.model_dump()
                    # Convert datetime objects to ISO strings
                    if task_dict.get("created_at"):
                        task_dict["created_at"] = task_dict["created_at"].isoformat()
                    if task_dict.get("started_at"):
                        task_dict["started_at"] = task_dict["started_at"].isoformat()
                    if task_dict.get("completed_at"):
                        task_dict["completed_at"] = task_dict["completed_at"].isoformat()
                    tasks_data.append(task_dict)
                json.dump(tasks_data, f, indent=2)
        except Exception as e:
            print(f"Error saving tasks: {e}")
    
    def add_task(self, title: str, description: str, task_type: str = "general", priority: int = 1) -> Task:
        """Add a new task to the queue."""
        task = Task(
            title=title,
            description=description,
            task_type=task_type,
            priority=priority
        )
        self.tasks.append(task)
        if task.status == TaskStatus.PENDING:
            self.task_queue.append(task)
        self.save_tasks()
        return task
    
    def start_agent_loop(self):
        """Start the background agent loop."""
        if self.running:
            return
        
        self.running = True
        self.agent_thread = threading.Thread(target=self._agent_loop, daemon=True)
        self.agent_thread.start()
        print("Agent loop started")
    
    def stop_agent_loop(self):
        """Stop the background agent loop."""
        self.running = False
        if self.agent_thread:
            self.agent_thread.join(timeout=5)
        print("Agent loop stopped")
    
    def _agent_loop(self):
        """Background agent execution loop."""
        while self.running:
            try:
                if self.task_queue:
                    # Get next task (sorted by priority)
                    self.task_queue.sort(key=lambda t: t.priority, reverse=True)
                    task = self.task_queue[0]
                    
                    if task.status == TaskStatus.PENDING:
                        self._execute_task(task)
                
                # Sleep to prevent CPU spinning
                threading.Event().wait(1)
                
            except Exception as e:
                print(f"Agent loop error: {e}")
                self.agent_state.set_error(str(e))
                threading.Event().wait(5)  # Wait longer on error
    
    def _execute_task(self, task: Task):
        """Execute a single task."""
        try:
            task.start()
            self.agent_state.set_current_task(task.id)
            self.save_tasks()
            
            print(f"Executing task: {task.title}")
            
            # Execute based on task type
            if task.task_type.value == "research":
                result = self._execute_research_task(task)
            elif task.task_type.value == "message":
                result = self._execute_message_task(task)
            elif task.task_type.value == "vision":
                result = self._execute_vision_task(task)
            elif task.task_type.value == "system":
                result = self._execute_system_task(task)
            else:
                result = self._execute_general_task(task)
            
            task.complete(result)
            self.agent_state.clear_current_task()
            self.task_queue.remove(task)
            self.save_tasks()
            
            print(f"Task completed: {task.title}")
            
        except Exception as e:
            task.fail(str(e))
            self.agent_state.set_error(str(e))
            self.save_tasks()
            print(f"Task failed: {task.title} - {e}")
    
    def _execute_general_task(self, task: Task) -> str:
        """Execute a general AI task."""
        try:
            # Run async function in thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response, source = loop.run_until_complete(
                get_hybrid_response_async(task.description, [])
            )
            loop.close()
            return f"[{source}] {response}"
        except Exception as e:
            return f"Error executing general task: {e}"
    
    def _execute_research_task(self, task: Task) -> str:
        """Execute a research task (multi-step)."""
        try:
            # Step 1: Generate search queries
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            search_prompt = f"Generate 3 specific search queries to research: {task.description}"
            queries_response, _ = loop.run_until_complete(
                get_hybrid_response_async(search_prompt, [])
            )
            
            # Step 2: Simulate web search (would integrate with actual search)
            search_results = f"Research results for: {task.description}\n\nQueries generated: {queries_response}\n\n(Simulated web search results would appear here)"
            
            # Step 3: Synthesize results
            synthesis_prompt = f"Synthesize these research results into a comprehensive report: {search_results}"
            final_response, source = loop.run_until_complete(
                get_hybrid_response_async(synthesis_prompt, [])
            )
            
            loop.close()
            return f"[{source}] Research completed: {final_response}"
            
        except Exception as e:
            return f"Error executing research task: {e}"
    
    def _execute_message_task(self, task: Task) -> str:
        """Execute a message sending task."""
        try:
            # Extract recipient and message from task description
            # This would integrate with the WhatsApp system
            return f"Message task executed: {task.description} (Integration pending)"
        except Exception as e:
            return f"Error executing message task: {e}"
    
    def _execute_vision_task(self, task: Task) -> str:
        """Execute a vision analysis task."""
        try:
            # This would integrate with the camera and vision system
            return f"Vision task executed: {task.description} (Integration pending)"
        except Exception as e:
            return f"Error executing vision task: {e}"
    
    def _execute_system_task(self, task: Task) -> str:
        """Execute a system control task."""
        try:
            # This would integrate with system controls
            return f"System task executed: {task.description} (Integration pending)"
        except Exception as e:
            return f"Error executing system task: {e}"
    
    def get_status(self) -> Dict[str, Any]:
        """Get current scheduler status."""
        return {
            "agent_state": self.agent_state.to_dict(),
            "total_tasks": len(self.tasks),
            "pending_tasks": len([t for t in self.tasks if t.status == TaskStatus.PENDING]),
            "running_tasks": len([t for t in self.tasks if t.status == TaskStatus.RUNNING]),
            "completed_tasks": len([t for t in self.tasks if t.status == TaskStatus.COMPLETED]),
            "failed_tasks": len([t for t in self.tasks if t.status == TaskStatus.FAILED]),
            "agent_loop_running": self.running,
        }
