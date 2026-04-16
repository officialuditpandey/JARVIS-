#!/usr/bin/env python3
"""
Comprehensive Health Check Report
Runs all Phase 1 health checks and generates a complete report
"""

import sys
import os
import subprocess
from datetime import datetime

def run_health_check(test_name, script_path):
    """Run individual health check"""
    print(f"\n{'='*60}")
    print(f"RUNNING: {test_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, timeout=60)
        
        # Extract the final result line
        lines = result.stdout.strip().split('\n')
        final_result = lines[-1] if lines else "UNKNOWN"
        
        print(result.stdout)
        
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        
        return final_result, result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT: {test_name} took too long")
        return "TIMEOUT", False
    except Exception as e:
        print(f"ERROR: {e}")
        return f"ERROR: {e}", False

def main():
    """Run comprehensive health check"""
    print("JARVIS PHASE 1 COMPREHENSIVE HEALTH CHECK")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Define all health checks
    health_checks = [
        ("Router Service", "health_check_router.py"),
        ("Security Service", "health_check_security.py"),
        ("Browser Service", "health_check_browser.py"),
        ("Main.py Integration", "health_check_main.py")
    ]
    
    results = []
    
    # Run all health checks
    for test_name, script_path in health_checks:
        final_result, success = run_health_check(test_name, script_path)
        results.append((test_name, final_result, success))
    
    # Generate comprehensive report
    print(f"\n{'='*60}")
    print("COMPREHENSIVE HEALTH CHECK REPORT")
    print(f"{'='*60}")
    
    passed = 0
    failed = 0
    
    for test_name, final_result, success in results:
        status = "PASSED" if success else "FAILED"
        if success:
            passed += 1
        else:
            failed += 1
        
        print(f"{test_name:.<30} {status}")
        print(f"  Result: {final_result}")
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests: {len(results)}")
    print(f"PASSED: {passed}")
    print(f"FAILED: {failed}")
    print(f"Success Rate: {(passed/len(results)*100):.1f}%")
    
    if failed == 0:
        print(f"\n{'='*60}")
        print("ALL PHASE 1 FEATURES: PASSED")
        print(f"{'='*60}")
        print("System is ready for production use!")
        print("\nFeatures Verified:")
        print("1. Fast + Private Router: Intelligent routing between Gemini and Moondream")
        print("2. Security Service: 60-second Presence Lock with Moondream verification")
        print("3. Browser Service: Headless Playwright browser automation")
        print("4. Main.py Integration: All services properly integrated")
        print("\nDashboard Access: http://localhost:5000")
        print("Privacy Shield: Active when Moondream processes sensitive data")
        
    else:
        print(f"\n{'='*60}")
        print("SOME PHASE 1 FEATURES: FAILED")
        print(f"{'='*60}")
        print("System requires attention before production use!")
        
        # Suggest fixes for failed tests
        print("\nSUGGESTED FIXES:")
        for test_name, final_result, success in results:
            if not success:
                print(f"\n{test_name}:")
                if "TIMEOUT" in final_result:
                    print("  - Fix: Increase timeout or optimize performance")
                elif "ERROR" in final_result:
                    print("  - Fix: Check error details and resolve dependencies")
                elif "FAILED" in final_result:
                    print("  - Fix: Review test logic and fix implementation")
                else:
                    print("  - Fix: Investigate the failure cause")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
