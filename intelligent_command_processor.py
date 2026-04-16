#!/usr/bin/env python3
"""
Intelligent Command Processor for JARVIS
Automatically understands command variations without hardcoded patterns
"""

import re
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Any
import difflib

class IntelligentCommandProcessor:
    def __init__(self):
        self.learning_file = "command_patterns.json"
        self.command_categories = {
            "vision": {
                "keywords": ["see", "look", "vision", "camera", "holding", "hand", "object", "identify", "what", "show", "scan", "got", "am"],
                "context_words": ["in my hand", "holding", "camera", "room", "around", "screen", "my hand", "the room"],
                "action_words": ["tell", "show", "identify", "describe", "analyze", "what", "scan", "look"],
                "confidence_threshold": 0.3
            },
            "security": {
                "keywords": ["security", "guard", "protect", "monitor", "watch", "safe"],
                "context_words": ["mode", "engage", "start", "activate"],
                "action_words": ["engage", "start", "activate", "enable"],
                "confidence_threshold": 0.3
            },
            "browser": {
                "keywords": ["browse", "search", "open", "website", "go", "navigate"],
                "context_words": ["website", "page", "search", "browse"],
                "action_words": ["open", "search", "go", "navigate"],
                "confidence_threshold": 0.3
            },
            "automation": {
                "keywords": ["automation", "macro", "workflow", "prepare", "meeting", "study"],
                "context_words": ["mode", "prepare", "setup", "configure"],
                "action_words": ["prepare", "setup", "configure", "start"],
                "confidence_threshold": 0.3
            }
        }
        self.learned_patterns = self.load_learned_patterns()
    
    def load_learned_patterns(self) -> Dict[str, List[str]]:
        """Load previously learned command patterns"""
        try:
            if os.path.exists(self.learning_file):
                with open(self.learning_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Could not load learned patterns: {e}")
        return {category: [] for category in self.command_categories.keys()}
    
    def save_learned_patterns(self):
        """Save learned patterns to file"""
        try:
            with open(self.learning_file, 'w') as f:
                json.dump(self.learned_patterns, f, indent=2)
        except Exception as e:
            print(f"Could not save learned patterns: {e}")
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for better matching"""
        # Convert to lowercase
        text = text.lower()
        # Remove punctuation
        text = re.sub(r'[^\w\s]', ' ', text)
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        # Common misspellings and variations
        replacements = {
            'whats': 'what is',
            'what\'s': 'what is',
            'wuts': 'what is',
            'tellin': 'telling',
            'holdin': 'holding',
            'lookin': 'looking',
            'showin': 'showing',
            'cam': 'camera',
            'pic': 'picture',
            'photo': 'picture',
            'obj': 'object',
            'objs': 'objects'
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text
    
    def calculate_confidence(self, query: str, category: str) -> float:
        """Calculate confidence score for a category match"""
        if category not in self.command_categories:
            return 0.0
        
        config = self.command_categories[category]
        normalized_query = self.normalize_text(query)
        
        # Direct keyword matching - much simpler approach
        keyword_score = 0.0
        for keyword in config["keywords"]:
            if keyword in normalized_query:
                keyword_score += 1.0
        
        # Context phrase matching
        context_score = 0.0
        for context in config["context_words"]:
            if context in normalized_query:
                context_score += 1.0
        
        # Action word matching
        action_score = 0.0
        for action in config["action_words"]:
            if action in normalized_query:
                action_score += 1.0
        
        # Calculate total score
        total_score = keyword_score + context_score + action_score
        
        # Normalize by query length to avoid bias toward longer queries
        normalized_score = total_score / max(len(normalized_query.split()), 1)
        
        # Boost score for exact matches
        for keyword in config["keywords"]:
            if keyword == normalized_query.strip():
                normalized_score = 1.0
                break
        
        # Learned pattern matching (bonus)
        if category in self.learned_patterns:
            for pattern in self.learned_patterns[category]:
                similarity = difflib.SequenceMatcher(None, normalized_query, pattern).ratio()
                if similarity > 0.7:
                    normalized_score = max(normalized_score, similarity)
        
        return min(normalized_score, 1.0)
    
    def extract_intent_and_entities(self, query: str, category: str) -> Dict[str, Any]:
        """Extract specific intent and entities from the query"""
        normalized_query = self.normalize_text(query)
        
        result = {
            "category": category,
            "intent": "general",
            "entities": {},
            "specific_action": None
        }
        
        if category == "vision":
            # Extract specific vision intent
            if any(word in normalized_query for word in ["holding", "hand"]):
                result["intent"] = "identify_holding"
                result["specific_action"] = "identify_objects"
            elif any(word in normalized_query for word in ["room", "around", "scan"]):
                result["intent"] = "scan_environment"
                result["specific_action"] = "scan_room"
            elif any(word in normalized_query for word in ["camera", "see", "look"]):
                result["intent"] = "camera_analysis"
                result["specific_action"] = "camera_view"
            else:
                result["intent"] = "general_vision"
                result["specific_action"] = "identify_objects"
        
        elif category == "security":
            if any(word in normalized_query for word in ["engage", "start", "activate"]):
                result["intent"] = "activate_security"
                result["specific_action"] = "engage_security"
            else:
                result["intent"] = "general_security"
                result["specific_action"] = "security_status"
        
        elif category == "browser":
            if "search" in normalized_query:
                result["intent"] = "web_search"
                result["specific_action"] = "search_web"
            elif any(word in normalized_query for word in ["open", "go", "navigate"]):
                result["intent"] = "open_website"
                result["specific_action"] = "open_browser"
            else:
                result["intent"] = "general_browser"
                result["specific_action"] = "browser_action"
        
        elif category == "automation":
            if any(word in normalized_query for word in ["prepare", "setup"]):
                result["intent"] = "setup_automation"
                result["specific_action"] = "prepare_macro"
            else:
                result["intent"] = "general_automation"
                result["specific_action"] = "automation_action"
        
        return result
    
    def process_command(self, query: str) -> Dict[str, Any]:
        """Process a command and determine the best category and intent"""
        normalized_query = self.normalize_text(query)
        
        # Calculate confidence for each category
        category_scores = {}
        for category in self.command_categories:
            confidence = self.calculate_confidence(normalized_query, category)
            category_scores[category] = confidence
        
        # Find best match
        best_category = max(category_scores, key=category_scores.get)
        best_confidence = category_scores[best_category]
        
        # Check if confidence meets threshold
        threshold = self.command_categories[best_category]["confidence_threshold"]
        
        if best_confidence >= threshold:
            # Extract intent and entities
            intent_result = self.extract_intent_and_entities(query, best_category)
            intent_result["confidence"] = best_confidence
            intent_result["all_scores"] = category_scores
            
            # Learn from this successful match
            self.learn_from_command(normalized_query, best_category)
            
            return intent_result
        else:
            # No confident match, return general processing
            return {
                "category": "general",
                "intent": "unknown",
                "confidence": best_confidence,
                "all_scores": category_scores,
                "specific_action": None,
                "entities": {}
            }
    
    def learn_from_command(self, normalized_query: str, category: str):
        """Learn from successful command matches"""
        if category not in self.learned_patterns:
            self.learned_patterns[category] = []
        
        # Add to learned patterns if not already present and if it's unique enough
        if normalized_query not in self.learned_patterns[category]:
            # Check if this pattern is sufficiently different from existing ones
            is_unique = True
            for existing in self.learned_patterns[category]:
                similarity = difflib.SequenceMatcher(None, normalized_query, existing).ratio()
                if similarity > 0.8:  # Too similar, don't add
                    is_unique = False
                    break
            
            if is_unique and len(self.learned_patterns[category]) < 50:  # Limit learned patterns
                self.learned_patterns[category].append(normalized_query)
                self.save_learned_patterns()
                print(f"Learned new pattern for {category}: {normalized_query}")
    
    def get_command_suggestion(self, query: str) -> str:
        """Get suggestions for unclear commands"""
        normalized_query = self.normalize_text(query)
        category_scores = {}
        
        for category in self.command_categories:
            confidence = self.calculate_confidence(normalized_query, category)
            category_scores[category] = confidence
        
        best_category = max(category_scores, key=category_scores.get)
        best_confidence = category_scores[best_category]
        
        if best_category == "vision":
            return "Did you mean to ask about vision analysis? Try: 'what do you see', 'what am I holding', or 'scan the room'"
        elif best_category == "security":
            return "Did you mean to engage security? Try: 'engage security mode' or 'start security'"
        elif best_category == "browser":
            return "Did you want to browse the web? Try: 'search for [topic]' or 'open website [url]'"
        elif best_category == "automation":
            return "Did you want to set up automation? Try: 'prepare study mode' or 'setup meeting'"
        else:
            return "I'm not sure what you want. Try being more specific about vision, security, browser, or automation tasks."
    
    def add_new_category(self, name: str, keywords: List[str], context_words: List[str], action_words: List[str], threshold: float = 0.6):
        """Add a new command category"""
        self.command_categories[name] = {
            "keywords": keywords,
            "context_words": context_words,
            "action_words": action_words,
            "confidence_threshold": threshold
        }
        if name not in self.learned_patterns:
            self.learned_patterns[name] = []
        self.save_learned_patterns()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get learning statistics"""
        stats = {
            "categories": len(self.command_categories),
            "learned_patterns": {cat: len(patterns) for cat, patterns in self.learned_patterns.items()},
            "total_patterns": sum(len(patterns) for patterns in self.learned_patterns.values())
        }
        return stats

# Global instance
intelligent_processor = IntelligentCommandProcessor()

def process_command_intelligently(query: str) -> Dict[str, Any]:
    """Global function to process commands intelligently"""
    return intelligent_processor.process_command(query)

def test_intelligent_processor():
    """Test the intelligent command processor"""
    test_commands = [
        "what am I holding",
        "tell me what's in my hand",
        "can you see what I got",
        "look at my hand and tell me",
        "show me what you see",
        "scan the room",
        "what do you see around",
        "engage security mode",
        "start security",
        "search for python tutorials",
        "open google",
        "prepare study mode",
        "setup meeting",
        "random unclear command",
        "help me with something"
    ]
    
    print("=== Testing Intelligent Command Processor ===")
    for cmd in test_commands:
        result = process_command_intelligently(cmd)
        print(f"\nCommand: '{cmd}'")
        print(f"Category: {result['category']} (confidence: {result['confidence']:.2f})")
        print(f"Intent: {result['intent']}")
        print(f"Action: {result['specific_action']}")
        
        if result['confidence'] < 0.6:
            suggestion = intelligent_processor.get_command_suggestion(cmd)
            print(f"Suggestion: {suggestion}")
    
    print(f"\n=== Statistics ===")
    stats = intelligent_processor.get_statistics()
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    test_intelligent_processor()
