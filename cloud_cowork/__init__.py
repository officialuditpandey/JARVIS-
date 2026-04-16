import reflex as rx
import asyncio
import json
import time
from datetime import datetime
from typing import List, Dict, Any

# Import backend modules (we'll create these next)
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.ai_engine import get_hybrid_response
from core.task_scheduler import TaskScheduler
from models.task import Task, TaskStatus
from models.status import AgentStatus

class State(rx.State):
    """The main app state."""
    
    # Agent status
    agent_status: str = "Online"
    agent_thinking: str = "Ready"
    agent_doing: str = "Idle"
    
    # Task management
    tasks: List[Task] = []
    current_task: Task = None
    
    # Vision portal
    camera_active: bool = False
    vision_analysis: str = ""
    
    # Action center
    message_recipient: str = ""
    message_content: str = ""
    
    # System info
    system_stats: Dict[str, Any] = {}
    
    def load_tasks(self):
        """Load tasks from persistent storage."""
        try:
            with open("static/data/tasks.json", "r") as f:
                tasks_data = json.load(f)
                self.tasks = [Task(**task) for task in tasks_data]
        except FileNotFoundError:
            self.tasks = []
    
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
    
    def add_task(self, title: str, description: str, task_type: str = "general"):
        """Add a new task to the queue."""
        task = Task(
            title=title,
            description=description,
            task_type=task_type,
            priority=1
        )
        self.tasks.append(task)
        self.save_tasks()
        return task
    
    def update_agent_status(self, thinking: str, doing: str):
        """Update agent status display."""
        self.agent_thinking = thinking
        self.agent_doing = doing
    
    def handle_send_message(self):
        """Handle send message button click."""
        print(f"Sending message to {self.message_recipient}: {self.message_content}")
        # Will implement actual message sending logic
    
    def handle_system_scan(self):
        """Handle system scan button click."""
        print("Starting system scan...")
        # Will implement actual system scan logic
    
    def handle_study_session(self):
        """Handle study session button click."""
        print("Starting study session...")
        # Will implement actual study session logic
    
    def handle_vision_mode(self):
        """Handle vision mode button click."""
        print("Activating vision mode...")
        # Will implement actual vision mode logic
    
    async def execute_task(self, task_id: str):
        """Execute a task asynchronously."""
        task = next((t for t in self.tasks if t.id == task_id), None)
        if not task:
            return
        
        task.status = TaskStatus.RUNNING
        self.current_task = task
        self.update_agent_status(f"Executing: {task.title}", "Processing task...")
        
        try:
            # Simulate task execution (will be replaced with actual logic)
            await asyncio.sleep(2)
            
            # Get AI response for the task
            response, source = get_hybrid_response(task.description, [])
            task.result = response
            task.status = TaskStatus.COMPLETED
            
            self.update_agent_status("Task completed", "Ready for next task")
            
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            self.update_agent_status("Error occurred", f"Failed: {e}")
        
        self.save_tasks()
        self.current_task = None

def status_monitor():
    """Real-time status monitor component."""
    return rx.card(
        rx.vstack(
            rx.heading("JARVIS Status Monitor", size="5", color="white"),
            rx.hstack(
                rx.vstack(
                    rx.text("System Status", color="gray", size="1"),
                    rx.text(State.agent_status, color="green", size="4", weight="bold"),
                ),
                rx.vstack(
                    rx.text("Thinking", color="gray", size="1"),
                    rx.text(State.agent_thinking, color="cyan", size="1"),
                ),
                rx.vstack(
                    rx.text("Doing", color="gray", size="1"),
                    rx.text(State.agent_doing, color="yellow", size="1"),
                ),
                spacing="4",
            ),
            rx.divider(color="gray"),
            rx.text(f"Last Update: {datetime.now().strftime('%H:%M:%S')}", color="gray", size="1"),
        ),
        bg="#1a1a1a",
        border="2px solid #333",
        padding="4",
        shadow="lg",
    )

def action_center():
    """Action control center component."""
    return rx.card(
        rx.vstack(
            rx.heading("Action Center", size="5", color="white"),
            
            # Message section
            rx.vstack(
                rx.heading("Send Message", size="4", color="white"),
                rx.input(
                    placeholder="Recipient",
                    value=State.message_recipient,
                    on_change=State.set_message_recipient,
                    bg="#2a2a2a",
                    color="white",
                    border_color="#444",
                ),
                rx.text_area(
                    placeholder="Message content",
                    value=State.message_content,
                    on_change=State.set_message_content,
                    bg="#2a2a2a",
                    color="white",
                    border_color="#444",
                ),
                rx.button(
                    "Send Message",
                    bg="#ff6b35",
                    color="white",
                    on_click=State.handle_send_message,
                    _hover={"bg": "#ff5722"},
                ),
                spacing="2",
            ),
            
            rx.divider(color="gray"),
            
            # Quick actions
            rx.hstack(
                rx.button(
                    "System Scan",
                    bg="#4caf50",
                    color="white",
                    on_click=State.handle_system_scan,
                    _hover={"bg": "#45a049"},
                ),
                rx.button(
                    "Study Session",
                    bg="#2196f3",
                    color="white",
                    on_click=State.handle_study_session,
                    _hover={"bg": "#1976d2"},
                ),
                rx.button(
                    "Vision Mode",
                    bg="#9c27b0",
                    color="white",
                    on_click=State.handle_vision_mode,
                    _hover={"bg": "#7b1fa2"},
                ),
                spacing="3",
            ),
        ),
        bg="#1a1a1a",
        border="2px solid #333",
        padding="4",
        shadow="lg",
    )

