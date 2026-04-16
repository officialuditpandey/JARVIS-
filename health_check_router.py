#!/usr/bin/env python3
"""
Router Service Health Check
Tests Fast + Private Router with mocked voice inputs
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_router_service():
    """Test router service with mocked inputs"""
    print("=== ROUTER SERVICE HEALTH CHECK ===")
    
    try:
        # Import router service
        from services.router_service import FastPrivateRouter
        print("Router Service Import: SUCCESS")
        
        # Initialize router
        router = FastPrivateRouter()
        print("Router Initialization: SUCCESS")
        
        # Test mocked voice inputs
        test_cases = [
            ("open notepad", "moondream", "Privacy-sensitive task"),
            ("what is the meaning of life", "gemini", "Default routing"),
            ("what do you see", "moondream", "Privacy-sensitive task"),
            ("explain quantum physics", "gemini", "General task"),
            ("what's in my hand", "moondream", "Privacy-sensitive task"),
            ("help me code this", "gemini", "General task"),
            ("who is there", "moondream", "Privacy-sensitive task"),
            ("research this topic", "gemini", "General task")
        ]
        
        passed = 0
        total = len(test_cases)
        
        for query, expected_brain, test_type in test_cases:
            try:
                result = router.route_command(query)
                actual_brain = result['routing_decision']
                privacy_mode = router.is_privacy_mode()
                
                if actual_brain == expected_brain:
                    print(f"  '{query}' -> {actual_brain.upper()} (Privacy: {privacy_mode}) [{test_type}] - PASS")
                    passed += 1
                else:
                    print(f"  '{query}' -> {actual_brain.upper()} (Expected: {expected_brain.upper()}) - FAIL")
                    
            except Exception as e:
                print(f"  '{query}' -> ERROR: {e} - FAIL")
        
        # Check statistics
        stats = router.get_routing_stats()
        print(f"  Routing Statistics: {stats['total_commands']} commands processed")
        print(f"  Gemini: {stats['gemini_count']}, Moondream: {stats['moondream_count']}")
        
        # Final result
        success_rate = (passed / total) * 100
        print(f"Router Service Test: {passed}/{total} passed ({success_rate:.1f}%)")
        
        return success_rate >= 80  # 80% success rate required
        
    except Exception as e:
        print(f"Router Service Health Check FAILED: {e}")
        return False

if __name__ == "__main__":
    result = test_router_service()
    print(f"ROUTER SERVICE: {'PASSED' if result else 'FAILED'}")
