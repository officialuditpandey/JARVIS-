#!/usr/bin/env python3
"""
JARVIS Full System Diagnostic
Comprehensive check of all JARVIS features and components
"""

import sys
import os
import time
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any

# Add JARVIS backend path
sys.path.insert(0, '.')

class JarvisSystemDiagnostic:
    """Comprehensive diagnostic tool for JARVIS"""
    
    def __init__(self):
        self.test_results = {}
        self.overall_status = "UNKNOWN"
        self.failed_tests = []
        self.passed_tests = []
        
    def run_full_diagnostic(self) -> Dict[str, Any]:
        """Run complete system diagnostic"""
        print("🔍 JARVIS FULL SYSTEM DIAGNOSTIC")
        print("=" * 60)
        print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Test all major components
        self._test_core_infrastructure()
        self._test_intelligence_systems()
        self._test_enhanced_features()
        self._test_integrations()
        self._test_utilities()
        
        # Calculate overall status
        self._calculate_overall_status()
        
        # Generate report
        return self._generate_diagnostic_report()
    
    def _test_core_infrastructure(self):
        """Test core JARVIS infrastructure"""
        print("🧪 TESTING CORE INFRASTRUCTURE")
        print("-" * 40)
        
        # Test 1: Main JARVIS Module
        try:
            import jarvis_final
            self.test_results['core_module'] = {
                'status': 'PASS',
                'message': 'Main JARVIS module loads successfully',
                'details': f'File: jarvis_final.py'
            }
            self.passed_tests.append('core_module')
        except Exception as e:
            self.test_results['core_module'] = {
                'status': 'FAIL',
                'message': f'Main module error: {str(e)}',
                'details': 'Critical failure - JARVIS cannot run'
            }
            self.failed_tests.append('core_module')
        
        # Test 2: Memory Service
        try:
            from services.memory_service import MemoryService
            memory = MemoryService()
            memory.save_conversation("Test", "Response", "Diagnostic")
            history = memory.get_conversation_history(limit=1)
            
            self.test_results['memory_service'] = {
                'status': 'PASS',
                'message': 'Memory service operational',
                'details': f'Database: {memory.db_path}, History entries: {len(history)}'
            }
            self.passed_tests.append('memory_service')
        except Exception as e:
            self.test_results['memory_service'] = {
                'status': 'FAIL',
                'message': f'Memory service error: {str(e)}',
                'details': 'Conversation memory not working'
            }
            self.failed_tests.append('memory_service')
        
        # Test 3: AI Service
        try:
            from services.ai_service import AIService
            ai = AIService()
            
            self.test_results['ai_service'] = {
                'status': 'PASS',
                'message': 'AI service loaded',
                'details': 'Service initialized successfully'
            }
            self.passed_tests.append('ai_service')
        except Exception as e:
            self.test_results['ai_service'] = {
                'status': 'FAIL',
                'message': f'AI service error: {str(e)}',
                'details': 'AI processing may not work'
            }
            self.failed_tests.append('ai_service')
        
        print()
    
    def _test_intelligence_systems(self):
        """Test self-intelligence and reasoning systems"""
        print("🧠 TESTING INTELLIGENCE SYSTEMS")
        print("-" * 40)
        
        # Test 4: Self-Awareness Core
        try:
            from services.self_awareness_core import SelfAwarenessCore, ConsciousnessLevel
            awareness = SelfAwarenessCore()
            
            report = awareness.get_consciousness_report()
            
            self.test_results['self_awareness'] = {
                'status': 'PASS',
                'message': 'Self-awareness system operational',
                'details': f'Consciousness: {report["consciousness_level"]}, Goals: {report["active_goals"]}'
            }
            self.passed_tests.append('self_awareness')
        except Exception as e:
            self.test_results['self_awareness'] = {
                'status': 'FAIL',
                'message': f'Self-awareness error: {str(e)}',
                'details': 'JARVIS self-intelligence limited'
            }
            self.failed_tests.append('self_awareness')
        
        # Test 5: Proactive Reasoning
        try:
            from services.proactive_reasoning_engine import ProactiveReasoningEngine
            reasoning = ProactiveReasoningEngine()
            status = reasoning.get_reasoning_status()
            
            self.test_results['proactive_reasoning'] = {
                'status': 'PASS',
                'message': 'Proactive reasoning operational',
                'details': f'Mode: {status["current_mode"]}, Tasks: {status["completed_tasks"]}'
            }
            self.passed_tests.append('proactive_reasoning')
        except Exception as e:
            self.test_results['proactive_reasoning'] = {
                'status': 'FAIL',
                'message': f'Reasoning error: {str(e)}',
                'details': 'Autonomous decision making limited'
            }
            self.failed_tests.append('proactive_reasoning')
        
        # Test 6: Emotional Intelligence
        try:
            from services.emotional_intelligence_engine import EmotionalIntelligenceEngine
            emotional = EmotionalIntelligenceEngine()
            report = emotional.get_emotional_report()
            
            self.test_results['emotional_intelligence'] = {
                'status': 'PASS',
                'message': 'Emotional intelligence operational',
                'details': f'Emotion: {report["current_emotion"]}, Empathy: {report["empathy_level"]:.2f}'
            }
            self.passed_tests.append('emotional_intelligence')
        except Exception as e:
            self.test_results['emotional_intelligence'] = {
                'status': 'FAIL',
                'message': f'Emotional intelligence error: {str(e)}',
                'details': 'Emotion processing not working'
            }
            self.failed_tests.append('emotional_intelligence')
        
        # Test 7: Autonomous Goals
        try:
            from services.autonomous_goal_manager import AutonomousGoalManager
            goals = AutonomousGoalManager()
            status = goals.get_goal_status()
            
            self.test_results['autonomous_goals'] = {
                'status': 'PASS',
                'message': 'Goal management operational',
                'details': f'Active goals: {status["active_goals"]}, Progress: {status["average_progress"]:.2f}'
            }
            self.passed_tests.append('autonomous_goals')
        except Exception as e:
            self.test_results['autonomous_goals'] = {
                'status': 'FAIL',
                'message': f'Goal system error: {str(e)}',
                'details': 'Autonomous goal setting limited'
            }
            self.failed_tests.append('autonomous_goals')
        
        # Test 8: Self-Modification
        try:
            from services.self_modification_engine import SelfModificationEngine
            modification = SelfModificationEngine()
            status = modification.get_modification_status()
            
            self.test_results['self_modification'] = {
                'status': 'PASS',
                'message': 'Self-modification system operational',
                'details': f'Modifications: {status["modifications_completed"]}, Learning: {status["learning_queue_size"]}'
            }
            self.passed_tests.append('self_modification')
        except Exception as e:
            self.test_results['self_modification'] = {
                'status': 'FAIL',
                'message': f'Self-modification error: {str(e)}',
                'details': 'JARVIS cannot improve itself'
            }
            self.failed_tests.append('self_modification')
        
        # Test 9: Self-Preservation
        try:
            from services.self_preservation_engine import SelfPreservationEngine
            preservation = SelfPreservationEngine()
            status = preservation.get_preservation_status()
            
            self.test_results['self_preservation'] = {
                'status': 'PASS',
                'message': 'Self-preservation operational',
                'details': f'Threat level: {status["current_threat_level"]}, System health: {status["system_health"].get("overall_health", 0):.1f}%'
            }
            self.passed_tests.append('self_preservation')
        except Exception as e:
            self.test_results['self_preservation'] = {
                'status': 'FAIL',
                'message': f'Preservation error: {str(e)}',
                'details': 'System protection limited'
            }
            self.failed_tests.append('self_preservation')
        
        print()
    
    def _test_enhanced_features(self):
        """Test enhanced JARVIS features"""
        print("🚀 TESTING ENHANCED FEATURES")
        print("-" * 40)
        
        # Test 10: Enhanced JARVIS Core
        try:
            from enhanced_jarvis_core import EnhancedJarvisCore
            enhanced = EnhancedJarvisCore()
            status = enhanced.get_status_report()
            
            self.test_results['enhanced_core'] = {
                'status': 'PASS',
                'message': 'Enhanced core operational',
                'details': f'Files indexed: {status["file_index_size"]}, Profile: {len(status["user_profile"])} preferences'
            }
            self.passed_tests.append('enhanced_core')
        except Exception as e:
            self.test_results['enhanced_core'] = {
                'status': 'FAIL',
                'message': f'Enhanced core error: {str(e)}',
                'details': 'Personalization features not working'
            }
            self.failed_tests.append('enhanced_core')
        
        # Test 11: Intelligent Command Processor
        try:
            from intelligent_command_processor import process_command_intelligently
            result = process_command_intelligently("what do you see")
            
            self.test_results['command_processor'] = {
                'status': 'PASS',
                'message': 'Intelligent command processing operational',
                'details': f'Category: {result["category"]}, Confidence: {result["confidence"]:.2f}'
            }
            self.passed_tests.append('command_processor')
        except Exception as e:
            self.test_results['command_processor'] = {
                'status': 'FAIL',
                'message': f'Command processor error: {str(e)}',
                'details': 'Natural language understanding limited'
            }
            self.failed_tests.append('command_processor')
        
        # Test 12: Chitti Intelligence Core
        try:
            from services.chitti_intelligence_core import ChittiIntelligenceCore
            chitti = ChittiIntelligenceCore()
            status = chitti.get_chitti_status()
            
            self.test_results['chitti_intelligence'] = {
                'status': 'PASS',
                'message': 'Chitti intelligence core operational',
                'details': f'Integration level: {status["integration_level_name"]}, Score: {status["overall_intelligence_score"]:.2f}'
            }
            self.passed_tests.append('chitti_intelligence')
        except Exception as e:
            self.test_results['chitti_intelligence'] = {
                'status': 'FAIL',
                'message': f'Chitti core error: {str(e)}',
                'details': 'Advanced self-intelligence limited'
            }
            self.failed_tests.append('chitti_intelligence')
        
        print()
    
    def _test_integrations(self):
        """Test integration systems"""
        print("🔌 TESTING INTEGRATIONS")
        print("-" * 40)
        
        # Test 13: Integrations Manager
        try:
            from jarvis_integrations_manager import JarvisIntegrationsManager
            integrations = JarvisIntegrationsManager()
            status = integrations.get_integration_status()
            
            self.test_results['integrations_manager'] = {
                'status': 'PASS',
                'message': 'Integrations manager operational',
                'details': f'Total: {status["total_integrations"]}, Active: {status["active_integrations"]}'
            }
            self.passed_tests.append('integrations_manager')
        except Exception as e:
            self.test_results['integrations_manager'] = {
                'status': 'FAIL',
                'message': f'Integrations error: {str(e)}',
                'details': 'External service integration limited'
            }
            self.failed_tests.append('integrations_manager')
        
        print()
    
    def _test_utilities(self):
        """Test utility functions"""
        print("🛠️ TESTING UTILITY FUNCTIONS")
        print("-" * 40)
        
        # Test 14: Database Connectivity
        try:
            # Test personal database
            conn = sqlite3.connect("personal_jarvis_data.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            conn.close()
            
            self.test_results['database_system'] = {
                'status': 'PASS',
                'message': 'Database system operational',
                'details': f'Tables: {len(tables)}'
            }
            self.passed_tests.append('database_system')
        except Exception as e:
            self.test_results['database_system'] = {
                'status': 'FAIL',
                'message': f'Database error: {str(e)}',
                'details': 'Data storage may be compromised'
            }
            self.failed_tests.append('database_system')
        
        # Test 15: File System Access
        try:
            # Check if we can read/write files
            test_file = "diagnostic_test.txt"
            with open(test_file, "w") as f:
                f.write("JARVIS diagnostic test")
            
            with open(test_file, "r") as f:
                content = f.read()
            
            os.remove(test_file)
            
            self.test_results['file_system'] = {
                'status': 'PASS',
                'message': 'File system access operational',
                'details': 'Read/write permissions confirmed'
            }
            self.passed_tests.append('file_system')
        except Exception as e:
            self.test_results['file_system'] = {
                'status': 'FAIL',
                'message': f'File system error: {str(e)}',
                'details': 'File operations may not work'
            }
            self.failed_tests.append('file_system')
        
        # Test 16: Ollama Connection
        try:
            import ollama
            models = ollama.list()
            model_count = len(models.models) if hasattr(models, 'models') else 0
            
            self.test_results['ollama_connection'] = {
                'status': 'PASS',
                'message': 'Ollama connection operational',
                'details': f'Available models: {model_count}'
            }
            self.passed_tests.append('ollama_connection')
        except Exception as e:
            self.test_results['ollama_connection'] = {
                'status': 'FAIL',
                'message': f'Ollama error: {str(e)}',
                'details': 'AI models may not be accessible'
            }
            self.failed_tests.append('ollama_connection')
        
        print()
    
    def _calculate_overall_status(self):
        """Calculate overall system status"""
        total_tests = len(self.test_results)
        passed = len(self.passed_tests)
        failed = len(self.failed_tests)
        
        pass_rate = passed / total_tests if total_tests > 0 else 0
        
        if pass_rate >= 0.9:
            self.overall_status = "EXCELLENT"
        elif pass_rate >= 0.7:
            self.overall_status = "GOOD"
        elif pass_rate >= 0.5:
            self.overall_status = "FAIR"
        else:
            self.overall_status = "CRITICAL"
    
    def _generate_diagnostic_report(self) -> Dict[str, Any]:
        """Generate comprehensive diagnostic report"""
        total_tests = len(self.test_results)
        passed = len(self.passed_tests)
        failed = len(self.failed_tests)
        pass_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': self.overall_status,
            'summary': {
                'total_tests': total_tests,
                'passed': passed,
                'failed': failed,
                'pass_rate': f'{pass_rate:.1f}%'
            },
            'test_results': self.test_results,
            'passed_tests': self.passed_tests,
            'failed_tests': self.failed_tests,
            'recommendations': self._generate_recommendations()
        }
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 DIAGNOSTIC SUMMARY")
        print("=" * 60)
        print(f"Overall Status: {self.overall_status}")
        print(f"Tests Passed: {passed}/{total_tests} ({pass_rate:.1f}%)")
        print(f"Tests Failed: {failed}")
        print()
        
        if self.failed_tests:
            print("❌ FAILED COMPONENTS:")
            for test in self.failed_tests:
                result = self.test_results[test]
                print(f"  • {test}: {result['message']}")
            print()
        
        print("✅ OPERATIONAL FEATURES:")
        operational_features = [test for test in self.passed_tests]
        for feature in operational_features:
            print(f"  • {feature}")
        print()
        
        print("💡 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
        print()
        
        print("=" * 60)
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        if 'ollama_connection' in self.failed_tests:
            recommendations.append("Install/Start Ollama for AI functionality")
        
        if 'memory_service' in self.failed_tests:
            recommendations.append("Check database permissions for memory storage")
        
        if 'self_awareness' in self.failed_tests:
            recommendations.append("Review self-intelligence component installation")
        
        if 'enhanced_core' in self.failed_tests:
            recommendations.append("Verify enhanced JARVIS core files are present")
        
        if 'command_processor' in self.failed_tests:
            recommendations.append("Check intelligent command processor module")
        
        if len(self.passed_tests) >= 10:
            recommendations.append("JARVIS is mostly operational - focus on failed components")
        
        if not recommendations:
            recommendations.append("JARVIS is fully operational! No action needed.")
        
        return recommendations

def main():
    """Run full system diagnostic"""
    print("🏥 JARVIS HEALTH CHECK")
    print("Running comprehensive system diagnostic...")
    print()
    
    diagnostic = JarvisSystemDiagnostic()
    
    try:
        report = diagnostic.run_full_diagnostic()
        
        # Save report to file
        report_file = f"jarvis_diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📄 Full report saved to: {report_file}")
        print()
        
        # Return exit code based on status
        if report['overall_status'] in ['EXCELLENT', 'GOOD']:
            print("🎉 JARVIS IS HEALTHY AND OPERATIONAL!")
            return 0
        elif report['overall_status'] == 'FAIR':
            print("⚠️ JARVIS HAS SOME ISSUES BUT IS FUNCTIONAL")
            return 1
        else:
            print("🚨 JARVIS HAS CRITICAL ISSUES - REQUIRES ATTENTION")
            return 2
            
    except Exception as e:
        print(f"💥 CRITICAL ERROR: Diagnostic failed completely")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 3

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
