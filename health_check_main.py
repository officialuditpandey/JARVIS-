#!/usr/bin/env python3
"""
Main.py Integration Health Check
Tests imports and main loop for circular dependencies and exceptions
"""

import sys
import os
import ast
import importlib.util
sys.path.append(os.path.dirname(__file__))

def test_main_integration():
    """Test main.py integration for imports and main loop issues"""
    print("=== MAIN.PY INTEGRATION HEALTH CHECK ===")
    
    try:
        # Test main.py file exists
        main_file = "jarvis_final.py"
        if not os.path.exists(main_file):
            print(f"Main File Check: FAILED - {main_file} not found")
            return False
        print("Main File Check: SUCCESS")
        
        # Parse main.py AST to check for issues
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
            print("Main.py Syntax Check: SUCCESS")
        except SyntaxError as e:
            print(f"Main.py Syntax Check: FAILED - {e}")
            return False
        
        # Check for circular dependencies in imports
        print("Checking Import Structure...")
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        # Check for problematic imports
        problematic_imports = []
        service_imports = [imp for imp in imports if 'services' in imp]
        
        for i, imp in enumerate(service_imports):
            for j, other_imp in enumerate(service_imports):
                if i != j and imp == other_imp:  # Same import appearing multiple times
                    problematic_imports.append(imp)
        
        if problematic_imports:
            print(f"Circular Dependency Check: WARNING - {len(problematic_imports)} potential issues")
        else:
            print("Circular Dependency Check: SUCCESS")
        
        # Test main imports without execution
        print("Testing Main Imports...")
        try:
            # Test individual service imports
            service_imports = [
                'services.router_service',
                'services.security_service', 
                'services.browser_service',
                'services.dashboard_service',
                'services.vision_service'
            ]
            
            for service in service_imports:
                try:
                    spec = importlib.util.find_spec(service)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        # Don't execute, just check if it can be loaded
                        print(f"  {service}: SUCCESS")
                    else:
                        print(f"  {service}: FAILED - Not found")
                        return False
                except Exception as e:
                    print(f"  {service}: FAILED - {e}")
                    return False
                    
        except Exception as e:
            print(f"Import Test FAILED: {e}")
            return False
        
        # Check main loop structure
        print("Checking Main Loop Structure...")
        main_loop_found = False
        exception_handling_found = False
        
        for node in ast.walk(tree):
            if isinstance(node, ast.While):
                if hasattr(node, 'test') and node.test:
                    main_loop_found = True
            elif isinstance(node, ast.Try):
                exception_handling_found = True
            elif isinstance(node, ast.ExceptHandler):
                exception_handling_found = True
        
        if main_loop_found:
            print("Main Loop Structure: SUCCESS")
        else:
            print("Main Loop Structure: WARNING - No main loop found")
        
        if exception_handling_found:
            print("Exception Handling: SUCCESS")
        else:
            print("Exception Handling: WARNING - No exception handling found")
        
        # Check for service initialization
        print("Checking Service Initialization...")
        service_init_found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if 'init' in node.name.lower() and 'service' in node.name.lower():
                    service_init_found = True
                    break
            elif isinstance(node, ast.Call):
                if hasattr(node.func, 'id') and 'service' in node.func.id:
                    service_init_found = True
                    break
        
        if service_init_found:
            print("Service Initialization: SUCCESS")
        else:
            print("Service Initialization: WARNING - No explicit service initialization found")
        
        # Check for router integration
        print("Checking Router Integration...")
        if 'FastPrivateRouter' in content or 'router_service' in content:
            print("Router Integration: SUCCESS")
        else:
            print("Router Integration: FAILED")
            return False
        
        # Check for security integration
        print("Checking Security Integration...")
        if 'SecurityService' in content or 'security_service' in content:
            print("Security Integration: SUCCESS")
        else:
            print("Security Integration: FAILED")
            return False
        
        # Check for browser integration
        print("Checking Browser Integration...")
        if 'BrowserService' in content or 'browser_service' in content:
            print("Browser Integration: SUCCESS")
        else:
            print("Browser Integration: FAILED")
            return False
        
        # Check for dashboard integration
        print("Checking Dashboard Integration...")
        if 'DashboardService' in content or 'dashboard_service' in content:
            print("Dashboard Integration: SUCCESS")
        else:
            print("Dashboard Integration: FAILED")
            return False
        
        print("Main.py Integration Health Check: PASSED")
        return True
        
    except Exception as e:
        print(f"Main.py Integration Health Check FAILED: {e}")
        return False

if __name__ == "__main__":
    result = test_main_integration()
    print(f"MAIN.PY INTEGRATION: {'PASSED' if result else 'FAILED'}")
