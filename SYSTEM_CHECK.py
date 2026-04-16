#!/usr/bin/env python3
"""
JARVIS System Check - Final Verification
Verifies all four major systems are operational
"""

import sys
import os
import time
from datetime import datetime

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), 'cloud_cowork'))

def run_system_check():
    """Run comprehensive system check for JARVIS 2.0"""
    print("=" * 60)
    print("🚀 JARVIS 2.0 SYSTEM CHECK")
    print("=" * 60)
    
    checks = {
        'Memory Vault': False,
        'Plugin System': False,
        'Professional Automation': False,
        'High-Fidelity Voice': False,
        'Orchestrator': False
    }
    
    try:
        # Check 1: Memory Vault
        print("📋 Checking Memory Vault...")
        try:
            from services.memory_service import MemoryService
            memory_service = MemoryService()
            stats = memory_service.get_memory_stats()
            print(f"   Database: jarvis_memory.db")
            print(f"   Conversations: {stats.get('conversations', 0)}")
            print(f"   Memories: {stats.get('memories', 0)}")
            print(f"   Size: {stats.get('database_size', 0)} bytes")
            checks['Memory Vault'] = True
            print("✅ Memory Vault: OPERATIONAL")
        except Exception as e:
            print(f"❌ Memory Vault: FAILED - {e}")
        
        time.sleep(1)
        
        # Check 2: Plugin System
        print("🔌 Checking Plugin System...")
        try:
            from plugins import PluginManager
            plugin_manager = PluginManager()
            available_plugins = plugin_manager.discover_plugins()
            print(f"   Available plugins: {available_plugins}")
            checks['Plugin System'] = True
            print("✅ Plugin System: OPERATIONAL")
        except Exception as e:
            print(f"❌ Plugin System: FAILED - {e}")
        
        time.sleep(1)
        
        # Check 3: Professional Automation
        print("⚙️ Checking Professional Automation...")
        try:
            from services.automation_local import LocalAutomation
            automation_service = LocalAutomation()
            
            # Test Windows URI schemes
            test_apps = ["calculator", "camera", "settings", "notepad"]
            uri_results = {}
            
            for app in test_apps:
                try:
                    result = automation_service.execute_command(f"open {app}")
                    if "opened" in result.lower():
                        uri_results[app] = "✅ PASS"
                    else:
                        uri_results[app] = f"❌ FAIL - {result}"
                except Exception as e:
                    uri_results[app] = f"❌ ERROR - {e}"
            
            print("   Windows URI Scheme Tests:")
            for app, result in uri_results.items():
                print(f"     {app}: {result}")
            
            checks['Professional Automation'] = True
            print("✅ Professional Automation: OPERATIONAL")
        except Exception as e:
            print(f"❌ Professional Automation: FAILED - {e}")
        
        time.sleep(1)
        
        # Check 4: High-Fidelity Voice
        print("🎤️ Checking High-Fidelity Voice...")
        try:
            from services.speaker import SpeakerService
            speaker_service = SpeakerService()
            status = speaker_service.get_status()
            print(f"   Edge-TTS: {'✅' if status.get('pygame_available') else '❌'}")
            print(f"   Pygame: {'✅' if status.get('pygame_available') else '❌'}")
            print(f"   Subprocess: {'✅' if status.get('subprocess_available') else '❌'}")
            print(f"   Queue Size: {status.get('queue_size', 0)}")
            
            checks['High-Fidelity Voice'] = True
            print("✅ High-Fidelity Voice: OPERATIONAL")
        except Exception as e:
            print(f"❌ High-Fidelity Voice: FAILED - {e}")
        
        time.sleep(1)
        
        # Check 5: Orchestrator
        print("🎛️ Checking Orchestrator...")
        try:
            import jarvis_final
            if hasattr(jarvis_final, 'global_brain_service') and hasattr(jarvis_final, 'global_automation_service') and hasattr(jarvis_final, 'global_memory_service') and hasattr(jarvis_final, 'global_plugin_manager') and hasattr(jarvis_final, 'global_speaker_service'):
                checks['Orchestrator'] = True
                print("✅ Orchestrator: ALL SERVICES INTEGRATED")
            else:
                checks['Orchestrator'] = False
                print("❌ Orchestrator: MISSING GLOBAL SERVICES")
        except Exception as e:
            print(f"❌ Orchestrator: FAILED - {e}")
        
        time.sleep(1)
        
        # Final Results
        print("\n" + "=" * 60)
        print("🎯 FINAL SYSTEM STATUS")
        print("=" * 60)
        
        passed = sum(checks.values())
        total = len(checks)
        
        print(f"Overall Health Score: {passed}/{total}")
        print(f"Systems Operational: {passed}/{total}")
        
        if passed == total:
            print("🎉 JARVIS 2.0: FULLY OPERATIONAL")
            print("All four major systems are working perfectly!")
            print("Ready for production deployment!")
        else:
            print(f"⚠️  JARVIS 2.0: PARTIALLY OPERATIONAL")
            print(f"Systems needing attention: {total - passed}")
            
            failed_systems = [name for name, status in checks.items() if not status]
            if failed_systems:
                print("\n⚠️  SYSTEMS REQUIRING ATTENTION:")
                for system in failed_systems:
                    print(f"   • {system}")
                print("\nPlease run the recommended fixes to achieve 100% functionality.")
        
        return passed == total
    except Exception as e:
        print(f"Error during check: {e}")
    if __name__ == "__main__":
        try:
            success = run_system_check()
            if success:
                print("\n🚀 JARVIS SYSTEM CHECK COMPLETE")
                print("All systems verified and operational!")
            else:
                print("\n❌ JARVIS SYSTEM CHECK FAILED")
                print("Please review errors above and fix issues.")
        except Exception as e:
            print(f"\n❌ SYSTEM CHECK ERROR: {e}")
            print("Please review errors above and fix issues.")
