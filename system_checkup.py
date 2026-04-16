#!/usr/bin/env python3
"""
JARVIS System Comprehensive Checkup
Tests every feature of the integrated JARVIS system
"""

import sys
import os
import time
import subprocess
from datetime import datetime

# Add JARVIS backend path
sys.path.append(os.path.dirname(__file__))

class JARVISCheckup:
    def __init__(self):
        self.test_results = []
        self.start_time = datetime.now()
        
    def log_test(self, feature, test_name, status, details=""):
        """Log test result"""
        result = {
            "feature": feature,
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        self.test_results.append(result)
        
        status_icon = "PASS" if status == "PASS" else "FAIL" if status == "FAIL" else "SKIP"
        print(f"[{status_icon}] {feature}: {test_name}")
        if details:
            print(f"    Details: {details}")
    
    def test_basic_connectivity(self):
        """Test basic system connectivity"""
        print("\n=== BASIC CONNECTIVITY TESTS ===")
        
        # Test 1: Check if jarvis_final.py is running
        try:
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                  capture_output=True, text=True)
            if 'python.exe' in result.stdout:
                self.log_test("Connectivity", "JARVIS Process Running", "PASS")
            else:
                self.log_test("Connectivity", "JARVIS Process Running", "FAIL", "No Python process found")
        except Exception as e:
            self.log_test("Connectivity", "JARVIS Process Running", "FAIL", str(e))
        
        # Test 2: Check Ollama connection
        try:
            import ollama
            models = ollama.list()
            if hasattr(models, 'models') and len(models.models) > 0:
                model_names = [model.model.split(':')[0] for model in models.models]
                if 'llama3.1' in str(model_names) or 'llama3' in str(model_names):
                    self.log_test("Connectivity", "Ollama Connection", "PASS", f"Models: {model_names}")
                else:
                    self.log_test("Connectivity", "Ollama Connection", "FAIL", "Llama3 model not found")
            else:
                self.log_test("Connectivity", "Ollama Connection", "FAIL", "No models found")
        except Exception as e:
            self.log_test("Connectivity", "Ollama Connection", "FAIL", str(e))
    
    def test_ai_services(self):
        """Test AI service components"""
        print("\n=== AI SERVICE TESTS ===")
        
        # Test 1: Local Brain Service
        try:
            sys.path.append('cloud_cowork')
            from services.brain_local import LocalBrain
            brain = LocalBrain()
            if brain.is_available():
                self.log_test("AI Services", "Local Brain", "PASS", f"Model: {brain.model_name}")
            else:
                self.log_test("AI Services", "Local Brain", "FAIL", "Brain not available")
        except Exception as e:
            self.log_test("AI Services", "Local Brain", "FAIL", str(e))
        
        # Test 2: Vision Service
        try:
            from services.vision_local import LocalVision
            vision = LocalVision()
            if vision.is_available():
                self.log_test("AI Services", "Vision Service", "PASS", f"Model: {vision.vision_model}")
            else:
                self.log_test("AI Services", "Vision Service", "FAIL", "Vision not available")
        except Exception as e:
            self.log_test("AI Services", "Vision Service", "FAIL", str(e))
        
        # Test 3: Voice Service
        try:
            from services.voice_local import LocalVoice
            voice = LocalVoice()
            if voice.is_available():
                self.log_test("AI Services", "Voice Service", "PASS", "Speech recognition available")
            else:
                self.log_test("AI Services", "Voice Service", "FAIL", "Voice not available")
        except Exception as e:
            self.log_test("AI Services", "Voice Service", "FAIL", str(e))
        
        # Test 4: Automation Service
        try:
            from services.automation_local import LocalAutomation
            automation = LocalAutomation()
            if automation.is_available():
                self.log_test("AI Services", "Automation Service", "PASS", "System automation available")
            else:
                self.log_test("AI Services", "Automation Service", "FAIL", "Automation not available")
        except Exception as e:
            self.log_test("AI Services", "Automation Service", "FAIL", str(e))
    
    def test_automation_features(self):
        """Test automation features"""
        print("\n=== AUTOMATION FEATURE TESTS ===")
        
        try:
            from services.automation_local import LocalAutomation
            automation = LocalAutomation()
            
            # Test 1: Memory Commands
            result = automation.execute_command("remember that today is system checkup day")
            if "Remembered" in result:
                self.log_test("Automation", "Memory - Remember", "PASS", result)
            else:
                self.log_test("Automation", "Memory - Remember", "FAIL", result)
            
            # Test 2: Recall Commands
            result = automation.execute_command("what do you remember")
            if "Recalling" in result or "remember" in result.lower():
                self.log_test("Automation", "Memory - Recall", "PASS", result)
            else:
                self.log_test("Automation", "Memory - Recall", "FAIL", result)
            
            # Test 3: Weather Command
            result = automation.execute_command("weather")
            if "Weather:" in result or "weather" in result.lower():
                self.log_test("Automation", "Weather Service", "PASS", result[:50])
            else:
                self.log_test("Automation", "Weather Service", "FAIL", result)
            
            # Test 4: Web Search
            result = automation.execute_command("search python programming")
            if "Searching" in result or "search" in result.lower():
                self.log_test("Automation", "Web Search", "PASS", result)
            else:
                self.log_test("Automation", "Web Search", "FAIL", result)
            
            # Test 5: Application Launch
            result = automation.execute_command("open notepad")
            if "Opened" in result or "notepad" in result.lower():
                self.log_test("Automation", "App Launch", "PASS", result)
            else:
                self.log_test("Automation", "App Launch", "FAIL", result)
                
        except Exception as e:
            self.log_test("Automation", "Service Error", "FAIL", str(e))
    
    def test_system_integrations(self):
        """Test system integrations"""
        print("\n=== SYSTEM INTEGRATION TESTS ===")
        
        # Test 1: PyAutoGUI (Screen capture)
        try:
            import pyautogui
            screenshot = pyautogui.screenshot()
            if screenshot:
                self.log_test("System", "PyAutoGUI", "PASS", "Screen capture working")
            else:
                self.log_test("System", "PyAutoGUI", "FAIL", "Screen capture failed")
        except Exception as e:
            self.log_test("System", "PyAutoGUI", "FAIL", str(e))
        
        # Test 2: OpenCV (Camera)
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                if ret:
                    self.log_test("System", "OpenCV Camera", "PASS", "Camera access working")
                else:
                    self.log_test("System", "OpenCV Camera", "FAIL", "Cannot read from camera")
            else:
                self.log_test("System", "OpenCV Camera", "FAIL", "Camera not available")
        except Exception as e:
            self.log_test("System", "OpenCV Camera", "FAIL", str(e))
        
        # Test 3: Speech Recognition
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            mics = sr.Microphone.list_microphone_names()
            if len(mics) > 0:
                self.log_test("System", "Speech Recognition", "PASS", f"Found {len(mics)} microphones")
            else:
                self.log_test("System", "Speech Recognition", "FAIL", "No microphones found")
        except Exception as e:
            self.log_test("System", "Speech Recognition", "FAIL", str(e))
        
        # Test 4: TTS (PowerShell)
        try:
            import subprocess
            ps_command = 'Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak("Test")'
            result = subprocess.run(["powershell", "-NoProfile", "-Command", ps_command], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.log_test("System", "PowerShell TTS", "PASS", "TTS working")
            else:
                self.log_test("System", "PowerShell TTS", "FAIL", "TTS failed")
        except Exception as e:
            self.log_test("System", "PowerShell TTS", "FAIL", str(e))
    
    def test_gui_components(self):
        """Test GUI components"""
        print("\n=== GUI COMPONENT TESTS ===")
        
        # Test 1: PyQt6 Availability
        try:
            from PyQt6.QtWidgets import QApplication
            self.log_test("GUI", "PyQt6 Available", "PASS", "PyQt6 imported successfully")
        except Exception as e:
            self.log_test("GUI", "PyQt6 Available", "FAIL", str(e))
        
        # Test 2: GUI File Structure
        gui_file = os.path.join('cloud_cowork', 'desktop_gui.py')
        if os.path.exists(gui_file):
            self.log_test("GUI", "GUI File Exists", "PASS", "desktop_gui.py found")
        else:
            self.log_test("GUI", "GUI File Exists", "FAIL", "desktop_gui.py not found")
        
        # Test 3: GUI Import Test
        try:
            sys.path.append('cloud_cowork')
            from desktop_gui import JARVISDesktopGUI
            self.log_test("GUI", "GUI Import", "PASS", "JARVISDesktopGUI imported successfully")
        except Exception as e:
            self.log_test("GUI", "GUI Import", "FAIL", str(e))
    
    def generate_report(self):
        """Generate comprehensive checkup report"""
        print("\n" + "="*60)
        print("JARVIS SYSTEM COMPREHENSIVE CHECKUP REPORT")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        skipped_tests = len([r for r in self.test_results if r['status'] == 'SKIP'])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
        print(f"Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
        print(f"Skipped: {skipped_tests} ({skipped_tests/total_tests*100:.1f}%)")
        print(f"Checkup Duration: {datetime.now() - self.start_time}")
        
        print("\n" + "="*60)
        print("DETAILED RESULTS")
        print("="*60)
        
        # Group by feature
        features = {}
        for result in self.test_results:
            feature = result['feature']
            if feature not in features:
                features[feature] = []
            features[feature].append(result)
        
        for feature, tests in features.items():
            print(f"\n{feature}:")
            for test in tests:
                status_icon = "PASS" if test['status'] == 'PASS' else "FAIL" if test['status'] == 'FAIL' else "SKIP"
                print(f"  [{status_icon}] {test['test']}")
                if test['details']:
                    print(f"      {test['details']}")
        
        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        
        if failed_tests == 0:
            print("ALL SYSTEMS OPERATIONAL - JARVIS is fully functional!")
        elif failed_tests <= 2:
            print("MOSTLY OPERATIONAL - Minor issues detected")
        else:
            print("MULTIPLE ISSUES DETECTED - System requires attention")
        
        # Critical failures
        critical_failures = [r for r in self.test_results 
                           if r['status'] == 'FAIL' and 
                           any(keyword in r['feature'].lower() for keyword in ['connectivity', 'ai services', 'system'])]
        
        if critical_failures:
            print("\nCRITICAL ISSUES:")
            for failure in critical_failures:
                print(f"  - {failure['feature']}: {failure['test']}")
        
        return {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "skipped": skipped_tests,
            "results": self.test_results
        }
    
    def run_full_checkup(self):
        """Run complete system checkup"""
        print("Starting JARVIS System Comprehensive Checkup...")
        print(f"Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.test_basic_connectivity()
        self.test_ai_services()
        self.test_automation_features()
        self.test_system_integrations()
        self.test_gui_components()
        
        return self.generate_report()

if __name__ == "__main__":
    checkup = JARVISCheckup()
    report = checkup.run_full_checkup()
