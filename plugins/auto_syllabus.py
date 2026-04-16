#!/usr/bin/env python3
"""
Auto-Syllabus Tracker Plugin - JARVIS Plugin
Automatically tracks learning milestones and topic changes in conversations
"""

import os
import re
from datetime import datetime
from typing import List, Dict, Optional

class AutoSyllabusTracker:
    """Plugin to track syllabus progress and milestones"""
    
    def __init__(self, memory_service=None):
        self.memory_service = memory_service
        self.syllabus_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Syllabus_Progress.md")
        self.milestone_keywords = [
            "finished", "completed", "done", "mastered", "learned", "understand",
            "implemented", "built", "created", "developed", "achieved", "accomplished"
        ]
        self.topic_keywords = [
            "ui layout", "user interface", "frontend", "backend", "database", 
            "api", "authentication", "testing", "deployment", "design", "architecture",
            "algorithm", "function", "class", "module", "feature", "component"
        ]
        
    def detect_milestone(self, user_input: str, jarvis_response: str) -> Optional[Dict]:
        """Detect if conversation contains a milestone or topic change"""
        combined_text = f"{user_input.lower()} {jarvis_response.lower()}"
        
        # Check for milestone keywords
        has_milestone = any(keyword in combined_text for keyword in self.milestone_keywords)
        
        if not has_milestone:
            return None
            
        # Extract topic/topic name
        topic = self._extract_topic(user_input, jarvis_response)
        
        if topic:
            return {
                'timestamp': datetime.now(),
                'topic': topic,
                'status': 'Completed',
                'user_input': user_input,
                'jarvis_response': jarvis_response
            }
        
        return None
    
    def _extract_topic(self, user_input: str, jarvis_response: str) -> Optional[str]:
        """Extract topic name from conversation"""
        combined_text = f"{user_input} {jarvis_response}".lower()
        
        # Look for topic keywords and extract context
        for topic_keyword in self.topic_keywords:
            if topic_keyword in combined_text:
                # Try to extract a more specific topic
                patterns = [
                    rf'(?:finished|completed|done|mastered|implemented|built|created|developed)\s+(.+?{topic_keyword})',
                    rf'{topic_keyword}(.+?)(?:finished|completed|done|mastered)',
                    rf'(?:learning|working on|studying)\s+(.+?{topic_keyword})',
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, combined_text, re.IGNORECASE)
                    if match:
                        topic = match.group(1).strip()
                        # Clean up the topic name
                        topic = re.sub(r'[^\w\s-]', '', topic).strip()
                        topic = topic.title()
                        if len(topic) > 3:  # Filter out very short matches
                            return topic
                
                # Fallback to just the keyword
                return topic_keyword.title()
        
        # Try to extract from common patterns
        patterns = [
            r'(?:finished|completed|done|mastered|implemented|built|created|developed)\s+(.+?)(?:\.|$|\n)',
            r'(?:learning|working on|studying)\s+(.+?)(?:\.|$|\n)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, combined_text, re.IGNORECASE)
            if match:
                topic = match.group(1).strip()
                topic = re.sub(r'[^\w\s-]', '', topic).strip()
                topic = topic.title()
                if len(topic) > 3:
                    return topic
        
        return None
    
    def log_milestone(self, milestone: Dict):
        """Log milestone to syllabus progress file"""
        try:
            # Create file if it doesn't exist
            if not os.path.exists(self.syllabus_file):
                with open(self.syllabus_file, 'w', encoding='utf-8') as f:
                    f.write("# JARVIS Auto-Syllabus Progress Tracker\n\n")
                    f.write("This file automatically tracks learning milestones and topic completion.\n\n")
                    f.write("## Progress Log\n\n")
            
            # Format the entry
            timestamp_str = milestone['timestamp'].strftime("%Y-%m-%d %H:%M")
            entry = f"[{timestamp_str}] - Topic: {milestone['topic']} | Status: {milestone['status']}\n"
            
            # Append to file
            with open(self.syllabus_file, 'a', encoding='utf-8') as f:
                f.write(entry)
            
            print(f"✅ Milestone logged: {milestone['topic']} - {milestone['status']}")
            return True
            
        except Exception as e:
            print(f"❌ Error logging milestone: {e}")
            return False
    
    def process_conversation(self, user_input: str, jarvis_response: str):
        """Process conversation and log milestones if detected"""
        milestone = self.detect_milestone(user_input, jarvis_response)
        
        if milestone:
            self.log_milestone(milestone)
            
            # Also save to memory system if available
            if self.memory_service:
                self.memory_service.save_memory(
                    category="syllabus",
                    key=f"milestone_{milestone['timestamp'].strftime('%Y%m%d_%H%M%S')}",
                    value=f"Topic: {milestone['topic']} | Status: {milestone['status']}",
                    importance=2
                )
    
    def get_progress_summary(self) -> str:
        """Get summary of progress from syllabus file"""
        try:
            if not os.path.exists(self.syllabus_file):
                return "No progress tracked yet."
            
            with open(self.syllabus_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Count milestones
            milestone_lines = [line for line in content.split('\n') if '| Status:' in line]
            total_milestones = len(milestone_lines)
            
            if total_milestones == 0:
                return "No milestones tracked yet."
            
            # Get recent milestones
            recent_milestones = milestone_lines[-5:]  # Last 5 milestones
            
            summary = f"Total Milestones: {total_milestones}\n\nRecent Progress:\n"
            for milestone in recent_milestones:
                summary += f"  {milestone.strip()}\n"
            
            return summary
            
        except Exception as e:
            return f"Error reading progress: {e}"

# Global plugin instance
global_syllabus_tracker = None

# Plugin initialization function (required by PluginManager)
def initialize():
    """Initialize Auto-Syllabus Tracker plugin"""
    global global_syllabus_tracker
    
    try:
        # Import memory service from the services directory
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from services.memory_service import MemoryService
        
        # Initialize memory service
        memory_service = MemoryService()
        
        # Create plugin instance
        global_syllabus_tracker = AutoSyllabusTracker(memory_service)
        print("✅ Auto-Syllabus Tracker plugin initialized")
        return True
        
    except Exception as e:
        print(f"❌ Auto-Syllabus Tracker plugin initialization failed: {e}")
        return False

# Plugin info function (required by PluginManager)
def get_info():
    """Get plugin information"""
    return {
        'name': "Auto-Syllabus Tracker",
        'version': "1.0.0",
        'description': "Automatically tracks learning milestones and topic changes in conversations"
    }

# Plugin function to process conversations
def process_conversation(user_input: str, jarvis_response: str):
    """Process conversation and track milestones"""
    global global_syllabus_tracker
    
    if global_syllabus_tracker:
        global_syllabus_tracker.process_conversation(user_input, jarvis_response)

# Plugin function to get progress summary
def get_progress_summary():
    """Get progress summary from syllabus tracker"""
    global global_syllabus_tracker
    
    if global_syllabus_tracker:
        return global_syllabus_tracker.get_progress_summary()
    return "Auto-Syllabus Tracker not initialized"
