#!/usr/bin/env python3
"""
JARVIS Connection Checker
Validates all external service connections on startup
"""

import os
import sys
import time
import requests
from datetime import datetime
from typing import Dict, Any, List, Tuple

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

class ConnectionChecker:
    """Checks all JARVIS external connections on startup"""
    
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = []
        self.errors = []
        
    def check_connections(self) -> Dict[str, Any]:
        """Main connection check function"""
        print("=" * 80)
        print("JARVIS CONNECTION CHECKER - Startup Validation")
        print("=" * 80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'summary': {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'warnings': 0
            }
        }
        
        # Check 1: Google APIs (Drive & Calendar)
        google_result = self.check_google_apis()
        results['checks']['google_apis'] = google_result
        
        # Check 2: Ollama (Local AI)
        ollama_result = self.check_ollama()
        results['checks']['ollama'] = ollama_result
        
        # Check 3: Internet Connection
        internet_result = self.check_internet()
        results['checks']['internet'] = internet_result
        
        # Check 4: Microphone (Voice Recognition)
        mic_result = self.check_microphone()
        results['checks']['microphone'] = mic_result
        
        # Check 5: Camera (Vision)
        camera_result = self.check_camera()
        results['checks']['camera'] = camera_result
        
        # Check 6: Text-to-Speech
        tts_result = self.check_tts()
        results['checks']['tts'] = tts_result
        
        # Calculate summary
        for check_name, check_result in results['checks'].items():
            results['summary']['total'] += 1
            if check_result['status'] == 'PASS':
                results['summary']['passed'] += 1
            elif check_result['status'] == 'FAIL':
                results['summary']['failed'] += 1
            elif check_result['status'] == 'WARN':
                results['summary']['warnings'] += 1
        
        # Print summary
        self._print_summary(results)
        
        return results
    
    def check_google_apis(self) -> Dict[str, Any]:
        """Check Google API connections (Drive & Calendar)"""
        print("Checking Google API connections...")
        
        result = {
            'service': 'Google APIs (Drive & Calendar)',
            'status': 'PASS',
            'message': '',
            'details': {}
        }
        
        try:
            # Check if credentials.json exists (use absolute path from script location)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            creds_path = os.path.join(script_dir, 'credentials.json')
            if not os.path.exists(creds_path):
                result['status'] = 'FAIL'
                result['message'] = f'credentials.json not found at {creds_path}'
                self.errors.append(result['message'])
                return result
            
            # Try to authenticate with Google
            from cloud_sync_service import CloudSyncService
            cloud_service = CloudSyncService()
            
            if cloud_service.is_active:
                result['message'] = 'Google Drive and Calendar services connected'
                result['details']['drive'] = 'Connected'
                result['details']['calendar'] = 'Connected'
                print("  Google Drive: Connected")
                print("  Google Calendar: Connected")
            else:
                result['status'] = 'FAIL'
                result['message'] = 'Google authentication failed - check credentials.json'
                self.errors.append(result['message'])
                print("  Google Drive: FAILED")
                print("  Google Calendar: FAILED")
                print("  ERROR: Invalid Google credentials detected!")
                print("  ACTION: Please verify your Google Cloud Desktop App credentials")
                
        except Exception as e:
            result['status'] = 'FAIL'
            result['message'] = f'Google API check failed: {str(e)}'
            self.errors.append(result['message'])
            print(f"  ERROR: {str(e)}")
        
        return result
    
    def check_ollama(self) -> Dict[str, Any]:
        """Check Ollama local AI service"""
        print("Checking Ollama local AI...")
        
        result = {
            'service': 'Ollama (Local AI)',
            'status': 'PASS',
            'message': '',
            'details': {}
        }
        
        try:
            import ollama
            models = ollama.list()
            
            # Properly check for models in the response object
            if hasattr(models, 'models') and len(models.models) > 0:
                model_names = [m.model for m in models.models]
                result['message'] = f'Found {len(models.models)} models'
                result['details']['models'] = model_names
                print(f"  Models available: {len(models.models)}")
                for model in model_names[:5]:
                    print(f"    - {model}")
            else:
                result['status'] = 'WARN'
                result['message'] = 'Ollama running but no models found'
                self.warnings.append(result['message'])
                print("  WARNING: Ollama running but no models found")
                
        except Exception as e:
            result['status'] = 'FAIL'
            result['message'] = f'Ollama not available: {str(e)}'
            self.errors.append(result['message'])
            print(f"  ERROR: {str(e)}")
        
        return result
    
    def check_internet(self) -> Dict[str, Any]:
        """Check internet connection"""
        print("Checking internet connection...")
        
        result = {
            'service': 'Internet Connection',
            'status': 'PASS',
            'message': '',
            'details': {}
        }
        
        try:
            # Test connection to Google
            response = requests.get('https://www.google.com', timeout=5)
            if response.status_code == 200:
                result['message'] = 'Internet connection working'
                result['details']['google'] = 'Connected'
                print("  Google: Connected")
            else:
                result['status'] = 'WARN'
                result['message'] = f'Internet response code: {response.status_code}'
                self.warnings.append(result['message'])
                print(f"  WARNING: Response code {response.status_code}")
                
        except requests.exceptions.Timeout:
            result['status'] = 'FAIL'
            result['message'] = 'Internet connection timeout'
            self.errors.append(result['message'])
            print("  ERROR: Connection timeout")
        except Exception as e:
            result['status'] = 'FAIL'
            result['message'] = f'Internet connection failed: {str(e)}'
            self.errors.append(result['message'])
            print(f"  ERROR: {str(e)}")
        
        return result
    
    def check_microphone(self) -> Dict[str, Any]:
        """Check microphone availability"""
        print("Checking microphone...")
        
        result = {
            'service': 'Microphone (Voice Recognition)',
            'status': 'PASS',
            'message': '',
            'details': {}
        }
        
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            mics = sr.Microphone.list_microphone_names()
            
            if len(mics) > 0:
                result['message'] = f'Found {len(mics)} microphones'
                result['details']['microphones'] = len(mics)
                print(f"  Microphones found: {len(mics)}")
                for i, mic in enumerate(mics[:3]):
                    print(f"    {i}: {mic}")
            else:
                result['status'] = 'WARN'
                result['message'] = 'No microphones found'
                self.warnings.append(result['message'])
                print("  WARNING: No microphones found")
                
        except Exception as e:
            result['status'] = 'FAIL'
            result['message'] = f'Microphone check failed: {str(e)}'
            self.errors.append(result['message'])
            print(f"  ERROR: {str(e)}")
        
        return result
    
    def check_camera(self) -> Dict[str, Any]:
        """Check camera availability"""
        print("Checking camera...")
        
        result = {
            'service': 'Camera (Vision)',
            'status': 'PASS',
            'message': '',
            'details': {}
        }
        
        try:
            import cv2
            
            # Try to access default camera
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                result['message'] = 'Camera available'
                result['details']['camera'] = 'Available'
                print("  Camera: Available")
                cap.release()
            else:
                result['status'] = 'WARN'
                result['message'] = 'Camera not accessible'
                self.warnings.append(result['message'])
                print("  WARNING: Camera not accessible")
                
        except Exception as e:
            result['status'] = 'FAIL'
            result['message'] = f'Camera check failed: {str(e)}'
            self.errors.append(result['message'])
            print(f"  ERROR: {str(e)}")
        
        return result
    
    def check_tts(self) -> Dict[str, Any]:
        """Check text-to-speech"""
        print("Checking text-to-speech...")
        
        result = {
            'service': 'Text-to-Speech',
            'status': 'PASS',
            'message': '',
            'details': {}
        }
        
        try:
            import pyttsx3
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            
            if len(voices) > 0:
                result['message'] = f'Found {len(voices)} TTS voices'
                result['details']['voices'] = len(voices)
                print(f"  TTS voices: {len(voices)}")
                for i, voice in enumerate(voices[:2]):
                    print(f"    {i}: {voice.name}")
            else:
                result['status'] = 'WARN'
                result['message'] = 'No TTS voices found'
                self.warnings.append(result['message'])
                print("  WARNING: No TTS voices found")
                
        except Exception as e:
            result['status'] = 'FAIL'
            result['message'] = f'TTS check failed: {str(e)}'
            self.errors.append(result['message'])
            print(f"  ERROR: {str(e)}")
        
        return result
    
    def _print_summary(self, results: Dict[str, Any]):
        """Print connection check summary"""
        print()
        print("=" * 80)
        print("CONNECTION CHECK SUMMARY")
        print("=" * 80)
        
        summary = results['summary']
        print(f"Total Checks: {summary['total']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Warnings: {summary['warnings']}")
        
        # Print critical errors first
        if self.errors:
            print("\nCRITICAL ERRORS:")
            for error in self.errors:
                print(f"  ERROR: {error}")
        
        # Print warnings
        if self.warnings:
            print("\nWARNINGS:")
            for warning in self.warnings:
                print(f"  WARNING: {warning}")
        
        # Overall status
        print()
        if summary['failed'] > 0:
            print("OVERALL STATUS: FAILED - Fix critical errors before using JARVIS")
        elif summary['warnings'] > 0:
            print("OVERALL STATUS: WARNING - Some features may not work properly")
        else:
            print("OVERALL STATUS: GOOD - All systems ready")
        
        print("=" * 80)

def check_connections():
    """Main function to check all connections"""
    checker = ConnectionChecker()
    return checker.check_connections()

if __name__ == '__main__':
    # Run connection check
    results = check_connections()
    
    # Exit with appropriate code
    if results['summary']['failed'] > 0:
        sys.exit(1)
    elif results['summary']['warnings'] > 0:
        sys.exit(2)
    else:
        sys.exit(0)
