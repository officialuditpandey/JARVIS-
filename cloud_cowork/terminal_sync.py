#!/usr/bin/env python3
"""
JARVIS Terminal Sync Script
Integrates with JARVIS terminal to sync commands with website
"""

import sys
import os
import json
import threading
import time
import requests
from datetime import datetime

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from core.ai_engine import get_hybrid_response
    JARVIS_AVAILABLE = True
except ImportError as e:
    print(f"JARVIS backend not available: {e}")
    JARVIS_AVAILABLE = False

class TerminalSync:
    def __init__(self, dashboard_url="http://localhost:3000"):
        self.dashboard_url = dashboard_url
        self.sync_active = True
        self.running = False
        
    def send_to_website(self, command, response, source="terminal"):
        """Send command and response to website for sync"""
        try:
            data = {
                'command': command,
                'response': response,
                'source': source
            }
            
            response = requests.post(
                f"{self.dashboard_url}/api/terminal_command",
                json=data,
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"Synced to website: {command}")
            else:
                print(f"Failed to sync to website: {response.status_code}")
                
        except Exception as e:
            print(f"Error syncing to website: {e}")
    
    def process_command(self, command):
        """Process command through JARVIS AI and sync to website"""
        if not JARVIS_AVAILABLE:
            response = f"Command received: {command} (JARVIS backend not available)"
        else:
            try:
                response, source = get_hybrid_response(command, [])
                response = f"[{source}] {response}"
            except Exception as e:
                response = f"Error processing command: {e}"
        
        # Sync to website
        self.send_to_website(command, response)
        
        return response
    
    def start_terminal_interface(self):
        """Start interactive terminal interface"""
        print("=== JARVIS Terminal Sync Interface ===")
        print("Commands typed here will sync with the website dashboard")
        print("Type 'quit' or 'exit' to stop")
        print("=====================================")
        
        self.running = True
        
        while self.running:
            try:
                # Get command from user
                command = input(f"\nJARVIS [{datetime.now().strftime('%H:%M:%S')}]> ").strip()
                
                if command.lower() in ['quit', 'exit', 'stop']:
                    print("Stopping terminal sync...")
                    self.running = False
                    break
                
                if command:
                    print(f"Processing: {command}")
                    response = self.process_command(command)
                    print(f"JARVIS: {response}")
                
            except KeyboardInterrupt:
                print("\nStopping terminal sync...")
                self.running = False
                break
            except EOFError:
                print("\nStopping terminal sync...")
                self.running = False
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("Terminal sync stopped.")

def main():
    """Main function to start terminal sync"""
    sync = TerminalSync()
    
    try:
        # Test connection to dashboard
        response = requests.get(f"{sync.dashboard_url}/api/status", timeout=5)
        if response.status_code == 200:
            print("Connected to Cloud Cowork dashboard")
            sync.start_terminal_interface()
        else:
            print(f"Dashboard not responding: {response.status_code}")
            print("Make sure the dashboard is running at http://localhost:3000")
            
    except requests.exceptions.ConnectionError:
        print("Cannot connect to dashboard at http://localhost:3000")
        print("Please start the dashboard first: python simple_server.py")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
