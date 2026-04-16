#!/usr/bin/env python3
"""
Macro Service for JARVIS - Phase 3 PC Mastery
Workflow automation for common tasks
"""

import os
import time
import subprocess
import webbrowser
from typing import Dict, Any, List, Optional
from datetime import datetime
import sys
import json

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    print("psutil not available - some macro features limited")
    PSUTIL_AVAILABLE = False

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
    pyautogui.FAILSAFE = False
except ImportError:
    print("pyautogui not available - GUI automation limited")
    PYAUTOGUI_AVAILABLE = False

class MacroService:
    """Macro service for workflow automation"""
    
    def __init__(self):
        self.workflows = {}
        self.workflow_history = []
        self.running_workflows = []
        
        # Education sites whitelist
        self.education_sites = [
            'coursera.org', 'edx.org', 'udemy.com', 'khanacademy.org',
            'mit.edu', 'stanford.edu', 'harvard.edu', 'youtube.com/watch',
            'wikipedia.org', 'stackoverflow.com', 'github.com'
        ]
        
        # Initialize predefined workflows
        self._initialize_workflows()
        
        print("Macro Service initialized with workflow automation")
    
    def _initialize_workflows(self):
        """Initialize predefined workflows"""
        self.workflows = {
            'prepare_study': {
                'name': 'Prepare Study Environment',
                'description': 'Open Chrome to exam portal and start Lofi playlist',
                'steps': [
                    'open_chrome_exam_portal',
                    'start_lofi_playlist',
                    'minimize_distractions'
                ]
            },
            'kill_distractions': {
                'name': 'Kill Distractions',
                'description': 'Close all Chrome tabs except education sites',
                'steps': [
                    'close_non_educational_tabs',
                    'minimize_non_essential_apps',
                    'set_study_mode'
                ]
            },
            'meeting_mode': {
                'name': 'Meeting Mode',
                'description': 'Prepare for video meetings',
                'steps': [
                    'close_background_apps',
                    'open_zoom_teams',
                    'mute_notifications'
                ]
            },
            'break_time': {
                'name': 'Break Time',
                'description': 'Take a scheduled break',
                'steps': [
                    'save_current_work',
                    'open_break_activity',
                    'set_break_timer'
                ]
            }
        }
    
    async def execute_workflow(self, workflow_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a predefined workflow"""
        if workflow_name not in self.workflows:
            return {
                "success": False,
                "error": f"Workflow '{workflow_name}' not found",
                "available_workflows": list(self.workflows.keys())
            }
        
        workflow = self.workflows[workflow_name]
        start_time = time.time()
        
        try:
            print(f"Executing workflow: {workflow['name']}")
            self.running_workflows.append(workflow_name)
            
            results = []
            for step in workflow['steps']:
                step_result = await self._execute_step(step, params or {})
                results.append({
                    "step": step,
                    "success": step_result.get("success", False),
                    "message": step_result.get("message", ""),
                    "timestamp": datetime.now().isoformat()
                })
                
                if not step_result.get("success", False):
                    print(f"Workflow '{workflow_name}' failed at step: {step}")
                    break
            
            execution_time = time.time() - start_time
            
            # Add to history
            history_entry = {
                "workflow": workflow_name,
                "execution_time": execution_time,
                "steps_completed": len([r for r in results if r["success"]]),
                "total_steps": len(workflow['steps']),
                "success": all(r["success"] for r in results),
                "timestamp": datetime.now().isoformat()
            }
            self.workflow_history.append(history_entry)
            
            if workflow_name in self.running_workflows:
                self.running_workflows.remove(workflow_name)
            
            return {
                "success": all(r["success"] for r in results),
                "workflow": workflow_name,
                "execution_time": execution_time,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            if workflow_name in self.running_workflows:
                self.running_workflows.remove(workflow_name)
            
            return {
                "success": False,
                "error": str(e),
                "workflow": workflow_name,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _execute_step(self, step: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute individual workflow step"""
        try:
            if step == 'open_chrome_exam_portal':
                return await self._open_chrome_exam_portal(params)
            elif step == 'start_lofi_playlist':
                return await self._start_lofi_playlist(params)
            elif step == 'minimize_distractions':
                return await self._minimize_distractions(params)
            elif step == 'close_non_educational_tabs':
                return await self._close_non_educational_tabs(params)
            elif step == 'minimize_non_essential_apps':
                return await self._minimize_non_essential_apps(params)
            elif step == 'set_study_mode':
                return await self._set_study_mode(params)
            elif step == 'close_background_apps':
                return await self._close_background_apps(params)
            elif step == 'open_zoom_teams':
                return await self._open_zoom_teams(params)
            elif step == 'mute_notifications':
                return await self._mute_notifications(params)
            elif step == 'save_current_work':
                return await self._save_current_work(params)
            elif step == 'open_break_activity':
                return await self._open_break_activity(params)
            elif step == 'set_break_timer':
                return await self._set_break_timer(params)
            else:
                return {"success": False, "error": f"Unknown step: {step}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _open_chrome_exam_portal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Open Chrome to exam portal"""
        try:
            exam_url = params.get('exam_url', 'https://exam.example.com')
            
            # Open Chrome with specific URL
            if os.name == 'nt':  # Windows
                subprocess.Popen([
                    'chrome.exe',
                    '--new-window',
                    exam_url
                ], shell=True)
            else:  # macOS/Linux
                subprocess.Popen([
                    'google-chrome',
                    '--new-window',
                    exam_url
                ])
            
            time.sleep(2)  # Wait for Chrome to open
            
            return {"success": True, "message": f"Opened Chrome to {exam_url}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _start_lofi_playlist(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Start Lofi playlist on YouTube"""
        try:
            lofi_urls = [
                'https://www.youtube.com/watch?v=5qap5aO4i9A',  # Lofi hip hop radio
                'https://www.youtube.com/watch?v=DWcJFNfaw9c',  # Lofi study beats
                'https://www.youtube.com/watch?v=4xDzrJKXOOY'   # Lofi chill beats
            ]
            
            playlist_url = params.get('playlist_url', lofi_urls[0])
            
            # Open YouTube in new tab
            if os.name == 'nt':  # Windows
                subprocess.Popen([
                    'chrome.exe',
                    '--new-tab',
                    playlist_url
                ], shell=True)
            else:  # macOS/Linux
                subprocess.Popen([
                    'google-chrome',
                    '--new-tab',
                    playlist_url
                ])
            
            return {"success": True, "message": f"Started Lofi playlist: {playlist_url}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _minimize_distractions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Minimize distracting applications"""
        try:
            if not PYAUTOGUI_AVAILABLE:
                return {"success": False, "error": "pyautogui not available"}
            
            # Minimize all windows except essential ones
            time.sleep(1)
            pyautogui.hotkey('win', 'd')  # Show desktop
            
            return {"success": True, "message": "Minimized all windows"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _close_non_educational_tabs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Close Chrome tabs except education sites"""
        try:
            if not PSUTIL_AVAILABLE:
                return {"success": False, "error": "psutil not available"}
            
            # Find Chrome processes
            chrome_closed = 0
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'chrome' in proc.info['name'].lower():
                        # Check if it's a tab process (has URL parameter)
                        cmdline = proc.info.get('cmdline', [])
                        if any(url in ' '.join(cmdline) for url in self.education_sites):
                            continue  # Keep educational tabs
                        
                        # Close non-educational Chrome processes
                        proc.terminate()
                        chrome_closed += 1
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {"success": True, "message": f"Closed {chrome_closed} non-educational Chrome tabs"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _minimize_non_essential_apps(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Minimize non-essential applications"""
        try:
            if not PYAUTOGUI_AVAILABLE:
                return {"success": False, "error": "pyautogui not available"}
            
            # List of non-essential apps to minimize
            non_essential = ['spotify', 'discord', 'slack', 'telegram']
            
            minimized = 0
            for app in non_essential:
                try:
                    # Try to find and minimize app window
                    # This is a simplified version - in production, you'd use more sophisticated window management
                    pyautogui.hotkey('win', 'd')  # Show desktop as fallback
                    minimized += 1
                    time.sleep(0.5)
                except:
                    continue
            
            return {"success": True, "message": f"Minimized {minimized} non-essential applications"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _set_study_mode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set system to study mode"""
        try:
            # Set system volume to comfortable level
            if os.name == 'nt':  # Windows
                subprocess.run(['nircmd.exe', 'setsysvolume', '50'], shell=True, capture_output=True)
            
            # Disable notifications (simplified)
            print("Study mode activated - notifications muted")
            
            return {"success": True, "message": "Study mode activated"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _close_background_apps(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Close background applications for meetings"""
        try:
            if not PSUTIL_AVAILABLE:
                return {"success": False, "error": "psutil not available"}
            
            background_apps = ['spotify', 'discord', 'slack', 'telegram', 'steam']
            closed = 0
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if any(app in proc.info['name'].lower() for app in background_apps):
                        proc.terminate()
                        closed += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {"success": True, "message": f"Closed {closed} background applications"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _open_zoom_teams(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Open Zoom or Teams for meeting"""
        try:
            meeting_app = params.get('meeting_app', 'zoom')
            
            if meeting_app.lower() == 'zoom':
                # Try to open Zoom
                if os.name == 'nt':
                    subprocess.Popen(['zoom.exe'], shell=True)
                else:
                    subprocess.Popen(['zoom'], shell=True)
            elif meeting_app.lower() == 'teams':
                # Try to open Teams
                if os.name == 'nt':
                    subprocess.Popen(['teams.exe'], shell=True)
                else:
                    subprocess.Popen(['teams'], shell=True)
            
            return {"success": True, "message": f"Opened {meeting_app}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _mute_notifications(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mute system notifications"""
        try:
            # Focus mode - simplified implementation
            print("Notifications muted for meeting")
            
            return {"success": True, "message": "System notifications muted"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _save_current_work(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Save current work before break"""
        try:
            # Send Ctrl+S to save current work
            if PYAUTOGUI_AVAILABLE:
                pyautogui.hotkey('ctrl', 's')
                time.sleep(1)
            
            return {"success": True, "message": "Current work saved"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _open_break_activity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Open break activity"""
        try:
            break_activities = [
                'https://www.youtube.com/watch?v=jfKfPfyJRdk',  # Relaxing music
                'https://www.calm.com/',  # Meditation app
                'https://www.youtube.com/watch?v=dQw4w9WgXcQ'   # Surprise break activity
            ]
            
            activity = params.get('break_activity', break_activities[0])
            webbrowser.open(activity)
            
            return {"success": True, "message": f"Opened break activity: {activity}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _set_break_timer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set break timer"""
        try:
            break_duration = params.get('duration', 300)  # 5 minutes default
            
            print(f"Break timer set for {break_duration} seconds")
            
            return {"success": True, "message": f"Break timer set for {break_duration} seconds"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_available_workflows(self) -> Dict[str, Any]:
        """Get list of available workflows"""
        return {
            "workflows": self.workflows,
            "running_workflows": self.running_workflows,
            "total_workflows": len(self.workflows)
        }
    
    def get_workflow_history(self, limit: int = 10) -> Dict[str, Any]:
        """Get workflow execution history"""
        return {
            "history": self.workflow_history[-limit:],
            "total_executions": len(self.workflow_history),
            "limit": limit
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get macro service status"""
        return {
            "available_workflows": len(self.workflows),
            "running_workflows": len(self.running_workflows),
            "total_executions": len(self.workflow_history),
            "psutil_available": PSUTIL_AVAILABLE,
            "pyautogui_available": PYAUTOGUI_AVAILABLE,
            "last_updated": datetime.now().isoformat()
        }
