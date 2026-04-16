"""
Fuzzy Command Matcher for JARVIS
Handles misspellings and variations in user commands
"""

from rapidfuzz import fuzz, process
from typing import List, Tuple, Optional, Dict
import re
import asyncio

class FuzzyMatcher:
    """Fuzzy matching system for JARVIS commands"""
    
    def __init__(self, threshold: float = 80.0):
        self.threshold = threshold
        self.command_mappings = {
            # Apps and Services
            'whatsapp': ['whatsapp', 'whats app', 'whatapp', 'whatsupp', 'watsapp', 'whatsap'],
            'youtube': ['youtube', 'you tube', 'utube', 'youtub', 'you tube', 'utube'],
            'chrome': ['chrome', 'google chrome', 'crome', 'chrom', 'googl chrome'],
            'firefox': ['firefox', 'fire fox', 'firefo', 'fire fox'],
            'edge': ['edge', 'ms edge', 'microsoft edge', 'edg'],
            'notepad': ['notepad', 'note pad', 'notepd', 'note pad'],
            'calculator': ['calculator', 'calc', 'calculater', 'calulator'],
            'explorer': ['explorer', 'file explorer', 'file explorer', 'explor'],
            'cmd': ['cmd', 'command prompt', 'command prompt', 'comand prompt'],
            
            # Actions
            'play': ['play', 'ply', 'pla', 'paly', 'play music', 'play song'],
            'open': ['open', 'opn', 'oppen', 'opan', 'start', 'launch'],
            'send': ['send', 'snd', 'sedn', 'send message', 'send email'],
            'message': ['message', 'msg', 'mesage', 'messsage', 'massage', 'mdg'],
            'email': ['email', 'e mail', 'e-mail', 'emal', 'mail'],
            'search': ['search', 'serch', 'searc', 'serach', 'web search'],
            'close': ['close', 'clos', 'cloe', 'cls', 'exit'],
            
            # System Commands
            'volume': ['volume', 'vol', 'volum', 'sound', 'audio'],
            'brightness': ['brightness', 'bright', 'brighness', 'screen brightness'],
            'shutdown': ['shutdown', 'shut down', 'shutdwon', 'shut down'],
            'restart': ['restart', 're start', 'restrat', 'reboot'],
            'screenshot': ['screenshot', 'screen shot', 'screen capture', 'ss'],
            'camera': ['camera', 'cam', 'camra', 'webcam', 'web cam'],
            
            # Analysis Commands
            'analyze': ['analyze', 'analize', 'anlyze', 'analysis', 'check'],
            'diagnose': ['diagnose', 'diagnos', 'diagnose', 'check'],
            'remember': ['remember', 'rember', 'remembr', 'memorize'],
            'recall': ['recall', 'recal', 'recal', 'remember'],
            
            # Media
            'music': ['music', 'musik', 'msic', 'song', 'songs'],
            'video': ['video', 'vido', 'vidoe', 'movie', 'movies'],
            'pause': ['pause', 'puse', 'paus', 'stop'],
            'next': ['next', 'nxt', 'next track', 'skip'],
            'previous': ['previous', 'prev', 'previous track', 'back'],
        }
        
        # Create reverse mapping for faster lookup
        self.reverse_mappings = {}
        for standard, variations in self.command_mappings.items():
            for variation in variations:
                self.reverse_mappings[variation.lower()] = standard
    
    def fuzzy_match_command(self, command: str) -> str:
        """
        Match command using fuzzy logic
        Returns the standardized command name
        """
        command_lower = command.lower()
        
        # First try exact match in reverse mappings
        if command_lower in self.reverse_mappings:
            return self.reverse_mappings[command_lower]
        
        # Try fuzzy matching
        best_match = None
        best_score = 0
        
        for standard, variations in self.command_mappings.items():
            for variation in variations:
                score = fuzz.ratio(command_lower, variation.lower())
                if score > best_score and score >= self.threshold:
                    best_score = score
                    best_match = standard
        
        return best_match if best_match else command
    
    def fuzzy_match_multiple(self, command: str) -> List[Tuple[str, float]]:
        """
        Find multiple fuzzy matches with scores
        Returns list of (matched_command, score) tuples
        """
        command_lower = command.lower()
        matches = []
        
        for standard, variations in self.command_mappings.items():
            for variation in variations:
                score = fuzz.ratio(command_lower, variation.lower())
                if score >= self.threshold:
                    matches.append((standard, score))
        
        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches
    
    def normalize_command(self, command: str) -> str:
        """
        Normalize entire command by replacing fuzzy matches
        """
        words = command.split()
        normalized_words = []
        
        for word in words:
            # Remove punctuation for matching
            clean_word = re.sub(r'[^\w\s]', '', word)
            if clean_word:
                matched = self.fuzzy_match_command(clean_word)
                # Don't replace if it's a proper name or if the match is too short
                if (matched != clean_word and 
                    len(clean_word) > 2 and 
                    matched != clean_word.lower() and
                    not clean_word.lower() in ['jarvis', 'tony', 'stark']):
                    normalized_words.append(matched)
                else:
                    normalized_words.append(word)
            else:
                normalized_words.append(word)
        
        return ' '.join(normalized_words)
    
    def get_command_type(self, command: str) -> Optional[str]:
        """
        Determine the type of command (app, action, system, etc.)
        """
        normalized = self.normalize_command(command)
        
        # Check for app commands
        apps = ['whatsapp', 'youtube', 'chrome', 'firefox', 'edge', 'notepad', 'calculator', 'explorer', 'cmd']
        for app in apps:
            if app in normalized:
                return 'app'
        
        # Check for action commands
        actions = ['play', 'open', 'send', 'message', 'email', 'search', 'close']
        for action in actions:
            if action in normalized:
                return 'action'
        
        # Check for system commands
        system = ['volume', 'brightness', 'shutdown', 'restart', 'screenshot', 'camera']
        for cmd in system:
            if cmd in normalized:
                return 'system'
        
        # Check for analysis commands
        analysis = ['analyze', 'diagnose', 'remember', 'recall']
        for cmd in analysis:
            if cmd in normalized:
                return 'analysis'
        
        # Check for media commands
        media = ['music', 'video', 'pause', 'next', 'previous']
        for cmd in media:
            if cmd in normalized:
                return 'media'
        
        return 'general'

