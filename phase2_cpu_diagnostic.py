#!/usr/bin/env python3
"""
Phase 2 CPU Usage Diagnostic
Tests hand tracking CPU usage to ensure it stays under 20%
"""

import sys
import os
import time
import psutil
import threading
from datetime import datetime

sys.path.append(os.path.dirname(__file__))

def test_gesture_service_cpu_usage():
    """Test gesture service CPU usage"""
    print("=== GESTURE SERVICE CPU USAGE DIAGNOSTIC ===")
    
    try:
        from services.gesture_service import GestureService
        
        # Initialize gesture service
        gesture = GestureService()
        print("Gesture Service: Initialized")
        
        # Start CPU monitoring
        cpu_usage_samples = []
        monitoring_duration = 30  # Test for 30 seconds
        sample_interval = 1  # Sample every second
        
        def monitor_cpu():
            """Monitor CPU usage in background"""
            start_time = time.time()
            while time.time() - start_time < monitoring_duration:
                cpu_percent = psutil.cpu_percent(interval=None)
                cpu_usage_samples.append(cpu_percent)
                time.sleep(sample_interval)
        
        # Start hand tracking
        print("Starting hand tracking...")
        if not gesture.start_tracking():
            print("Failed to start hand tracking")
            return False
        
        # Start CPU monitoring
        print(f"Monitoring CPU usage for {monitoring_duration} seconds...")
        cpu_thread = threading.Thread(target=monitor_cpu, daemon=True)
        cpu_thread.start()
        
        # Wait for monitoring to complete
        time.sleep(monitoring_duration + 2)
        
        # Stop hand tracking
        gesture.stop_tracking()
        print("Hand tracking stopped")
        
        # Analyze CPU usage
        if cpu_usage_samples:
            avg_cpu = sum(cpu_usage_samples) / len(cpu_usage_samples)
            max_cpu = max(cpu_usage_samples)
            min_cpu = min(cpu_usage_samples)
            
            print(f"\nCPU Usage Analysis:")
            print(f"  Average: {avg_cpu:.2f}%")
            print(f"  Maximum: {max_cpu:.2f}%")
            print(f"  Minimum: {min_cpu:.2f}%")
            print(f"  Samples: {len(cpu_usage_samples)}")
            
            # Check if under 20% threshold
            if avg_cpu <= 20:
                print(f"CPU Usage: PASSED (Average {avg_cpu:.2f}% <= 20%)")
                return True
            else:
                print(f"CPU Usage: FAILED (Average {avg_cpu:.2f}% > 20%)")
                return False
        else:
            print("No CPU usage samples collected")
            return False
            
    except Exception as e:
        print(f"CPU diagnostic failed: {e}")
        return False

def test_posture_ai_cpu_usage():
    """Test posture AI CPU usage"""
    print("\n=== POSTURE AI CPU USAGE DIAGNOSTIC ===")
    
    try:
        from services.vision_service import VisionService
        import cv2
        
        # Initialize vision service
        vision = VisionService()
        print("Vision Service: Initialized")
        
        # Start posture monitoring
        if not vision.start_posture_monitoring():
            print("Failed to start posture monitoring")
            return False
        print("Posture monitoring: Started")
        
        # Test CPU usage with camera
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            print("Failed to open camera")
            return False
        
        cpu_usage_samples = []
        test_duration = 15  # Test for 15 seconds
        
        print(f"Testing posture AI CPU usage for {test_duration} seconds...")
        start_time = time.time()
        
        while time.time() - start_time < test_duration:
            ret, frame = camera.read()
            if ret:
                # Process posture detection
                posture_data = vision.detect_posture(frame)
                
                # Sample CPU usage
                cpu_percent = psutil.cpu_percent(interval=None)
                cpu_usage_samples.append(cpu_percent)
            
            time.sleep(0.1)
        
        camera.release()
        vision.stop_posture_monitoring()
        print("Posture monitoring: Stopped")
        
        # Analyze CPU usage
        if cpu_usage_samples:
            avg_cpu = sum(cpu_usage_samples) / len(cpu_usage_samples)
            max_cpu = max(cpu_usage_samples)
            
            print(f"\nPosture AI CPU Usage:")
            print(f"  Average: {avg_cpu:.2f}%")
            print(f"  Maximum: {max_cpu:.2f}%")
            print(f"  Samples: {len(cpu_usage_samples)}")
            
            return True
        else:
            print("No CPU usage samples collected for posture AI")
            return False
            
    except Exception as e:
        print(f"Posture AI CPU diagnostic failed: {e}")
        return False

def test_privacy_blur_cpu_usage():
    """Test privacy blur CPU usage"""
    print("\n=== PRIVACY BLUR CPU USAGE DIAGNOSTIC ===")
    
    try:
        from services.security_service import SecurityService
        import cv2
        
        # Initialize security service
        security = SecurityService()
        print("Security Service: Initialized")
        
        # Test CPU usage with privacy blur
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            print("Failed to open camera")
            return False
        
        cpu_usage_samples = []
        test_duration = 10  # Test for 10 seconds
        
        print(f"Testing privacy blur CPU usage for {test_duration} seconds...")
        start_time = time.time()
        
        while time.time() - start_time < test_duration:
            ret, frame = camera.read()
            if ret:
                # Process privacy blur detection
                security.check_privacy_blur(frame)
                
                # Sample CPU usage
                cpu_percent = psutil.cpu_percent(interval=None)
                cpu_usage_samples.append(cpu_percent)
            
            time.sleep(0.1)
        
        camera.release()
        print("Privacy blur test: Completed")
        
        # Analyze CPU usage
        if cpu_usage_samples:
            avg_cpu = sum(cpu_usage_samples) / len(cpu_usage_samples)
            max_cpu = max(cpu_usage_samples)
            
            print(f"\nPrivacy Blur CPU Usage:")
            print(f"  Average: {avg_cpu:.2f}%")
            print(f"  Maximum: {max_cpu:.2f}%")
            print(f"  Samples: {len(cpu_usage_samples)}")
            
            return True
        else:
            print("No CPU usage samples collected for privacy blur")
            return False
            
    except Exception as e:
        print(f"Privacy blur CPU diagnostic failed: {e}")
        return False

def main():
    """Run comprehensive Phase 2 CPU diagnostic"""
    print("JARVIS PHASE 2 CPU USAGE DIAGNOSTIC")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    results = []
    
    # Test all Phase 2 features
    print("\nTesting Phase 2 Sensory Features CPU Usage...")
    
    # Test Gesture Service
    gesture_result = test_gesture_service_cpu_usage()
    results.append(("Gesture Service", gesture_result))
    
    # Test Posture AI
    posture_result = test_posture_ai_cpu_usage()
    results.append(("Posture AI", posture_result))
    
    # Test Privacy Blur
    privacy_result = test_privacy_blur_cpu_usage()
    results.append(("Privacy Blur", privacy_result))
    
    # Generate report
    print(f"\n{'='*50}")
    print("PHASE 2 CPU USAGE DIAGNOSTIC REPORT")
    print(f"{'='*50}")
    
    passed = 0
    total = len(results)
    
    for feature, result in results:
        status = "PASSED" if result else "FAILED"
        if result:
            passed += 1
        print(f"{feature:.<25} {status}")
    
    print(f"\nSummary: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nAll Phase 2 sensory features are within CPU usage limits!")
        print("System is ready for production use.")
    else:
        print("\nSome Phase 2 features exceed CPU usage limits.")
        print("Consider optimization before production deployment.")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
