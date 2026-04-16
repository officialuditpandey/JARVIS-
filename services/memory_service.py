#!/usr/bin/env python3
"""
JARVIS Neural Memory Service - Feature 50
ChromaDB integration for conversation memory and RAG
"""

import os
import sys
import json
import time
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import uuid

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    print("ChromaDB not available - Installing...")
    os.system("pip install chromadb")
    try:
        import chromadb
        from chromadb.config import Settings
        CHROMA_AVAILABLE = True
    except ImportError:
        CHROMA_AVAILABLE = False

try:
    import sentence_transformers
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    print("Sentence transformers not available - Installing...")
    os.system("pip install sentence-transformers")
    try:
        import sentence_transformers
        from sentence_transformers import SentenceTransformer
        SENTENCE_TRANSFORMERS_AVAILABLE = True
    except ImportError:
        SENTENCE_TRANSFORMERS_AVAILABLE = False
from typing import List, Dict, Optional, Any
import os
import sys

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class MemoryService:
    """SQLite-based memory service for persistent conversation storage"""
    
    def __init__(self, db_path: str = "jarvis_memory.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize SQLite database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create conversations table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        user_input TEXT NOT NULL,
                        jarvis_response TEXT NOT NULL,
                        source TEXT NOT NULL,
                        context_data TEXT
                    )
                ''')
                
                # Create memories table for facts
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS memories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        category TEXT NOT NULL,
                        key TEXT NOT NULL,
                        value TEXT NOT NULL,
                        importance INTEGER DEFAULT 1
                    )
                ''')
                
                # Create indexes for performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category)')
                
                conn.commit()
                print(f"Memory database initialized: {self.db_path}")
                
        except Exception as e:
            print(f"Memory database initialization error: {e}")
    
    def save_conversation(self, user_input: str, jarvis_response: str, source: str, context_data: Dict = None):
        """Save conversation turn to database"""
        try:
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Insert conversation record
                    cursor.execute('''
                        INSERT INTO conversations (timestamp, user_input, jarvis_response, source, context_data)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        datetime.now().isoformat(),
                        user_input,
                        jarvis_response,
                        source,
                        json.dumps(context_data) if context_data else None
                    ))
                    conn.commit()
                    
        except Exception as e:
            print(f"Error saving conversation: {e}")
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation history for context"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                    
                cursor.execute('''
                    SELECT user_input, jarvis_response, source, timestamp
                    FROM conversations
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                
                return [
                    {
                        'user_input': row[0],
                        'jarvis_response': row[1],
                        'source': row[2],
                        'timestamp': row[3]
                    }
                    for row in rows
                ]
                    
        except Exception as e:
            print(f"Error retrieving conversation history: {e}")
            return []
    
    def save_memory(self, category: str, key: str, value: str, importance: int = 1):
        """Save a memory/fact to database"""
        try:
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Insert memory record
                    cursor.execute('''
                        INSERT OR REPLACE INTO memories (timestamp, category, key, value, importance)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        datetime.now().isoformat(),
                        category,
                        key,
                        value,
                        importance
                    ))
                    
                    conn.commit()
                    
        except Exception as e:
            print(f"Error saving memory: {e}")
    
    def recall_memories(self, category: str = None, limit: int = 5) -> List[Dict]:
        """Recall memories from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                    
                if category:
                    cursor.execute('''
                            SELECT key, value, timestamp, importance
                            FROM memories
                            WHERE category = ?
                            ORDER BY importance DESC, timestamp DESC
                            LIMIT ?
                        ''', (category, limit))
                else:
                    cursor.execute('''
                            SELECT key, value, timestamp, importance
                            FROM memories
                            ORDER BY importance DESC, timestamp DESC
                            LIMIT ?
                        ''', (limit,))
                    
                rows = cursor.fetchall()
                
                return [
                    {
                        'key': row[0],
                        'value': row[1],
                        'timestamp': row[2],
                        'importance': row[3]
                    }
                    for row in rows
                ]
                    
        except Exception as e:
            print(f"Error recalling memories: {e}")
            return []
    
    def get_recent_context(self, limit: int = 5) -> str:
        """Get recent conversation context for AI brain"""
        history = self.get_conversation_history(limit)
        
        if not history:
            return ""
        
        # Format context for AI brain
        context_lines = []
        for i, conv in enumerate(history):
            context_lines.append(f"User: {conv['user_input']}")
            context_lines.append(f"JARVIS: {conv['jarvis_response']}")
            context_lines.append(f"Source: {conv['source']}")
            context_lines.append("")
        
        return "\n".join(context_lines)
    
    def cleanup_old_memories(self, days: int = 30):
        """Clean up old memories to prevent database bloat"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                    
                cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
                
                cursor.execute('''
                        DELETE FROM memories
                        WHERE timestamp < ?
                    ''', (cutoff_date,))
                    
                conn.commit()
                print(f"Cleaned up memories older than {days} days")
                    
        except Exception as e:
            print(f"Error cleaning up memories: {e}")
    
    def get_memory_stats(self) -> Dict:
        """Get memory database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                    
                # Get conversation count
                cursor.execute("SELECT COUNT(*) FROM conversations")
                conv_count = cursor.fetchone()[0]
                
                # Get memory count
                cursor.execute("SELECT COUNT(*) FROM memories")
                mem_count = cursor.fetchone()[0]
                
                return {
                    'conversations': conv_count,
                    'memories': mem_count,
                    'database_size': os.path.getsize(self.db_path)
                }
                    
        except Exception as e:
            print(f"Error getting memory stats: {e}")
            return {'conversations': 0, 'memories': 0, 'database_size': 0}