class LLMCorrector:
    """LLM-based command correction"""
    
    def __init__(self):
        self.correction_cache = {}
    
    async def correct_command(self, command: str) -> str:
        """
        Use Ollama to correct spelling in commands
        """
        # Check cache first
        if command in self.correction_cache:
            return self.correction_cache[command]
        
        try:
            import ollama
            
            correction_prompt = f"""Correct the spelling and return only the cleaned name of the app or action the user wants to open. 
User input: "{command}"
Corrected output (only the corrected term):"""
            
            response = ollama.generate('llama3.1:8b', correction_prompt)
            corrected = response['response'].strip()
            
            # Cache the result
            self.correction_cache[command] = corrected
            return corrected
            
        except Exception as e:
            print(f"LLM correction failed: {e}")
            return command

class SmartCommandProcessor:
    """Combined fuzzy and LLM command processing"""
    
    def __init__(self, threshold: float = 90.0):
        self.fuzzy_matcher = FuzzyMatcher(threshold)
        self.llm_corrector = LLMCorrector()
    
    def process_command(self, command: str) -> str:
        """
        Process command using fuzzy matching first, then LLM if needed
        """
        # Check for math expressions - bypass all processing
        # Only bypass if it looks like a pure math expression, not a command with phone numbers
        math_symbols = ['+', '-', '*', '/', '=', '(', ')', '^', '%']
        has_digits = any(char.isdigit() for char in command)
        has_math = any(symbol in command for symbol in math_symbols)
        
        # Check if it's a pure math expression (no letters other than common math words)
        words = command.lower().split()
        math_words = {'plus', 'minus', 'times', 'divide', 'equals', 'x', 'multiply'}
        non_math_words = []
        
        for word in words:
            # Remove math symbols to check if it's just numbers
            clean_word = word.replace('+', '').replace('-', '').replace('*', '').replace('/', '').replace('=', '').replace('(', '').replace(')', '').replace('^', '').replace('%', '')
            # If the word contains letters and is not a math word, it's non-math
            if any(char.isalpha() for char in clean_word) and word not in math_words:
                non_math_words.append(word)
        
        if has_digits and has_math and len(non_math_words) == 0:
            return command  # Return math expression unchanged
        
        # Check for pure greetings only - not commands that contain greetings
        command_lower = command.lower().strip()
        pure_greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings']
        
        # Only bypass if the entire command is just a greeting
        if command_lower in pure_greetings:
            return command  # Return original greeting unchanged
        
        # Don't bypass if it contains action words
        action_words = ['open', 'close', 'send', 'message', 'play', 'stop', 'start', 'launch', 'run', 'execute']
        if any(action in command_lower for action in action_words):
            # This is a command, proceed with fuzzy matching
            pass
        else:
            # Check if it's a greeting with additional words (like "hello there")
            is_greeting_with_extra = False
            for greeting in pure_greetings:
                if command_lower.startswith(greeting) and len(command_lower) > len(greeting):
                    # It's a greeting with additional words, proceed with fuzzy matching
                    is_greeting_with_extra = True
                    break
            
            if not is_greeting_with_extra:
                # Check if it's exactly a greeting
                for greeting in pure_greetings:
                    if command_lower == greeting:
                        # Pure greeting, bypass
                        return command
        
        # Try fuzzy matching first
        normalized = self.fuzzy_matcher.normalize_command(command)
        
        # If no significant changes, try LLM correction (synchronous)
        if normalized == command:
            try:
                # Try to run the async LLM correction with proper async handling
                import asyncio
                try:
                    loop = asyncio.get_running_loop()
                    # We're in a running event loop, use run_in_executor
                    future = loop.run_in_executor(None, asyncio.run, self.llm_corrector.correct_command(command))
                    corrected = loop.run_until_complete(future)
                except RuntimeError:
                    # No running event loop, use asyncio.run
                    corrected = asyncio.run(self.llm_corrector.correct_command(command))
                
                if corrected != command:
                    return corrected
            except Exception as e:
                print(f"LLM correction failed: {e}")
                # Fall back to fuzzy matching result
        
        # LAST RESORT: Only use fuzzy matching for unclear intents or app commands
        # Check if this is an unclear intent or app command that needs fuzzy matching
        words = command.lower().split()
        unclear_indicators = ['what', 'how', 'tell', 'explain', 'help', 'why', 'when', 'where', 'who', 'which']
        app_commands = ['open', 'launch', 'start', 'run', 'execute']
        
        # Only use fuzzy matching if query is unclear or contains app command indicators
        if (any(indicator in words for indicator in unclear_indicators) or 
            any(cmd in words for cmd in app_commands)):
            # This is an unclear query or app command - use fuzzy matching
            if normalized != command:
                return normalized
            else:
                return command
        else:
            # Clear intent (chat, math, etc.) - return as-is without fuzzy matching
            return command
    
    async def process_command_async(self, command: str) -> str:
        """
        Async version of process_command for compatibility
        """
        return self.process_command(command)
    
    def get_command_info(self, command: str) -> Dict:
        """
        Get detailed information about the command
        """
        normalized = self.fuzzy_matcher.normalize_command(command)
        command_type = self.fuzzy_matcher.get_command_type(normalized)
        matches = self.fuzzy_matcher.fuzzy_match_multiple(command)
        
        return {
            'original': command,
            'normalized': normalized,
            'type': command_type,
            'matches': matches,
            'confidence': matches[0][1] if matches else 0
        }