def vision_portal():
    """Vision portal component for camera feed."""
    return rx.card(
        rx.vstack(
            rx.heading("Vision Portal", size="5", color="white"),
            rx.cond(
                State.camera_active,
                rx.vstack(
                    rx.box(
                        width="100%",
                        height="300px",
                        bg="#000",
                        border="2px solid #444",
                        border_radius="md",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                    ),
                    rx.text("Camera Feed Active", color="green", size="1"),
                    rx.button(
                        "Stop Camera",
                        bg="#f44336",
                        color="white",
                        on_click=lambda: State.set_camera_active(False),
                        _hover={"bg": "#d32f2f"},
                    ),
                    spacing="3",
                ),
                rx.vstack(
                    rx.box(
                        width="100%",
                        height="300px",
                        bg="#2a2a2a",
                        border="2px solid #444",
                        border_radius="md",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                    ),
                    rx.text("Camera Inactive", color="gray", size="1"),
                    rx.button(
                        "Start Camera",
                        bg="#4caf50",
                        color="white",
                        on_click=lambda: State.set_camera_active(True),
                        _hover={"bg": "#45a049"},
                    ),
                    spacing="3",
                ),
            ),
            rx.divider(color="gray"),
            rx.text_area(
                placeholder="Vision analysis will appear here...",
                value=State.vision_analysis,
                bg="#2a2a2a",
                color="white",
                border_color="#444",
                read_only=True,
            ),
        ),
        bg="#1a1a1a",
        border="2px solid #333",
        padding="4",
        shadow="lg",
    )

def task_queue():
    """Task queue management component."""
    return rx.card(
        rx.vstack(
            rx.heading("Task Queue", size="5", color="white"),
            rx.foreach(
                State.tasks,
                lambda task: rx.hstack(
                    rx.vstack(
                        rx.text(task.title, color="white", weight="bold"),
                        rx.text(task.description, color="gray", size="1"),
                        rx.text(f"Status: {task.status}", color=get_status_color(task.status)),
                        spacing="1",
                    ),
                    rx.cond(
                        task.status == TaskStatus.PENDING,
                        rx.button(
                            "Execute",
                            bg="#ff6b35",
                            color="white",
                            on_click=lambda t=task: State.execute_task(t.id),
                            size="1",
                        ),
                    ),
                    spacing="3",
                    padding="2",
                    border_bottom="1px solid #333",
                ),
            ),
            spacing="3",
        ),
        bg="#1a1a1a",
        border="2px solid #333",
        padding="4",
        shadow="lg",
        max_height="400px",
        overflow_y="auto",
    )

def get_status_color(status: str) -> str:
    """Get color based on task status."""
    colors = {
        "pending": "yellow",
        "running": "blue",
        "completed": "green",
        "failed": "red"
    }
    return colors.get(status, "gray")

def dashboard():
    """Main dashboard layout."""
    return rx.vstack(
        rx.heading(
            "CLOUD COWORK - JARVIS Autonomous Agent System",
            size="8",
            color="white",
            text_align="center",
            margin_bottom="4",
        ),
        
        # Main grid layout using flexbox
        rx.flex(
            rx.vstack(
                status_monitor(),
                action_center(),
                spacing="4",
                width="50%",
            ),
            rx.vstack(
                vision_portal(),
                task_queue(),
                spacing="4",
                width="50%",
            ),
            spacing="4",
            width="100%",
        ),
        
        spacing="6",
        padding="6",
        min_height="100vh",
    )

# Iron Man theme styling
styles = [
    """
    body {
        background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%);
        color: white;
    }
    
    * {
        scrollbar-width: thin;
        scrollbar-color: #444 #1a1a1a;
    }
    
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a1a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #444;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    """
]

# Create the app
app = rx.App(
    style={
        "background": "linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%)",
        "min_height": "100vh",
    },
)

# Add the main page
app.add_page(
    dashboard,
    title="Cloud Cowork - JARVIS Dashboard",
    description="Autonomous Agent System Dashboard",
)

if __name__ == "__main__":
    import reflex as rx
    rx.run()
