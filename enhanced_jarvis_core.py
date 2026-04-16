#!/usr/bin/env python3
"""
Enhanced JARVIS Core - Practical Upgrades for Laptop Use
Free improvements that make JARVIS a personal genius assistant
"""

import os
import sys
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import sqlite3
import glob

# Add JARVIS backend path
sys.path.insert(0, '.')

from intelligent_command_processor import process_command_intelligently
from jarvis_final import speak, identify_objects

class EnhancedJarvisCore:
    """Enhanced JARVIS with practical improvements for laptop users"""
    
    def __init__(self):
        self.is_active = False
        self.user_profile = {}
        self.personal_knowledge = {}
        self.interaction_patterns = {}
        self.proactive_suggestions = []
        self.file_index = {}
        
        # Personal data storage
        self.personal_db = "personal_jarvis_data.db"
        self.knowledge_base = "personal_knowledge.json"
        
        # Initialize enhanced features
        self._initialize_enhanced_features()
        
    def _initialize_enhanced_features(self):
        """Initialize all enhanced features"""
        print("Initializing Enhanced JARVIS Core...")
        
        # Initialize personal database
        self._init_personal_database()
        
        # Load existing user profile
        self._load_user_profile()
        
        # Index personal files
        self._index_user_files()
        
        # Start pattern monitoring
        self._start_pattern_monitoring()
        
        # Start proactive suggestions
        self._start_proactive_engine()
        
        print("Enhanced JARVIS Core initialized")
    
    def _init_personal_database(self):
        """Initialize personal database for user data"""
        try:
            with sqlite3.connect(self.personal_db) as conn:
                cursor = conn.cursor()
                
                # User profile table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_profile (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        updated_at TIMESTAMP
                    )
                ''')
                
                # Interaction patterns table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS interaction_patterns (
                        id INTEGER PRIMARY KEY,
                        pattern_type TEXT,
                        pattern_data TEXT,
                        frequency INTEGER,
                        last_seen TIMESTAMP
                    )
                ''')
                
                # Personal knowledge table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS personal_knowledge (
                        id INTEGER PRIMARY KEY,
                        category TEXT,
                        title TEXT,
                        content TEXT,
                        source TEXT,
                        importance INTEGER,
                        created_at TIMESTAMP
                    )
                ''')
                
                # File index table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS file_index (
                        path TEXT PRIMARY KEY,
                        name TEXT,
                        type TEXT,
                        size INTEGER,
                        modified TIMESTAMP,
                        tags TEXT,
                        content_summary TEXT
                    )
                ''')
                
                conn.commit()
                print("Personal database initialized")
                
        except Exception as e:
            print(f"Database initialization error: {e}")
    
    def _load_user_profile(self):
        """Load existing user profile"""
        try:
            with sqlite3.connect(self.personal_db) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM user_profile")
                for row in cursor.fetchall():
                    self.user_profile[row[0]] = row[1]
            
            # Set defaults if no profile exists
            if not self.user_profile:
                self.user_profile = {
                    "name": "User",
                    "preferred_style": "friendly",
                    "work_hours": "9-5",
                    "interests": [],
                    "frequent_tasks": [],
                    "communication_preference": "balanced"
                }
                self._save_user_profile()
            
            print(f"User profile loaded: {len(self.user_profile)} preferences")
            
        except Exception as e:
            print(f"Profile loading error: {e}")
            self.user_profile = {}
    
    def _save_user_profile(self):
        """Save user profile to database"""
        try:
            with sqlite3.connect(self.personal_db) as conn:
                cursor = conn.cursor()
                for key, value in self.user_profile.items():
                    cursor.execute('''
                        INSERT OR REPLACE INTO user_profile (key, value, updated_at)
                        VALUES (?, ?, ?)
                    ''', (key, value, datetime.now()))
                conn.commit()
        except Exception as e:
            print(f"Profile saving error: {e}")
    
    def _index_user_files(self):
        """Index user's personal files for knowledge base"""
        try:
            # Common user directories to index
            user_dirs = [
                os.path.expanduser("~/Documents"),
                os.path.expanduser("~/Desktop"),
                os.path.expanduser("~/Downloads"),
                os.path.join(os.getcwd(), "cloud_cowork"),
                os.getcwd()  # Current JARVIS directory
            ]
            
            indexed_count = 0
            with sqlite3.connect(self.personal_db) as conn:
                cursor = conn.cursor()
                
                for directory in user_dirs:
                    if os.path.exists(directory):
                        # Index different file types
                        for pattern in ["*.txt", "*.md", "*.py", "*.json", "*.pdf"]:
                            for file_path in glob.glob(os.path.join(directory, "**", pattern), recursive=True):
                                try:
                                    # Get file info
                                    stat = os.stat(file_path)
                                    file_name = os.path.basename(file_path)
                                    file_ext = os.path.splitext(file_name)[1].lower()
                                    
                                    # Extract content summary for text files
                                    content_summary = ""
                                    if file_ext in ['.txt', '.md', '.py', '.json']:
                                        try:
                                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                                content = f.read(1000)  # First 1000 chars
                                                content_summary = content[:200]
                                        except:
                                            content_summary = "Binary or unreadable file"
                                    
                                    # Store in database
                                    cursor.execute('''
                                        INSERT OR REPLACE INTO file_index 
                                        (path, name, type, size, modified, tags, content_summary)
                                        VALUES (?, ?, ?, ?, ?, ?, ?)
                                    ''', (
                                        file_path,
                                        file_name,
                                        file_ext,
                                        stat.st_size,
                                        datetime.fromtimestamp(stat.st_mtime),
                                        self._generate_file_tags(file_path, file_ext),
                                        content_summary
                                    ))
                                    
                                    indexed_count += 1
                                    
                                except Exception as e:
                                    print(f"Error indexing {file_path}: {e}")
                                    continue
                
                conn.commit()
            
            self.file_index = self._load_file_index()
            print(f"Indexed {indexed_count} personal files")
            
        except Exception as e:
            print(f"File indexing error: {e}")
    
    def _generate_file_tags(self, file_path: str, file_ext: str) -> str:
        """Generate tags for file based on path and type"""
        tags = []
        
        # File type tags
        type_tags = {
            '.py': 'code,python,programming',
            '.txt': 'text,document',
            '.md': 'markdown,documentation',
            '.json': 'data,json,config',
            '.pdf': 'document,pdf'
        }
        
        if file_ext in type_tags:
            tags.extend(type_tags[file_ext].split(','))
        
        # Path-based tags
        path_lower = file_path.lower()
        if 'jarvis' in path_lower:
            tags.append('jarvis')
        if 'test' in path_lower:
            tags.append('test')
        if 'service' in path_lower:
            tags.append('service')
        if 'config' in path_lower:
            tags.append('config')
        
        return ','.join(tags) if tags else 'general'
    
    def _load_file_index(self) -> Dict[str, Any]:
        """Load file index from database"""
        try:
            with sqlite3.connect(self.personal_db) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT path, name, type, tags, content_summary FROM file_index")
                
                file_index = {}
                for row in cursor.fetchall():
                    file_index[row[0]] = {
                        'name': row[1],
                        'type': row[2],
                        'tags': row[3],
                        'summary': row[4]
                    }
                
                return file_index
        except Exception as e:
            print(f"File index loading error: {e}")
            return {}
    
    def _start_pattern_monitoring(self):
        """Start monitoring user interaction patterns"""
        def monitor_patterns():
            while self.is_active:
                try:
                    # Analyze recent interactions
                    self._analyze_interaction_patterns()
                    time.sleep(60)  # Analyze every minute
                except Exception as e:
                    print(f"Pattern monitoring error: {e}")
                    time.sleep(10)
        
        self.pattern_thread = threading.Thread(target=monitor_patterns, daemon=True)
        self.pattern_thread.start()
    
    def _analyze_interaction_patterns(self):
        """Analyze user interaction patterns"""
        try:
            with sqlite3.connect(self.personal_db) as conn:
                cursor = conn.cursor()
                
                # Get recent interactions (this would integrate with JARVIS conversation history)
                # For now, simulate pattern detection
                
                # Time-based patterns
                current_hour = datetime.now().hour
                if 9 <= current_hour <= 17:
                    self.interaction_patterns['work_hours'] = self.interaction_patterns.get('work_hours', 0) + 1
                else:
                    self.interaction_patterns['personal_time'] = self.interaction_patterns.get('personal_time', 0) + 1
                
                # Update user profile based on patterns
                if self.interaction_patterns.get('work_hours', 0) > self.interaction_patterns.get('personal_time', 0):
                    self.user_profile['primary_usage'] = 'work'
                else:
                    self.user_profile['primary_usage'] = 'personal'
                
                self._save_user_profile()
                
        except Exception as e:
            print(f"Pattern analysis error: {e}")
    
    def _start_proactive_engine(self):
        """Start proactive suggestion engine"""
        def generate_suggestions():
            while self.is_active:
                try:
                    suggestions = self._generate_proactive_suggestions()
                    if suggestions:
                        self.proactive_suggestions = suggestions
                    time.sleep(300)  # Generate suggestions every 5 minutes
                except Exception as e:
                    print(f"Proactive engine error: {e}")
                    time.sleep(30)
        
        self.proactive_thread = threading.Thread(target=generate_suggestions, daemon=True)
        self.proactive_thread.start()
    
    def _generate_proactive_suggestions(self) -> List[str]:
        """Generate proactive suggestions based on user patterns"""
        suggestions = []
        
        try:
            current_hour = datetime.now().hour
            current_day = datetime.now().weekday()
            
            # Time-based suggestions
            if 8 <= current_hour <= 9:
                suggestions.append("Good morning! Ready to start your day? I can help organize your tasks.")
            
            elif 12 <= current_hour <= 13:
                suggestions.append("Lunch time! Would you like me to find something healthy to eat?")
            
            elif 17 <= current_hour <= 18:
                suggestions.append("End of work day! Let me help you wrap up and plan tomorrow.")
            
            # Day-based suggestions
            if current_day == 0:  # Monday
                suggestions.append("Monday! Let me help you plan your week for maximum productivity.")
            
            elif current_day == 4:  # Friday
                suggestions.append("Friday! Time to review your accomplishments and plan weekend activities.")
            
            # Usage pattern suggestions
            if self.user_profile.get('primary_usage') == 'work':
                suggestions.append("I notice you use JARVIS mainly for work. Want me to optimize your workflow?")
            
            # File-based suggestions
            recent_files = self._get_recent_files()
            if recent_files:
                suggestions.append(f"You recently worked on {recent_files[0]['name']}. Want to continue?")
            
        except Exception as e:
            print(f"Suggestion generation error: {e}")
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def _get_recent_files(self, limit: int = 3) -> List[Dict]:
        """Get recently modified files"""
        try:
            with sqlite3.connect(self.personal_db) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT name, type, modified FROM file_index 
                    ORDER BY modified DESC 
                    LIMIT ?
                ''', (limit,))
                
                return [{'name': row[0], 'type': row[1], 'modified': row[2]} for row in cursor.fetchall()]
        except:
            return []
    
    def enhanced_command_processing(self, user_input: str) -> Dict[str, Any]:
        """Process command with enhanced intelligence"""
        result = {
            'user_input': user_input,
            'understanding': {},
            'response': '',
            'actions': [],
            'suggestions': []
        }
        
        try:
            # Use intelligent command processor
            command_result = process_command_intelligently(user_input)
            result['understanding'] = command_result
            
            # Add personal context
            if command_result['category'] == 'vision':
                result['response'] = self._enhanced_vision_processing(user_input)
            elif command_result['category'] == 'general':
                result['response'] = self._enhanced_general_processing(user_input)
            else:
                result['response'] = f"I understand you want to {command_result['category']} related help."
            
            # Add proactive suggestions
            if self.proactive_suggestions:
                result['suggestions'] = self.proactive_suggestions
            
            # Record interaction for pattern learning
            self._record_interaction(user_input, command_result)
            
        except Exception as e:
            result['response'] = f"I had trouble processing that: {str(e)}"
        
        return result
    
    def _enhanced_vision_processing(self, user_input: str) -> str:
        """Enhanced vision processing with better prompts"""
        try:
            # Use existing vision but with enhanced analysis
            vision_result = identify_objects()
            
            # Add personal context to vision analysis
            if self.user_profile.get('name'):
                vision_result += f"\n\nPersonal note: This analysis was requested by {self.user_profile['name']}."
            
            return vision_result
            
        except Exception as e:
            return f"Vision processing error: {e}"
    
    def _enhanced_general_processing(self, user_input: str) -> str:
        """Enhanced general processing with personal knowledge"""
        try:
            # Search personal knowledge base
            knowledge_results = self._search_personal_knowledge(user_input)
            
            if knowledge_results:
                response = "Based on your personal information:\n"
                for result in knowledge_results[:3]:
                    response += f"- {result['title']}: {result['content'][:100]}...\n"
                return response
            else:
                # Use existing JARVIS response
                return "I understand you're looking for help. Let me assist you with that."
                
        except Exception as e:
            return f"General processing error: {e}"
    
    def _search_personal_knowledge(self, query: str) -> List[Dict]:
        """Search personal knowledge base"""
        try:
            with sqlite3.connect(self.personal_db) as conn:
                cursor = conn.cursor()
                
                # Simple text search (can be enhanced with better search)
                cursor.execute('''
                    SELECT title, content, category FROM personal_knowledge 
                    WHERE content LIKE ? OR title LIKE ?
                    ORDER BY importance DESC
                    LIMIT 5
                ''', (f'%{query}%', f'%{query}%'))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'title': row[0],
                        'content': row[1],
                        'category': row[2]
                    })
                
                return results
                
        except:
            return []
    
    def _record_interaction(self, user_input: str, command_result: Dict):
        """Record interaction for pattern learning"""
        try:
            with sqlite3.connect(self.personal_db) as conn:
                cursor = conn.cursor()
                
                # Record pattern
                pattern_data = json.dumps({
                    'input': user_input,
                    'category': command_result['category'],
                    'confidence': command_result['confidence']
                })
                
                cursor.execute('''
                    INSERT INTO interaction_patterns 
                    (pattern_type, pattern_data, frequency, last_seen)
                    VALUES (?, ?, 1, ?)
                ''', (command_result['category'], pattern_data, datetime.now()))
                
                conn.commit()
                
        except Exception as e:
            print(f"Interaction recording error: {e}")
    
    def add_personal_knowledge(self, category: str, title: str, content: str, source: str = "user"):
        """Add knowledge to personal knowledge base"""
        try:
            with sqlite3.connect(self.personal_db) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO personal_knowledge 
                    (category, title, content, source, importance, created_at)
                    VALUES (?, ?, ?, ?, 5, ?)
                ''', (category, title, content, source, datetime.now()))
                
                conn.commit()
                print(f"Added to personal knowledge: {title}")
                
        except Exception as e:
            print(f"Knowledge addition error: {e}")
    
    def search_files(self, query: str) -> List[Dict]:
        """Search indexed files"""
        results = []
        
        try:
            query_lower = query.lower()
            
            for file_path, file_info in self.file_index.items():
                # Search in name, tags, and summary
                if (query_lower in file_info['name'].lower() or 
                    query_lower in file_info['tags'].lower() or
                    query_lower in file_info['summary'].lower()):
                    
                    results.append({
                        'path': file_path,
                        'name': file_info['name'],
                        'type': file_info['type'],
                        'tags': file_info['tags'],
                        'summary': file_info['summary']
                    })
            
            return results[:10]  # Limit to 10 results
            
        except Exception as e:
            print(f"File search error: {e}")
            return []
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report"""
        return {
            'is_active': self.is_active,
            'user_profile': self.user_profile,
            'interaction_patterns': self.interaction_patterns,
            'file_index_size': len(self.file_index),
            'proactive_suggestions': self.proactive_suggestions,
            'personal_knowledge_count': len(self._search_personal_knowledge("")),
            'enhanced_features': [
                'Intelligent command processing',
                'Personal knowledge base',
                'File indexing and search',
                'Pattern learning',
                'Proactive suggestions',
                'Enhanced vision analysis'
            ]
        }
    
    def activate(self):
        """Activate enhanced JARVIS core"""
        self.is_active = True
        print("Enhanced JARVIS Core activated")
        print(f"Personal files indexed: {len(self.file_index)}")
        print(f"User preferences loaded: {len(self.user_profile)}")
        print("Enhanced features ready!")
    
    def deactivate(self):
        """Deactivate enhanced JARVIS core"""
        self.is_active = False
        print("Enhanced JARVIS Core deactivated")

# Global instance
enhanced_jarvis = EnhancedJarvisCore()
