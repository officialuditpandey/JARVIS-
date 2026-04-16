#!/usr/bin/env python3
"""
Live Problem Solver Service for JARVIS
Analyze active window to solve bugs or math problems in real-time
"""

import os
import sys
import time
import threading
import re
import json
import math
import ast
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import pyautogui
import cv2
import numpy as np

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import win32gui
    import win32con
    import win32process
    WIN32_AVAILABLE = True
except ImportError:
    print("win32gui not available - Installing...")
    os.system("pip install pywin32")
    try:
        import win32gui
        import win32con
        import win32process
        WIN32_AVAILABLE = True
    except ImportError:
        WIN32_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

class LiveProblemSolverService:
    """Live problem solver service for real-time analysis"""
    
    def __init__(self):
        self.is_active = False
        self.solver_thread = None
        self.stop_event = threading.Event()
        
        # Analysis configuration
        self.analysis_interval = 5  # seconds
        self.last_analysis_time = 0
        self.current_window_info = {}
        self.problem_history = []
        self.solutions = []
        
        # Problem detection patterns
        self.error_patterns = [
            r'error[:\s]*([^\n\r]+)',
            r'exception[:\s]*([^\n\r]+)',
            r'failed[:\s]*([^\n\r]+)',
            r'cannot[:\s]*([^\n\r]+)',
            r'unable[:\s]*([^\n\r]+)',
            r'traceback[:\s]*([^\n\r]+)',
            r'syntaxerror[:\s]*([^\n\r]+)',
            r'nameerror[:\s]*([^\n\r]+)',
            r'typeerror[:\s]*([^\n\r]+)',
            r'valueerror[:\s]*([^\n\r]+)',
            r'indexerror[:\s]*([^\n\r]+)',
            r'keyerror[:\s]*([^\n\r]+)',
            r'attributeerror[:\s]*([^\n\r]+)',
            r'importerror[:\s]*([^\n\r]+)',
            r'moduleerror[:\s]*([^\n\r]+)'
        ]
        
        self.math_patterns = [
            r'([0-9]+(?:\.[0-9]+)?)\s*([+\-*/])\s*([0-9]+(?:\.[0-9]+)?)',
            r'sqrt\(([^)]+)\)',
            r'pow\(([^,]+),\s*([^)]+)\)',
            r'log\(([^)]+)\)',
            r'ln\(([^)]+)\)',
            r'sin\(([^)]+)\)',
            r'cos\(([^)]+)\)',
            r'tan\(([^)]+)\)',
            r'([0-9]+)!\s*$',
            r'abs\(([^)]+)\)',
            r'ceil\(([^)]+)\)',
            r'floor\(([^)]+)\)',
            r'round\(([^)]+)\)'
        ]
        
        # Programming language detection
        self.language_patterns = {
            'python': [r'import\s+\w+', r'def\s+\w+\s*\(', r'class\s+\w+', r'print\s*\(', r'if\s+__name__'],
            'javascript': [r'function\s+\w+', r'const\s+\w+', r'let\s+\w+', r'var\s+\w+', r'console\.log'],
            'java': [r'public\s+class', r'public\s+static\s+void\s+main', r'System\.out\.println'],
            'cpp': [r'#include\s*<', r'int\s+main\s*\(', r'cout\s*<<', r'cin\s*>>'],
            'html': [r'<html', r'<body', r'<div', r'<script', r'<style'],
            'css': [r'\.?\w+\s*{', r'background-color:', r'margin:', r'padding:'],
            'sql': [r'SELECT\s+', r'FROM\s+', r'WHERE\s+', r'INSERT\s+INTO', r'UPDATE\s+']
        }
        
        # Solution templates
        self.solution_templates = {
            'syntax_error': {
                'python': "Check for missing colons, incorrect indentation, or unmatched brackets.",
                'javascript': "Check for missing semicolons, brackets, or syntax errors.",
                'general': "Review the syntax and ensure all brackets, quotes, and parentheses are properly matched."
            },
            'name_error': {
                'python': "Variable is not defined. Check spelling and ensure the variable is declared before use.",
                'general': "Check if the variable or function name is spelled correctly and properly declared."
            },
            'type_error': {
                'python': "Incompatible data types. Check if you're using the right data type for the operation.",
                'general': "Data type mismatch. Ensure you're using compatible types for the operation."
            },
            'import_error': {
                'python': "Module not found. Check if the module is installed and the import statement is correct.",
                'general': "Module or library not available. Check installation and import paths."
            }
        }
        
        # Performance metrics
        self.analysis_count = 0
        self.problems_detected = 0
        self.solutions_provided = 0
        self.start_time = time.time()
        
        print("Live Problem Solver Service initialized")
    
    def start_live_analysis(self) -> bool:
        """Start live problem analysis"""
        try:
            if self.is_active:
                return True
            
            self.is_active = True
            self.stop_event.clear()
            
            # Start analysis thread
            self.solver_thread = threading.Thread(target=self._analysis_loop, daemon=True)
            self.solver_thread.start()
            
            print("Live problem analysis started")
            return True
            
        except Exception as e:
            print(f"Failed to start live analysis: {e}")
            return False
    
    def stop_live_analysis(self):
        """Stop live problem analysis"""
        try:
            self.is_active = False
            self.stop_event.set()
            
            if self.solver_thread and self.solver_thread.is_alive():
                self.solver_thread.join(timeout=2)
            
            print("Live problem analysis stopped")
            
        except Exception as e:
            print(f"Failed to stop live analysis: {e}")
    
    def _analysis_loop(self):
        """Main analysis loop"""
        print("Live analysis loop started")
        
        while self.is_active and not self.stop_event.is_set():
            try:
                current_time = time.time()
                
                # Perform analysis at intervals
                if current_time - self.last_analysis_time > self.analysis_interval:
                    self._analyze_active_window()
                    self.last_analysis_time = current_time
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Analysis loop error: {e}")
                time.sleep(5)
        
        print("Live analysis loop ended")
    
    def _analyze_active_window(self):
        """Analyze the active window for problems"""
        try:
            # Get active window information
            window_info = self._get_active_window_info()
            
            if not window_info:
                return
            
            # Capture screenshot of active window
            screenshot = self._capture_window_screenshot(window_info)
            
            if screenshot is None:
                return
            
            # Extract text from screenshot
            text_content = self._extract_text_from_screenshot(screenshot)
            
            if not text_content:
                return
            
            # Detect problems
            problems = self._detect_problems(text_content, window_info)
            
            # Generate solutions
            solutions = self._generate_solutions(problems, text_content, window_info)
            
            # Store analysis results
            analysis_result = {
                'timestamp': datetime.now().isoformat(),
                'window_info': window_info,
                'text_content': text_content[:1000],  # Store first 1000 chars
                'problems_detected': problems,
                'solutions_generated': solutions
            }
            
            self.problem_history.append(analysis_result)
            self.current_window_info = window_info
            
            # Keep only last 50 analyses
            if len(self.problem_history) > 50:
                self.problem_history = self.problem_history[-50:]
            
            self.analysis_count += 1
            
            # Announce solutions if problems found
            if problems and solutions:
                self._announce_solutions(solutions)
                self.problems_detected += len(problems)
                self.solutions_provided += len(solutions)
            
            print(f"Analysis completed: {len(problems)} problems, {len(solutions)} solutions")
            
        except Exception as e:
            print(f"Active window analysis failed: {e}")
    
    def _get_active_window_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the active window"""
        try:
            if not WIN32_AVAILABLE:
                return None
            
            hwnd = win32gui.GetForegroundWindow()
            
            if not hwnd:
                return None
            
            # Get window title
            title = win32gui.GetWindowText(hwnd)
            
            # Get window class
            class_name = win32gui.GetClassName(hwnd)
            
            # Get window rectangle
            rect = win32gui.GetWindowRect(hwnd)
            
            # Get process information
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            window_info = {
                'handle': hwnd,
                'title': title,
                'class_name': class_name,
                'position': (rect[0], rect[1]),
                'size': (rect[2] - rect[0], rect[3] - rect[1]),
                'process_id': pid
            }
            
            return window_info
            
        except Exception as e:
            print(f"Failed to get active window info: {e}")
            return None
    
    def _capture_window_screenshot(self, window_info: Dict[str, Any]) -> Optional[np.ndarray]:
        """Capture screenshot of the active window"""
        try:
            # Get window bounds
            x, y = window_info['position']
            width, height = window_info['size']
            
            # Capture screenshot
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            
            # Convert to numpy array
            screenshot_array = np.array(screenshot)
            screenshot_bgr = cv2.cvtColor(screenshot_array, cv2.COLOR_RGB2BGR)
            
            return screenshot_bgr
            
        except Exception as e:
            print(f"Failed to capture window screenshot: {e}")
            return None
    
    def _extract_text_from_screenshot(self, screenshot: np.ndarray) -> str:
        """Extract text from screenshot using OCR"""
        try:
            if not TESSERACT_AVAILABLE:
                return "OCR not available"
            
            # Preprocess image for better OCR
            gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to get better text extraction
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Extract text
            text = pytesseract.image_to_string(thresh)
            
            return text.strip()
            
        except Exception as e:
            print(f"Text extraction failed: {e}")
            return ""
    
    def _detect_problems(self, text_content: str, window_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect problems in text content"""
        problems = []
        
        # Detect programming errors
        for pattern in self.error_patterns:
            matches = re.finditer(pattern, text_content, re.IGNORECASE)
            for match in matches:
                error_message = match.group(1) if match.groups() else match.group(0)
                
                # Determine error type
                error_type = self._classify_error(error_message)
                
                # Determine programming language
                language = self._detect_programming_language(text_content)
                
                problem = {
                    'type': 'programming_error',
                    'error_type': error_type,
                    'language': language,
                    'message': error_message,
                    'line_number': self._extract_line_number(text_content, match.start()),
                    'confidence': 0.8
                }
                
                problems.append(problem)
        
        # Detect math problems
        math_problems = self._detect_math_problems(text_content)
        problems.extend(math_problems)
        
        # Detect logic issues
        logic_problems = self._detect_logic_issues(text_content)
        problems.extend(logic_problems)
        
        return problems
    
    def _classify_error(self, error_message: str) -> str:
        """Classify error type"""
        error_lower = error_message.lower()
        
        if 'syntax' in error_lower:
            return 'syntax_error'
        elif 'name' in error_lower and 'not defined' in error_lower:
            return 'name_error'
        elif 'type' in error_lower:
            return 'type_error'
        elif 'import' in error_lower:
            return 'import_error'
        elif 'index' in error_lower:
            return 'index_error'
        elif 'key' in error_lower:
            return 'key_error'
        elif 'attribute' in error_lower:
            return 'attribute_error'
        elif 'value' in error_lower:
            return 'value_error'
        elif 'module' in error_lower:
            return 'module_error'
        else:
            return 'general_error'
    
    def _detect_programming_language(self, text_content: str) -> str:
        """Detect programming language from text content"""
        text_lower = text_content.lower()
        
        language_scores = {}
        for language, patterns in self.language_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    score += 1
            language_scores[language] = score
        
        if language_scores:
            best_language = max(language_scores, key=language_scores.get)
            if language_scores[best_language] > 0:
                return best_language
        
        return 'unknown'
    
    def _extract_line_number(self, text_content: str, position: int) -> Optional[int]:
        """Extract line number from text position"""
        try:
            text_before = text_content[:position]
            lines = text_before.count('\n')
            return lines + 1
        except:
            return None
    
    def _detect_math_problems(self, text_content: str) -> List[Dict[str, Any]]:
        """Detect math problems in text"""
        problems = []
        
        for pattern in self.math_patterns:
            matches = re.finditer(pattern, text_content)
            for match in matches:
                problem = {
                    'type': 'math_problem',
                    'expression': match.group(0),
                    'match_groups': match.groups(),
                    'position': match.start(),
                    'confidence': 0.9
                }
                problems.append(problem)
        
        return problems
    
    def _detect_logic_issues(self, text_content: str) -> List[Dict[str, Any]]:
        """Detect logic issues in code"""
        problems = []
        
        # Detect potential infinite loops
        if re.search(r'while\s+True\s*:', text_content) and not re.search(r'break', text_content):
            problems.append({
                'type': 'logic_issue',
                'issue_type': 'potential_infinite_loop',
                'description': 'Potential infinite loop detected - while True without break',
                'confidence': 0.7
            })
        
        # Detect missing return statements
        if re.search(r'def\s+\w+\s*\([^)]*\)\s*:', text_content):
            if not re.search(r'return\s+', text_content):
                problems.append({
                    'type': 'logic_issue',
                    'issue_type': 'missing_return',
                    'description': 'Function defined but no return statement found',
                    'confidence': 0.6
                })
        
        return problems
    
    def _generate_solutions(self, problems: List[Dict[str, Any]], text_content: str, window_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate solutions for detected problems"""
        solutions = []
        
        for problem in problems:
            if problem['type'] == 'programming_error':
                solution = self._generate_programming_solution(problem, text_content)
            elif problem['type'] == 'math_problem':
                solution = self._generate_math_solution(problem)
            elif problem['type'] == 'logic_issue':
                solution = self._generate_logic_solution(problem, text_content)
            else:
                solution = self._generate_general_solution(problem)
            
            if solution:
                solutions.append(solution)
        
        return solutions
    
    def _generate_programming_solution(self, problem: Dict[str, Any], text_content: str) -> Optional[Dict[str, Any]]:
        """Generate solution for programming error"""
        try:
            error_type = problem['error_type']
            language = problem['language']
            
            # Get template solution
            template = self.solution_templates.get(error_type, {})
            base_solution = template.get(language, template.get('general', "Check the error and review your code."))
            
            # Generate specific solution
            solution = {
                'type': 'programming_solution',
                'problem_type': error_type,
                'language': language,
                'solution': base_solution,
                'specific_fix': self._generate_specific_fix(problem, text_content),
                'confidence': 0.8
            }
            
            return solution
            
        except Exception as e:
            print(f"Failed to generate programming solution: {e}")
            return None
    
    def _generate_math_solution(self, problem: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate solution for math problem"""
        try:
            expression = problem['expression']
            
            # Evaluate the math expression
            result = self._evaluate_math_expression(expression)
            
            solution = {
                'type': 'math_solution',
                'expression': expression,
                'result': result,
                'explanation': self._generate_math_explanation(expression, result),
                'confidence': 0.95
            }
            
            return solution
            
        except Exception as e:
            return {
                'type': 'math_solution',
                'expression': expression,
                'result': 'Error: Cannot evaluate',
                'explanation': f'Cannot evaluate expression: {str(e)}',
                'confidence': 0.1
            }
    
    def _generate_logic_solution(self, problem: Dict[str, Any], text_content: str) -> Optional[Dict[str, Any]]:
        """Generate solution for logic issue"""
        try:
            issue_type = problem['issue_type']
            
            if issue_type == 'potential_infinite_loop':
                solution = "Add a break condition or use a finite loop instead of while True."
            elif issue_type == 'missing_return':
                solution = "Add a return statement to your function or specify a return type."
            else:
                solution = "Review the logic flow of your code."
            
            return {
                'type': 'logic_solution',
                'issue_type': issue_type,
                'solution': solution,
                'confidence': 0.7
            }
            
        except Exception as e:
            return None
    
    def _generate_general_solution(self, problem: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate general solution"""
        return {
            'type': 'general_solution',
            'solution': "Review the detected issue and consult documentation for best practices.",
            'confidence': 0.5
        }
    
    def _generate_specific_fix(self, problem: Dict[str, Any], text_content: str) -> str:
        """Generate specific fix for the problem"""
        try:
            error_message = problem['message']
            error_type = problem['error_type']
            
            if error_type == 'syntax_error':
                if 'colon' in error_message.lower():
                    return "Add a colon (:) at the end of the line."
                elif 'indentation' in error_message.lower():
                    return "Check indentation - Python requires consistent indentation."
                elif 'bracket' in error_message.lower() or 'parenthesis' in error_message.lower():
                    return "Check for unmatched brackets, parentheses, or quotes."
            elif error_type == 'name_error':
                var_name = self._extract_variable_name(error_message)
                if var_name:
                    return f"Define variable '{var_name}' before using it or check spelling."
            elif error_type == 'type_error':
                return "Check data types - ensure you're using compatible types for operations."
            
            return "Review the error message and check the corresponding line in your code."
            
        except:
            return "Check the error details and review your code syntax."
    
    def _extract_variable_name(self, error_message: str) -> Optional[str]:
        """Extract variable name from error message"""
        try:
            # Look for pattern like "name 'variable' is not defined"
            match = re.search(r"name '([^']+)' is not defined", error_message)
            if match:
                return match.group(1)
            return None
        except:
            return None
    
    def _evaluate_math_expression(self, expression: str) -> Any:
        """Evaluate math expression safely"""
        try:
            # Handle basic arithmetic
            if re.match(r'^[0-9+\-*/.() ]+$', expression):
                return eval(expression)
            
            # Handle functions
            if 'sqrt(' in expression:
                num = float(re.search(r'sqrt\(([^)]+)\)', expression).group(1))
                return math.sqrt(num)
            elif 'pow(' in expression:
                base, exp = map(float, re.search(r'pow\(([^,]+),\s*([^)]+)\)', expression).groups())
                return math.pow(base, exp)
            elif 'log(' in expression:
                num = float(re.search(r'log\(([^)]+)\)', expression).group(1))
                return math.log(num)
            elif 'sin(' in expression:
                num = float(re.search(r'sin\(([^)]+)\)', expression).group(1))
                return math.sin(num)
            elif 'cos(' in expression:
                num = float(re.search(r'cos\(([^)]+)\)', expression).group(1))
                return math.cos(num)
            elif 'tan(' in expression:
                num = float(re.search(r'tan\(([^)]+)\)', expression).group(1))
                return math.tan(num)
            elif expression.endswith('!'):
                num = int(expression[:-1])
                return math.factorial(num)
            elif 'abs(' in expression:
                num = float(re.search(r'abs\(([^)]+)\)', expression).group(1))
                return abs(num)
            elif 'ceil(' in expression:
                num = float(re.search(r'ceil\(([^)]+)\)', expression).group(1))
                return math.ceil(num)
            elif 'floor(' in expression:
                num = float(re.search(r'floor\(([^)]+)\)', expression).group(1))
                return math.floor(num)
            elif 'round(' in expression:
                num = float(re.search(r'round\(([^)]+)\)', expression).group(1))
                return round(num)
            
            return "Cannot evaluate"
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _generate_math_explanation(self, expression: str, result: Any) -> str:
        """Generate explanation for math solution"""
        try:
            if isinstance(result, str) and "Error" in result:
                return result
            
            if '+' in expression:
                return f"The sum of the numbers is {result}"
            elif '-' in expression:
                return f"The difference is {result}"
            elif '*' in expression:
                return f"The product is {result}"
            elif '/' in expression:
                return f"The quotient is {result}"
            elif 'sqrt(' in expression:
                return f"The square root is {result}"
            elif 'pow(' in expression:
                return f"The power is {result}"
            elif 'sin(' in expression:
                return f"The sine is {result}"
            elif 'cos(' in expression:
                return f"The cosine is {result}"
            elif 'tan(' in expression:
                return f"The tangent is {result}"
            elif expression.endswith('!'):
                return f"The factorial is {result}"
            else:
                return f"The result is {result}"
                
        except:
            return f"Calculated result: {result}"
    
    def _announce_solutions(self, solutions: List[Dict[str, Any]]):
        """Announce solutions to user"""
        try:
            for i, solution in enumerate(solutions[:3], 1):  # Announce top 3
                if solution['type'] == 'programming_solution':
                    message = f"Programming issue detected: {solution['solution']}"
                elif solution['type'] == 'math_solution':
                    message = f"Math problem: {solution['expression']} = {solution['result']}"
                elif solution['type'] == 'logic_solution':
                    message = f"Logic issue: {solution['solution']}"
                else:
                    message = f"Issue detected: {solution['solution']}"
                
                print(f"SOLUTION {i}: {message}")
                
                # In production, this would use JARVIS voice system
                
        except Exception as e:
            print(f"Solution announcement failed: {e}")
    
    def get_current_solutions(self) -> List[Dict[str, Any]]:
        """Get current solutions"""
        return self.solutions
    
    def get_problem_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent problem history"""
        return self.problem_history[-limit:]
    
    def solve_specific_problem(self, problem_text: str) -> Dict[str, Any]:
        """Solve a specific problem provided by user"""
        try:
            # Detect problem type
            problems = self._detect_problems(problem_text, {'title': 'User Input'})
            
            if not problems:
                return {
                    'success': False,
                    'message': 'No specific problem detected in the provided text'
                }
            
            # Generate solutions
            solutions = self._generate_solutions(problems, problem_text, {'title': 'User Input'})
            
            return {
                'success': True,
                'problems_detected': problems,
                'solutions_generated': solutions,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Problem solving failed: {str(e)}'
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get live problem solver service status"""
        return {
            'is_active': self.is_active,
            'analysis_interval': self.analysis_interval,
            'last_analysis_time': datetime.fromtimestamp(self.last_analysis_time).isoformat() if self.last_analysis_time > 0 else None,
            'analysis_count': self.analysis_count,
            'problems_detected': self.problems_detected,
            'solutions_provided': self.solutions_provided,
            'current_window': self.current_window_info.get('title', 'None'),
            'win32_available': WIN32_AVAILABLE,
            'tesseract_available': TESSERACT_AVAILABLE,
            'last_updated': datetime.now().isoformat()
        }
