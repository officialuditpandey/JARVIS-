#!/usr/bin/env python3
"""
Notes Service for JARVIS - Phase 3 Voice-to-JSON
Daily notes logging with timestamp, category, and priority
"""

import os
import json
import re
from datetime import datetime, date
from typing import Dict, Any, List, Optional
import sys

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class NotesService:
    """Voice-to-JSON notes service for daily logging"""
    
    def __init__(self):
        self.notes_dir = "logs"
        self.daily_notes_file = os.path.join(self.notes_dir, "daily_notes.json")
        
        # Ensure logs directory exists
        os.makedirs(self.notes_dir, exist_ok=True)
        
        # Initialize daily notes file
        self._initialize_notes_file()
        
        # Priority levels
        self.priority_levels = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
        
        # Categories
        self.categories = [
            'personal', 'work', 'study', 'ideas', 'tasks', 
            'meetings', 'reminders', 'health', 'finance', 'other'
        ]
        
        print("Voice-to-JSON Notes Service initialized")
    
    def _initialize_notes_file(self):
        """Initialize the daily notes JSON file"""
        try:
            if not os.path.exists(self.daily_notes_file):
                with open(self.daily_notes_file, 'w', encoding='utf-8') as f:
                    json.dump({"notes": [], "metadata": {"created": datetime.now().isoformat()}}, f, indent=2)
        except Exception as e:
            print(f"Failed to initialize notes file: {e}")
    
    def add_note(self, content: str, category: str = "other", priority: str = "medium", tags: List[str] = None) -> Dict[str, Any]:
        """Add a new note via voice command"""
        try:
            # Validate inputs
            if not content or not content.strip():
                return {"success": False, "error": "Note content cannot be empty"}
            
            category = category.lower() if category.lower() in self.categories else "other"
            priority = priority.lower() if priority.lower() in self.priority_levels else "medium"
            tags = tags or []
            
            # Create note object
            note = {
                "id": self._generate_note_id(),
                "content": content.strip(),
                "category": category,
                "priority": priority,
                "priority_level": self.priority_levels[priority],
                "tags": tags,
                "timestamp": datetime.now().isoformat(),
                "date": date.today().isoformat(),
                "word_count": len(content.split()),
                "created_by": "voice_command"
            }
            
            # Load existing notes
            notes_data = self._load_notes()
            
            # Add new note
            notes_data["notes"].append(note)
            notes_data["metadata"]["last_updated"] = datetime.now().isoformat()
            notes_data["metadata"]["total_notes"] = len(notes_data["notes"])
            
            # Save notes
            self._save_notes(notes_data)
            
            print(f"Note added: {category} - {priority} priority")
            
            return {
                "success": True,
                "note": note,
                "message": f"Note saved successfully in {category} category"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_note_id(self) -> str:
        """Generate unique note ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        import random
        random_suffix = random.randint(1000, 9999)
        return f"note_{timestamp}_{random_suffix}"
    
    def _load_notes(self) -> Dict[str, Any]:
        """Load notes from JSON file"""
        try:
            if os.path.exists(self.daily_notes_file):
                with open(self.daily_notes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {"notes": [], "metadata": {"created": datetime.now().isoformat()}}
        except Exception as e:
            print(f"Failed to load notes: {e}")
            return {"notes": [], "metadata": {"created": datetime.now().isoformat()}}
    
    def _save_notes(self, notes_data: Dict[str, Any]):
        """Save notes to JSON file"""
        try:
            with open(self.daily_notes_file, 'w', encoding='utf-8') as f:
                json.dump(notes_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save notes: {e}")
    
    def parse_voice_command(self, command: str) -> Dict[str, Any]:
        """Parse voice command for note creation"""
        try:
            # Pattern: "Jarvis, log this note: [content]"
            note_pattern = r'(?i)jarvis.*log this note[:]\s*(.+)$'
            match = re.match(note_pattern, command.strip())
            
            if not match:
                return {"success": False, "error": "Invalid voice command format"}
            
            content = match.group(1).strip()
            
            # Extract category from content if specified
            category = self._extract_category(content)
            priority = self._extract_priority(content)
            tags = self._extract_tags(content)
            
            # Clean content by removing category/priority keywords
            clean_content = self._clean_content(content, category, priority)
            
            return {
                "success": True,
                "content": clean_content,
                "category": category,
                "priority": priority,
                "tags": tags
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _extract_category(self, content: str) -> str:
        """Extract category from content"""
        content_lower = content.lower()
        
        # Check work category first (most specific)
        work_keywords = ['work', 'office', 'job', 'project', 'meeting', 'bug', 'code', 'error', 'python']
        if any(keyword in content_lower for keyword in work_keywords):
            return "work"
        
        # Check study category
        study_keywords = ['study', 'learn', 'exam', 'course', 'homework', 'math', 'syllabus', 'revision']
        if any(keyword in content_lower for keyword in study_keywords):
            return "study"
        
        # Check personal category
        personal_keywords = ['personal', 'private', 'my', 'me', 'buy', 'grocery', 'reminder']
        if any(keyword in content_lower for keyword in personal_keywords):
            return "personal"
        
        # Check other categories
        if any(keyword in content_lower for keyword in ['idea', 'think', 'innovate', 'create']):
            return "ideas"
        if any(keyword in content_lower for keyword in ['task', 'todo', 'do', 'complete']):
            return "tasks"
        if any(keyword in content_lower for keyword in ['meeting', 'call', 'conference']):
            return "meetings"
        if any(keyword in content_lower for keyword in ['remind', 'remember', 'don\'t forget']):
            return "reminders"
        if any(keyword in content_lower for keyword in ['health', 'doctor', 'medicine', 'exercise']):
            return "health"
        if any(keyword in content_lower for keyword in ['money', 'pay', 'bill', 'budget', 'finance']):
            return "finance"
        
        return "other"
    
    def _extract_priority(self, content: str) -> str:
        """Extract priority from content"""
        content_lower = content.lower()
        
        # Check for critical first (highest priority)
        critical_keywords = ['urgent', 'critical', 'emergency', 'asap', 'immediate', 'fix']
        if any(keyword in content_lower for keyword in critical_keywords):
            return "critical"
        
        # Check for high priority
        high_keywords = ['important', 'high', 'priority', 'soon', 'exam', 'revision', 'math', 'python', 'error']
        if any(keyword in content_lower for keyword in high_keywords):
            return "high"
        
        # Check for low priority
        low_keywords = ['low', 'later', 'sometime', 'when possible', 'groceries']
        if any(keyword in content_lower for keyword in low_keywords):
            return "low"
        
        # Default to medium
        return "medium"
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract tags from content (hashtags)"""
        tag_pattern = r'#(\w+)'
        tags = re.findall(tag_pattern, content)
        return [tag.lower() for tag in tags]
    
    def _clean_content(self, content: str, category: str, priority: str) -> str:
        """Clean content by removing category/priority keywords"""
        # Remove priority keywords
        priority_keywords = ['urgent', 'critical', 'emergency', 'asap', 'important', 'high', 'priority', 'soon', 'medium', 'normal', 'regular', 'low', 'later', 'sometime', 'when possible']
        
        # Remove category keywords
        category_keywords = ['personal', 'private', 'work', 'office', 'job', 'study', 'learn', 'idea', 'task', 'meeting', 'remind', 'health', 'finance']
        
        # Clean content
        clean_content = content
        for keyword in priority_keywords + category_keywords:
            clean_content = re.sub(rf'\b{keyword}\b', '', clean_content, flags=re.IGNORECASE)
        
        # Remove extra spaces and punctuation
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        clean_content = clean_content.rstrip(':,.!?')
        
        return clean_content
    
    def voice_log_note(self, command: str) -> Dict[str, Any]:
        """Process voice command and log note"""
        try:
            # Parse voice command
            parsed = self.parse_voice_command(command)
            if not parsed["success"]:
                return parsed
            
            # Add note
            result = self.add_note(
                content=parsed["content"],
                category=parsed["category"],
                priority=parsed["priority"],
                tags=parsed["tags"]
            )
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_notes(self, category: str = None, priority: str = None, date_filter: str = None, limit: int = 50) -> Dict[str, Any]:
        """Get notes with optional filtering"""
        try:
            notes_data = self._load_notes()
            notes = notes_data.get("notes", [])
            
            # Apply filters
            if category:
                notes = [note for note in notes if note["category"] == category.lower()]
            
            if priority:
                notes = [note for note in notes if note["priority"] == priority.lower()]
            
            if date_filter:
                notes = [note for note in notes if note["date"] == date_filter]
            
            # Sort by timestamp (newest first) and limit
            notes.sort(key=lambda x: x["timestamp"], reverse=True)
            notes = notes[:limit]
            
            return {
                "success": True,
                "notes": notes,
                "total_found": len(notes),
                "filters": {
                    "category": category,
                    "priority": priority,
                    "date_filter": date_filter,
                    "limit": limit
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_notes(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """Search notes by content"""
        try:
            notes_data = self._load_notes()
            notes = notes_data.get("notes", [])
            
            query_lower = query.lower()
            matching_notes = []
            
            for note in notes:
                # Search in content, tags, and category
                if (query_lower in note["content"].lower() or 
                    query_lower in note["category"] or
                    any(query_lower in tag.lower() for tag in note["tags"])):
                    matching_notes.append(note)
            
            # Sort by relevance (exact matches first) and timestamp
            matching_notes.sort(key=lambda x: (
                0 if query_lower in x["content"].lower() else 1,
                x["timestamp"]
            ), reverse=True)
            
            matching_notes = matching_notes[:limit]
            
            return {
                "success": True,
                "notes": matching_notes,
                "total_found": len(matching_notes),
                "query": query
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_note(self, note_id: str) -> Dict[str, Any]:
        """Delete a note by ID"""
        try:
            notes_data = self._load_notes()
            notes = notes_data.get("notes", [])
            
            # Find and remove note
            original_count = len(notes)
            notes = [note for note in notes if note["id"] != note_id]
            
            if len(notes) == original_count:
                return {"success": False, "error": f"Note with ID {note_id} not found"}
            
            # Save updated notes
            notes_data["notes"] = notes
            notes_data["metadata"]["last_updated"] = datetime.now().isoformat()
            notes_data["metadata"]["total_notes"] = len(notes)
            
            self._save_notes(notes_data)
            
            return {
                "success": True,
                "message": f"Note {note_id} deleted successfully"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get notes statistics"""
        try:
            notes_data = self._load_notes()
            notes = notes_data.get("notes", [])
            
            # Calculate statistics
            total_notes = len(notes)
            category_counts = {}
            priority_counts = {}
            notes_by_date = {}
            
            for note in notes:
                # Category counts
                category = note["category"]
                category_counts[category] = category_counts.get(category, 0) + 1
                
                # Priority counts
                priority = note["priority"]
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
                
                # Date counts
                note_date = note["date"]
                notes_by_date[note_date] = notes_by_date.get(note_date, 0) + 1
            
            # Most recent note
            most_recent = max(notes, key=lambda x: x["timestamp"]) if notes else None
            
            return {
                "success": True,
                "statistics": {
                    "total_notes": total_notes,
                    "category_distribution": category_counts,
                    "priority_distribution": priority_counts,
                    "notes_by_date": notes_by_date,
                    "most_recent_note": most_recent,
                    "average_note_length": sum(note["word_count"] for note in notes) / total_notes if total_notes > 0 else 0
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get notes service status"""
        try:
            notes_data = self._load_notes()
            total_notes = len(notes_data.get("notes", []))
            
            return {
                "notes_file": self.daily_notes_file,
                "total_notes": total_notes,
                "available_categories": self.categories,
                "priority_levels": list(self.priority_levels.keys()),
                "last_updated": notes_data.get("metadata", {}).get("last_updated"),
                "service_active": True
            }
            
        except Exception as e:
            return {"service_active": False, "error": str(e)}
