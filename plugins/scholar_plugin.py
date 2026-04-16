#!/usr/bin/env python3
"""
Scholar Plugin for JARVIS - Study Mode and Learning Features
"""

import sys
import os
from typing import Dict, Any

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from services.scholar_service import ScholarService
    SCHOLAR_AVAILABLE = True
except ImportError:
    SCHOLAR_AVAILABLE = False

class ScholarPlugin:
    """Scholar plugin for study mode and learning features"""
    
    def __init__(self):
        self.name = "scholar"
        self.version = "1.0.0"
        self.description = "Study mode and learning features"
        self.scholar_service = None
        
        self.command_patterns = [
            "start study mode",
            "stop study mode",
            "study mode",
            "focus time",
            "generate flashcards",
            "take note",
            "research topic",
            "study progress"
        ]
    
    def initialize(self) -> bool:
        """Initialize plugin"""
        try:
            if not SCHOLAR_AVAILABLE:
                return False
            
            self.scholar_service = ScholarService()
            return True
        except Exception as e:
            print(f"Scholar plugin initialization failed: {e}")
            return False
    
    def handles_command(self, query: str) -> bool:
        """Check if plugin handles command"""
        query_lower = query.lower()
        return any(pattern in query_lower for pattern in self.command_patterns)
    
    def process_command(self, query: str) -> Dict[str, Any]:
        """Process scholar command"""
        try:
            query_lower = query.lower()
            
            # Study mode commands
            if "start study mode" in query_lower or "focus time" in query_lower:
                duration = 60  # Default 60 minutes
                if "hour" in query_lower:
                    duration = int(query_lower.split("hour")[0].split()[-1]) * 60 if query_lower.split("hour")[0].split()[-1].isdigit() else 60
                
                if self.scholar_service.start_study_mode(duration):
                    return {
                        'success': True,
                        'response': f"Study mode started for {duration} minutes. Distractions blocked."
                    }
                else:
                    return {'success': False, 'error': 'Failed to start study mode'}
            
            elif "stop study mode" in query_lower:
                if self.scholar_service.stop_study_mode():
                    return {
                        'success': True,
                        'response': 'Study mode stopped. Distractions unblocked.'
                    }
                else:
                    return {'success': False, 'error': 'Study mode not active'}
            
            # Flashcard commands
            elif "generate flashcards" in query_lower:
                topic = "General"
                if "about" in query_lower:
                    topic = query_lower.split("about")[1].strip()
                
                flashcards = self.scholar_service.generate_flashcards(topic, f"Generated flashcards for {topic}")
                return {
                    'success': True,
                    'response': f"Generated {len(flashcards)} flashcards for {topic}."
                }
            
            # Note taking
            elif "take note" in query_lower:
                note = query.replace("take note", "").strip()
                if self.scholar_service.take_note(note):
                    return {
                        'success': True,
                        'response': "Note saved successfully."
                    }
                else:
                    return {'success': False, 'error': 'Failed to save note'}
            
            # Research
            elif "research topic" in query_lower:
                topic = query.replace("research topic", "").strip()
                results = self.scholar_service.research_topic(topic)
                if 'error' not in results:
                    return {
                        'success': True,
                        'response': f"Research completed for {topic}. Found {len(results.get('sources', []))} sources."
                    }
                else:
                    return {'success': False, 'error': 'Research failed'}
            
            # Status
            elif "study progress" in query_lower or "study status" in query_lower:
                stats = self.scholar_service.get_study_stats()
                return {
                    'success': True,
                    'response': f"Study mode: {'Active' if stats['study_mode_active'] else 'Inactive'}. "
                                f"Flashcards: {stats['total_flashcards']}. Notes: {stats['total_notes']}."
                }
            
            else:
                return {'success': False, 'error': 'Unknown scholar command'}
                
        except Exception as e:
            return {'success': False, 'error': f'Scholar command failed: {e}'}
