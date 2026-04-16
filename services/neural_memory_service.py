#!/usr/bin/env python3
"""
Neural Memory Service for JARVIS - Feature 50
ChromaDB integration for conversation memory and RAG
"""

import os
import sys
import json
import time
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

class NeuralMemoryService:
    """Neural Memory service with ChromaDB for RAG"""
    
    def __init__(self):
        self.memory_dir = "neural_memory"
        self.collection_name = "jarvis_conversations"
        self.client = None
        self.collection = None
        self.embedding_model = None
        self.is_initialized = False
        
        # Memory configuration
        self.max_memory_age_days = 30  # Keep memories for 30 days
        self.similarity_threshold = 0.7  # Minimum similarity for retrieval
        self.max_retrieval_count = 5  # Max memories to retrieve
        
        # Initialize service
        self._initialize_memory()
        
        print("Neural Memory Service initialized with ChromaDB RAG")
    
    def _initialize_memory(self):
        """Initialize ChromaDB and embedding model"""
        try:
            if not CHROMA_AVAILABLE:
                print("ChromaDB not available - using fallback memory")
                return
            
            # Create memory directory
            os.makedirs(self.memory_dir, exist_ok=True)
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=self.memory_dir,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=False
                )
            )
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(name=self.collection_name)
                print(f"Loaded existing collection: {self.collection_name}")
            except:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "JARVIS conversation memory"}
                )
                print(f"Created new collection: {self.collection_name}")
            
            # Initialize embedding model
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("Embedding model loaded: all-MiniLM-L6-v2")
            else:
                print("Using fallback embedding method")
            
            self.is_initialized = True
            
        except Exception as e:
            print(f"Memory initialization failed: {e}")
            self.is_initialized = False
    
    def add_memory(self, user_input: str, jarvis_response: str, context: Dict[str, Any] = None) -> str:
        """Add a new memory to ChromaDB"""
        try:
            if not self.is_initialized:
                return self._add_fallback_memory(user_input, jarvis_response, context)
            
            # Create memory entry
            memory_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            # Combine user input and response for embedding
            combined_text = f"User: {user_input}\nJARVIS: {jarvis_response}"
            
            # Generate embedding
            if self.embedding_model:
                embedding = self.embedding_model.encode(combined_text).tolist()
            else:
                embedding = self._fallback_embedding(combined_text)
            
            # Prepare metadata
            metadata = {
                "user_input": user_input,
                "jarvis_response": jarvis_response,
                "timestamp": timestamp,
                "context": context or {},
                "memory_type": "conversation"
            }
            
            # Add to ChromaDB
            self.collection.add(
                ids=[memory_id],
                embeddings=[embedding],
                documents=[combined_text],
                metadatas=[metadata]
            )
            
            print(f"Memory added: {memory_id[:8]}...")
            return memory_id
            
        except Exception as e:
            print(f"Failed to add memory: {e}")
            return None
    
    def search_memory(self, query: str, limit: int = None) -> List[Dict[str, Any]]:
        """Search memory for relevant past interactions"""
        try:
            if not self.is_initialized:
                return self._search_fallback_memory(query, limit)
            
            # Generate query embedding
            if self.embedding_model:
                query_embedding = self.embedding_model.encode(query).tolist()
            else:
                query_embedding = self._fallback_embedding(query)
            
            # Search ChromaDB
            search_limit = limit or self.max_retrieval_count
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=search_limit,
                where={"memory_type": "conversation"}
            )
            
            # Process results
            memories = []
            if results['ids'] and results['ids'][0]:
                for i, memory_id in enumerate(results['ids'][0]):
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i]
                    
                    # Convert distance to similarity
                    similarity = 1 - distance
                    
                    if similarity >= self.similarity_threshold:
                        memories.append({
                            "id": memory_id,
                            "user_input": metadata["user_input"],
                            "jarvis_response": metadata["jarvis_response"],
                            "timestamp": metadata["timestamp"],
                            "context": metadata.get("context", {}),
                            "similarity": similarity,
                            "distance": distance
                        })
            
            # Sort by similarity
            memories.sort(key=lambda x: x["similarity"], reverse=True)
            
            print(f"Memory search: {len(memories)} relevant memories found")
            return memories
            
        except Exception as e:
            print(f"Memory search failed: {e}")
            return []
    
    def get_context_for_query(self, query: str) -> str:
        """Get relevant context for a new query"""
        try:
            memories = self.search_memory(query, limit=3)
            
            if not memories:
                return ""
            
            # Format context
            context_parts = []
            for memory in memories:
                timestamp = memory["timestamp"]
                user_input = memory["user_input"]
                jarvis_response = memory["jarvis_response"]
                similarity = memory["similarity"]
                
                context_parts.append(
                    f"[Similarity: {similarity:.2f}] {timestamp}\n"
                    f"User: {user_input}\n"
                    f"JARVIS: {jarvis_response}\n"
                )
            
            return "\n---\n".join(context_parts)
            
        except Exception as e:
            print(f"Context generation failed: {e}")
            return ""
    
    def cleanup_old_memories(self):
        """Clean up old memories based on age"""
        try:
            if not self.is_initialized:
                return
            
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=self.max_memory_age_days)
            cutoff_timestamp = cutoff_date.isoformat()
            
            # Get all memories
            all_results = self.collection.get()
            
            if not all_results['ids']:
                return
            
            # Find old memories
            old_memory_ids = []
            for i, metadata in enumerate(all_results['metadatas']):
                if metadata and 'timestamp' in metadata:
                    memory_timestamp = metadata['timestamp']
                    if memory_timestamp < cutoff_timestamp:
                        old_memory_ids.append(all_results['ids'][i])
            
            # Delete old memories
            if old_memory_ids:
                self.collection.delete(ids=old_memory_ids)
                print(f"Cleaned up {len(old_memory_ids)} old memories")
            
        except Exception as e:
            print(f"Memory cleanup failed: {e}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        try:
            if not self.is_initialized:
                return {"status": "not_initialized"}
            
            # Get collection info
            collection_count = self.collection.count()
            
            return {
                "status": "active",
                "total_memories": collection_count,
                "max_age_days": self.max_memory_age_days,
                "similarity_threshold": self.similarity_threshold,
                "max_retrieval_count": self.max_retrieval_count,
                "chroma_available": CHROMA_AVAILABLE,
                "embedding_model_available": SENTENCE_TRANSFORMERS_AVAILABLE,
                "last_cleanup": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _fallback_embedding(self, text: str) -> List[float]:
        """Fallback embedding method using simple hashing"""
        import hashlib
        
        # Create a simple hash-based embedding
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Convert to numeric vector
        embedding = []
        for i in range(0, len(hash_hex), 2):
            if i + 1 < len(hash_hex):
                byte_val = int(hash_hex[i:i+2], 16)
                embedding.append(byte_val / 255.0)
        
        # Pad or truncate to 384 dimensions (standard for sentence transformers)
        while len(embedding) < 384:
            embedding.append(0.0)
        
        return embedding[:384]
    
    def _add_fallback_memory(self, user_input: str, jarvis_response: str, context: Dict[str, Any]) -> str:
        """Fallback memory storage using JSON"""
        try:
            memory_file = os.path.join(self.memory_dir, "fallback_memory.json")
            
            # Load existing memories
            if os.path.exists(memory_file):
                with open(memory_file, 'r', encoding='utf-8') as f:
                    memories = json.load(f)
            else:
                memories = []
            
            # Add new memory
            memory_id = str(uuid.uuid4())
            memory = {
                "id": memory_id,
                "user_input": user_input,
                "jarvis_response": jarvis_response,
                "timestamp": datetime.now().isoformat(),
                "context": context or {}
            }
            
            memories.append(memory)
            
            # Keep only last 100 memories
            if len(memories) > 100:
                memories = memories[-100:]
            
            # Save memories
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(memories, f, indent=2, ensure_ascii=False)
            
            print(f"Fallback memory added: {memory_id[:8]}...")
            return memory_id
            
        except Exception as e:
            print(f"Fallback memory failed: {e}")
            return None
    
    def _search_fallback_memory(self, query: str, limit: int = None) -> List[Dict[str, Any]]:
        """Fallback memory search using JSON"""
        try:
            memory_file = os.path.join(self.memory_dir, "fallback_memory.json")
            
            if not os.path.exists(memory_file):
                return []
            
            with open(memory_file, 'r', encoding='utf-8') as f:
                memories = json.load(f)
            
            # Simple keyword matching
            query_lower = query.lower()
            relevant_memories = []
            
            for memory in memories:
                user_input = memory.get("user_input", "").lower()
                jarvis_response = memory.get("jarvis_response", "").lower()
                
                # Check if query contains keywords from memory
                if any(word in user_input or word in jarvis_response for word in query_lower.split()):
                    memory["similarity"] = 0.8  # Fixed similarity for fallback
                    relevant_memories.append(memory)
            
            # Sort by timestamp (most recent first)
            relevant_memories.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            search_limit = limit or self.max_retrieval_count
            return relevant_memories[:search_limit]
            
        except Exception as e:
            print(f"Fallback memory search failed: {e}")
            return []
    
    def get_status(self) -> Dict[str, Any]:
        """Get neural memory service status"""
        return {
            "is_initialized": self.is_initialized,
            "chroma_available": CHROMA_AVAILABLE,
            "embedding_model_available": SENTENCE_TRANSFORMERS_AVAILABLE,
            "memory_directory": self.memory_dir,
            "collection_name": self.collection_name,
            "similarity_threshold": self.similarity_threshold,
            "max_memory_age_days": self.max_memory_age_days,
            "last_updated": datetime.now().isoformat()
        }
