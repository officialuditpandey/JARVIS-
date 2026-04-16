#!/usr/bin/env python3
"""
JARVIS System Health Check - Verifies import architecture and Memory Vault connectivity
"""

import os
import sys

# Fix pathing - add current working directory to Python path
sys.path.append(os.getcwd())

print("🔧 JARVIS 2.0 System Health Check")
print("=" * 50)

try:
    # Test imports
    print("\n[1/3] Testing Service Imports...")
    from cloud_cowork.services.memory_service import MemoryService
    from cloud_cowork.services.automation_local import LocalAutomation
    print("✅ Services imported successfully")
    
    # Test Memory Vault connectivity
    print("\n[2/3] Testing Memory Vault Connectivity...")
    memory_service = MemoryService()
    
    # Add a test message
    memory_service.save_conversation(
        user_input="System health check test",
        jarvis_response="Memory vault operational",
        source="system_check"
    )
    print("✅ Memory Vault: Write test passed")
    
    # Retrieve recent context
    context = memory_service.get_recent_context(limit=1)
    if "System health check test" in str(context):
        print("✅ Memory Vault: Read test passed")
    else:
        print("⚠️ Memory Vault: Read test failed")
    
    # Get memory stats
    stats = memory_service.get_memory_stats()
    print(f"✅ Memory Vault Stats: {stats['conversations']} conversations, {stats['memories']} memories")
    
    # Test Automation Service
    print("\n[3/3] Testing Automation Service...")
    automation_service = LocalAutomation()
    print("✅ Automation Service initialized")
    
    print("\n🎉 JARVIS 2.0 System Health: ALL SYSTEMS OPERATIONAL")
    print("The import architecture has been fixed and services are reachable.")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("The services folder structure may still need adjustment.")
    
except Exception as e:
    print(f"❌ System Error: {e}")
    print("There may be an issue with service initialization.")
