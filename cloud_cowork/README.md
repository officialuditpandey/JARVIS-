# Cloud Cowork - JARVIS Autonomous Agent System

## Project Overview
Transform JARVIS from a voice assistant into a full-stack autonomous agent system with a Reflex dashboard for background task management, scheduling, and vision capabilities.

## Architecture

### Backend Structure
```
backend/
  core/           # Core JARVIS engine extracted from original script
    - ai_engine.py      # Hybrid AI response system (Gemini + Ollama)
    - voice_engine.py   # TTS and speech recognition
    - memory_system.py  # Memory management
    - task_scheduler.py # Background task execution
    
  integrations/   # External service integrations
    - whatsapp.py      # WhatsApp automation
    - camera.py        # Vision and camera controls
    - system_control.py # Volume, brightness, etc.
    - omnichannel.py   # Telegram/Discord framework
    
  tasks/          # Task management system
    - task_manager.py  # Persistent task queue
    - agent_loop.py    # Background agent execution
    - task_types.py    # Multi-step task definitions
    
  models/         # Data models
    - task.py         # Task data structure
    - status.py       # Agent status tracking
```

### Frontend Structure
```
frontend/
  components/     # Reusable UI components
    - status_monitor.py   # Real-time JARVIS status
    - action_center.py    # Control buttons
    - vision_portal.py    # Camera feed interface
    - task_queue.py       # Task management UI
    
  pages/          # Full page layouts
    - dashboard.py    # Main dashboard
    - settings.py     # Configuration
    - logs.py         # Activity logs
    
  styles/         # Iron Man dark theme
    - theme.py       # Color schemes and styling
```

### Static Data
```
static/
  data/           # Persistent storage
    - tasks.json       # Task queue
    - memory.json      # JARVIS memory
    - config.json      # System configuration
    
  logs/           # Activity logs
    - agent.log        # Agent activity
    - errors.log       # Error tracking
```

## Key Features

### 1. Persistent Task Manager
- Background "Agent Loop" for multi-step tasks
- Task queue persistence in JSON
- Automatic task scheduling and execution

### 2. Reflex Dashboard UI
- Iron Man dark theme design
- Real-time status monitoring
- Interactive action center
- Vision portal with live camera feed

### 3. Omnichannel Integration
- Framework for Telegram/Discord
- Remote control capabilities
- Message routing system

### 4. Hardware Optimization
- Async AI calls (RTX 3050 optimized)
- Non-blocking UI operations
- Efficient resource management

## Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Initialize Reflex app: `reflex init`
3. Run dashboard: `python cloud_cowork.py`
4. Access at: `http://localhost:3000`

## Dependencies
- reflex (Python web framework)
- ollama (Local AI models)
- opencv-python (Computer vision)
- pyttsx3 (Text-to-speech)
- All original JARVIS dependencies
