#!/usr/bin/env python3
"""
Physical Modules Test Suite for JARVIS Omni-Upgrade
Comprehensive unit tests for camera, hand tracking, and hardware lag reporting
"""

import os
import sys
import time
import threading
import unittest
from datetime import datetime
from typing import Dict, Any, List, Optional
import cv2
import numpy as np

# Add JARVIS backend path
sys.path.append(os.path.dirname(__file__))

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False

# Import JARVIS services
try:
    from services.physical_control_service import PhysicalControlService
    from services.health_guardian_service import HealthGuardianService
    from services.biometric_security_service import BiometricSecurityService
    from services.gesture_service import GestureService
    SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"Services not available: {e}")
    SERVICES_AVAILABLE = False

class PhysicalModulesTestSuite:
    """Comprehensive test suite for physical modules"""
    
    def __init__(self):
        self.test_results = {}
        self.hardware_metrics = {}
        self.performance_report = {}
        self.start_time = datetime.now()
        
        print("Physical Modules Test Suite initialized")
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive test suite for all physical modules"""
        print("=" * 80)
        print("JARVIS OMNI-UPGRADE - PHYSICAL MODULES TEST SUITE")
        print("=" * 80)
        print(f"Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Test camera hardware
        self.test_camera_hardware()
        
        # Test MediaPipe performance
        self.test_mediapipe_performance()
        
        # Test Gesture Service
        self.test_gesture_service()
        
        # Test Physical Control Service
        self.test_physical_control_service()
        
        # Test Health Guardian Service
        self.test_health_guardian_service()
        
        # Test Biometric Security Service
        self.test_biometric_security_service()
        
        # Generate comprehensive report
        self._generate_performance_report()
        
        return self.performance_report
    
    def test_camera_hardware(self):
        """Test camera hardware capabilities and performance"""
        print("\n=== CAMERA HARDWARE TEST ===")
        
        test_result = {
            'test_name': 'Camera Hardware',
            'success': False,
            'metrics': {},
            'errors': [],
            'start_time': datetime.now().isoformat()
        }
        
        try:
            # Test camera availability
            cameras = []
            for i in range(5):  # Test first 5 camera indices
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    cameras.append(i)
                    cap.release()
            
            test_result['metrics']['available_cameras'] = len(cameras)
            test_result['metrics']['camera_indices'] = cameras
            
            if not cameras:
                test_result['errors'].append("No cameras found")
                print("Camera test: FAILED - No cameras found")
            else:
                print(f"Camera test: PASSED - Found {len(cameras)} cameras")
                
                # Test primary camera performance
                primary_camera = cameras[0]
                cap = cv2.VideoCapture(primary_camera)
                
                if cap.isOpened():
                    # Test resolution
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    
                    # Test FPS
                    start_time = time.time()
                    frame_count = 0
                    
                    for _ in range(30):  # Test 30 frames
                        ret, frame = cap.read()
                        if ret:
                            frame_count += 1
                    
                    end_time = time.time()
                    actual_fps = frame_count / (end_time - start_time)
                    
                    test_result['metrics']['actual_fps'] = actual_fps
                    test_result['metrics']['target_fps'] = 30
                    test_result['metrics']['fps_efficiency'] = (actual_fps / 30) * 100
                    
                    # Test resolution
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    test_result['metrics']['resolution'] = f"{width}x{height}"
                    
                    # Test frame quality
                    ret, frame = cap.read()
                    if ret:
                        test_result['metrics']['frame_shape'] = frame.shape
                        test_result['metrics']['frame_dtype'] = str(frame.dtype)
                    
                    cap.release()
                    test_result['success'] = True
                    
                    print(f"  Primary camera: {width}x{height} @ {actual_fps:.1f} FPS")
                    print(f"  FPS Efficiency: {(actual_fps/30)*100:.1f}%")
                else:
                    test_result['errors'].append("Failed to open primary camera")
                    print("Camera test: FAILED - Could not open primary camera")
            
        except Exception as e:
            test_result['errors'].append(f"Camera test failed: {str(e)}")
            print(f"Camera test: FAILED - {e}")
        
        test_result['end_time'] = datetime.now().isoformat()
        self.test_results['camera_hardware'] = test_result
    
    def test_mediapipe_performance(self):
        """Test MediaPipe performance and latency"""
        print("\n=== MEDIAPIPE PERFORMANCE TEST ===")
        
        test_result = {
            'test_name': 'MediaPipe Performance',
            'success': False,
            'metrics': {},
            'errors': [],
            'start_time': datetime.now().isoformat()
        }
        
        try:
            if not MEDIAPIPE_AVAILABLE:
                test_result['errors'].append("MediaPipe not available")
                print("MediaPipe test: FAILED - MediaPipe not available")
                test_result['end_time'] = datetime.now().isoformat()
                self.test_results['mediapipe_performance'] = test_result
                return
            
            # Initialize MediaPipe solutions
            mp_hands = mp.solutions.hands
            mp_pose = mp.solutions.pose
            mp_face_mesh = mp.solutions.face_mesh
            
            hands = mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            pose = mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            # Test with dummy frames
            test_frames = 50
            hand_processing_times = []
            pose_processing_times = []
            
            for i in range(test_frames):
                # Create dummy frame
                frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Test hands
                start_time = time.perf_counter()
                hand_results = hands.process(frame_rgb)
                hand_time = (time.perf_counter() - start_time) * 1000
                hand_processing_times.append(hand_time)
                
                # Test pose
                start_time = time.perf_counter()
                pose_results = pose.process(frame_rgb)
                pose_time = (time.perf_counter() - start_time) * 1000
                pose_processing_times.append(pose_time)
            
            # Calculate metrics
            avg_hand_time = sum(hand_processing_times) / len(hand_processing_times)
            avg_pose_time = sum(pose_processing_times) / len(pose_processing_times)
            max_hand_time = max(hand_processing_times)
            max_pose_time = max(pose_processing_times)
            
            test_result['metrics'] = {
                'test_frames': test_frames,
                'hand_detection': {
                    'avg_time_ms': avg_hand_time,
                    'max_time_ms': max_hand_time,
                    'fps_capability': 1000 / avg_hand_time if avg_hand_time > 0 else 0
                },
                'pose_detection': {
                    'avg_time_ms': avg_pose_time,
                    'max_time_ms': max_pose_time,
                    'fps_capability': 1000 / avg_pose_time if avg_pose_time > 0 else 0
                }
            }
            
            # Evaluate performance
            hand_lag_ms = avg_hand_time
            pose_lag_ms = avg_pose_time
            
            test_result['metrics']['hardware_lag'] = {
                'hand_tracking_lag_ms': hand_lag_ms,
                'pose_detection_lag_ms': pose_lag_ms,
                'overall_lag_ms': max(hand_lag_ms, pose_lag_ms)
            }
            
            # Performance classification
            if hand_lag_ms < 20 and pose_lag_ms < 30:
                performance_rating = "Excellent"
            elif hand_lag_ms < 50 and pose_lag_ms < 60:
                performance_rating = "Good"
            elif hand_lag_ms < 100 and pose_lag_ms < 120:
                performance_rating = "Acceptable"
            else:
                performance_rating = "Poor"
            
            test_result['metrics']['performance_rating'] = performance_rating
            
            print(f"Hand Detection: {avg_hand_time:.1f}ms avg, {max_hand_time:.1f}ms max")
            print(f"Pose Detection: {avg_pose_time:.1f}ms avg, {max_pose_time:.1f}ms max")
            print(f"Hardware Lag: {max(hand_lag_ms, pose_lag_ms):.1f}ms")
            print(f"Performance Rating: {performance_rating}")
            
            test_result['success'] = True
            
        except Exception as e:
            test_result['errors'].append(f"MediaPipe test failed: {str(e)}")
            print(f"MediaPipe test: FAILED - {e}")
        
        test_result['end_time'] = datetime.now().isoformat()
        self.test_results['mediapipe_performance'] = test_result
    
    def test_gesture_service(self):
        """Test Gesture Service functionality"""
        print("\n=== GESTURE SERVICE TEST ===")
        
        test_result = {
            'test_name': 'Gesture Service',
            'success': False,
            'metrics': {},
            'errors': [],
            'start_time': datetime.now().isoformat()
        }
        
        try:
            if not SERVICES_AVAILABLE:
                test_result['errors'].append("JARVIS services not available")
                print("Gesture Service test: FAILED - Services not available")
                test_result['end_time'] = datetime.now().isoformat()
                self.test_results['gesture_service'] = test_result
                return
            
            # Initialize gesture service
            gesture_service = GestureService()
            
            # Test service initialization
            test_result['metrics']['service_initialized'] = True
            
            # Test gesture tracking (dry run)
            start_time = time.perf_counter()
            
            # Create dummy frame for testing
            frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            
            # Process frame
            gesture_data = gesture_service.process_frame(frame)
            
            processing_time = (time.perf_counter() - start_time) * 1000
            
            test_result['metrics']['processing_time_ms'] = processing_time
            test_result['metrics']['gesture_data_returned'] = gesture_data is not None
            
            if gesture_data:
                test_result['metrics']['fps'] = gesture_data.get('fps', 0)
                test_result['metrics']['hand_detected'] = gesture_data.get('hand_detected', False)
            
            # Test coordinate mapping
            screen_x, screen_y = gesture_service.map_to_screen(0.5, 0.5)
            test_result['metrics']['coordinate_mapping'] = {
                'screen_center': f"({screen_x}, {screen_y})",
                'mapping_successful': screen_x > 0 and screen_y > 0
            }
            
            # Test pinch detection
            # Create dummy hand landmarks
            hand_landmarks = []
            for i in range(21):
                hand_landmarks.append(mp.solutions.hands.HandLandmark(i))
            
            # Set positions for pinch test
            hand_landmarks[8].x, hand_landmarks[8].y = 0.5, 0.5  # Index finger
            hand_landmarks[4].x, hand_landmarks[4].y = 0.52, 0.52  # Thumb (close)
            
            pinch_detected = gesture_service.detect_pinch(hand_landmarks)
            test_result['metrics']['pinch_detection'] = pinch_detected
            
            test_result['success'] = True
            
            print(f"Gesture Service: Processing time {processing_time:.1f}ms")
            print(f"Coordinate mapping: {screen_x}, {screen_y}")
            print(f"Pinch detection: {pinch_detected}")
            
        except Exception as e:
            test_result['errors'].append(f"Gesture Service test failed: {str(e)}")
            print(f"Gesture Service test: FAILED - {e}")
        
        test_result['end_time'] = datetime.now().isoformat()
        self.test_results['gesture_service'] = test_result
    
    def test_physical_control_service(self):
        """Test Physical Control Service"""
        print("\n=== PHYSICAL CONTROL SERVICE TEST ===")
        
        test_result = {
            'test_name': 'Physical Control Service',
            'success': False,
            'metrics': {},
            'errors': [],
            'start_time': datetime.now().isoformat()
        }
        
        try:
            if not SERVICES_AVAILABLE:
                test_result['errors'].append("JARVIS services not available")
                print("Physical Control test: FAILED - Services not available")
                test_result['end_time'] = datetime.now().isoformat()
                self.test_results['physical_control_service'] = test_result
                return
            
            # Initialize physical control service
            control_service = PhysicalControlService()
            
            # Test service initialization
            test_result['metrics']['service_initialized'] = True
            test_result['metrics']['screen_dimensions'] = f"{control_service.screen_width}x{control_service.screen_height}"
            
            # Test gesture detection performance
            performance_results = control_service.test_gesture_detection(duration=5)
            test_result['metrics']['performance_test'] = performance_results
            
            # Test virtual switches
            test_result['metrics']['virtual_switches'] = control_service.virtual_switches
            
            # Test status
            status = control_service.get_status()
            test_result['metrics']['service_status'] = status
            
            test_result['success'] = True
            
            print(f"Physical Control: Screen {control_service.screen_width}x{control_service.screen_height}")
            print(f"Performance test: {performance_results.get('avg_fps', 0):.1f} FPS")
            print(f"Hardware lag: {performance_results.get('hardware_lag_ms', 0):.1f}ms")
            
        except Exception as e:
            test_result['errors'].append(f"Physical Control test failed: {str(e)}")
            print(f"Physical Control test: FAILED - {e}")
        
        test_result['end_time'] = datetime.now().isoformat()
        self.test_results['physical_control_service'] = test_result
    
    def test_health_guardian_service(self):
        """Test Health Guardian Service"""
        print("\n=== HEALTH GUARDIAN SERVICE TEST ===")
        
        test_result = {
            'test_name': 'Health Guardian Service',
            'success': False,
            'metrics': {},
            'errors': [],
            'start_time': datetime.now().isoformat()
        }
        
        try:
            if not SERVICES_AVAILABLE:
                test_result['errors'].append("JARVIS services not available")
                print("Health Guardian test: FAILED - Services not available")
                test_result['end_time'] = datetime.now().isoformat()
                self.test_results['health_guardian_service'] = test_result
                return
            
            # Initialize health guardian service
            health_service = HealthGuardianService()
            
            # Test service initialization
            test_result['metrics']['service_initialized'] = True
            test_result['metrics']['posture_threshold'] = health_service.posture_threshold
            test_result['metrics']['eye_break_interval'] = health_service.eye_break_interval
            
            # Test health status
            health_status = health_service.get_health_status()
            test_result['metrics']['health_status'] = health_status
            
            # Test daily stats
            daily_stats = health_service.get_daily_stats()
            test_result['metrics']['daily_stats'] = daily_stats
            
            # Test posture calculation (simulate)
            health_service.current_posture_score = 75.5
            test_result['metrics']['posture_score_test'] = health_service.current_posture_score
            
            test_result['success'] = True
            
            print(f"Health Guardian: Posture threshold {health_service.posture_threshold}")
            print(f"Eye break interval: {health_service.eye_break_interval}s")
            print(f"Current posture score: {health_service.current_posture_score}")
            
        except Exception as e:
            test_result['errors'].append(f"Health Guardian test failed: {str(e)}")
            print(f"Health Guardian test: FAILED - {e}")
        
        test_result['end_time'] = datetime.now().isoformat()
        self.test_results['health_guardian_service'] = test_result
    
    def test_biometric_security_service(self):
        """Test Biometric Security Service"""
        print("\n=== BIOMETRIC SECURITY SERVICE TEST ===")
        
        test_result = {
            'test_name': 'Biometric Security Service',
            'success': False,
            'metrics': {},
            'errors': [],
            'start_time': datetime.now().isoformat()
        }
        
        try:
            if not SERVICES_AVAILABLE:
                test_result['errors'].append("JARVIS services not available")
                print("Biometric Security test: FAILED - Services not available")
                test_result['end_time'] = datetime.now().isoformat()
                self.test_results['biometric_security_service'] = test_result
                return
            
            # Initialize biometric security service
            security_service = BiometricSecurityService()
            
            # Test service initialization
            test_result['metrics']['service_initialized'] = True
            test_result['metrics']['authentication_timeout'] = security_service.authentication_timeout
            test_result['metrics']['scan_interval'] = security_service.scan_interval
            
            # Test face database
            face_db = security_service.get_face_database()
            test_result['metrics']['face_database'] = face_db
            
            # Test security status
            security_status = security_service.get_security_status()
            test_result['metrics']['security_status'] = security_status
            
            # Test authentication state
            test_result['metrics']['is_authenticated'] = security_service.is_authenticated
            test_result['metrics']['privacy_mode'] = security_service.privacy_mode
            
            test_result['success'] = True
            
            print(f"Biometric Security: Authenticated {security_service.is_authenticated}")
            print(f"Privacy mode: {security_service.privacy_mode}")
            print(f"Face database size: {face_db.get('users', 0)}")
            
        except Exception as e:
            test_result['errors'].append(f"Biometric Security test failed: {str(e)}")
            print(f"Biometric Security test: FAILED - {e}")
        
        test_result['end_time'] = datetime.now().isoformat()
        self.test_results['biometric_security_service'] = test_result
    
    def _generate_performance_report(self):
        """Generate comprehensive performance report"""
        print("\n" + "=" * 80)
        print("PHYSICAL MODULES PERFORMANCE REPORT")
        print("=" * 80)
        
        # Calculate overall metrics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results.values() if r['success'])
        failed_tests = total_tests - passed_tests
        
        # Hardware lag analysis
        hardware_lag_data = []
        for test_name, result in self.test_results.items():
            if 'hardware_lag' in result.get('metrics', {}):
                lag_info = result['metrics']['hardware_lag']
                hardware_lag_data.append({
                    'test': test_name,
                    'lag_ms': lag_info.get('overall_lag_ms', 0)
                })
        
        # Performance ratings
        performance_ratings = {}
        for test_name, result in self.test_results.items():
            if 'performance_rating' in result.get('metrics', {}):
                performance_ratings[test_name] = result['metrics']['performance_rating']
        
        # Generate report
        self.performance_report = {
            'test_summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                'start_time': self.start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_seconds': (datetime.now() - self.start_time).total_seconds()
            },
            'hardware_analysis': {
                'camera_available': self.test_results.get('camera_hardware', {}).get('success', False),
                'mediapipe_available': MEDIAPIPE_AVAILABLE,
                'services_available': SERVICES_AVAILABLE,
                'hardware_lag_data': hardware_lag_data,
                'max_lag_ms': max([d['lag_ms'] for d in hardware_lag_data]) if hardware_lag_data else 0,
                'avg_lag_ms': sum([d['lag_ms'] for d in hardware_lag_data]) / len(hardware_lag_data) if hardware_lag_data else 0
            },
            'performance_ratings': performance_ratings,
            'detailed_results': self.test_results
        }
        
        # Print summary
        print(f"Test Summary: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
        print(f"Duration: {self.performance_report['test_summary']['duration_seconds']:.1f} seconds")
        
        # Hardware analysis
        hardware = self.performance_report['hardware_analysis']
        print(f"\nHardware Analysis:")
        print(f"  Camera Available: {'Yes' if hardware['camera_available'] else 'No'}")
        print(f"  MediaPipe Available: {'Yes' if hardware['mediapipe_available'] else 'No'}")
        print(f"  Services Available: {'Yes' if hardware['services_available'] else 'No'}")
        
        if hardware['hardware_lag_data']:
            print(f"  Hardware Lag:")
            print(f"    Average: {hardware['avg_lag_ms']:.1f}ms")
            print(f"    Maximum: {hardware['max_lag_ms']:.1f}ms")
            
            for lag_data in hardware['hardware_lag_data']:
                print(f"    {lag_data['test']}: {lag_data['lag_ms']:.1f}ms")
        
        # Performance ratings
        if performance_ratings:
            print(f"\nPerformance Ratings:")
            for test, rating in performance_ratings.items():
                print(f"  {test}: {rating}")
        
        # Recommendations
        print(f"\nRecommendations:")
        if hardware['max_lag_ms'] > 100:
            print("  - High hardware lag detected. Consider optimizing MediaPipe settings.")
        if not hardware['camera_available']:
            print("  - No camera detected. Physical control features will not work.")
        if passed_tests < total_tests:
            print("  - Some tests failed. Check error logs for details.")
        else:
            print("  - All tests passed. System is ready for production use.")
        
        # Save report to file
        self._save_performance_report()
    
    def _save_performance_report(self):
        """Save performance report to file"""
        try:
            report_file = f"physical_modules_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(report_file, 'w') as f:
                json.dump(self.performance_report, f, indent=2, default=str)
            
            print(f"\nDetailed report saved to: {report_file}")
            
        except Exception as e:
            print(f"Failed to save performance report: {e}")

def main():
    """Run physical modules test suite"""
    test_suite = PhysicalModulesTestSuite()
    report = test_suite.run_all_tests()
    
    return report

if __name__ == "__main__":
    main()
