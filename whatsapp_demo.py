#!/usr/bin/env python3
"""
Demo script to show WhatsApp desktop functionality
"""
import re
import time
import subprocess
import platform
import pyperclip

# Constants from JARVIS
OS_IS_WINDOWS = platform.system() == "Windows"

def open_whatsapp_desktop():
    """Open WhatsApp desktop app on Windows"""
    try:
        if OS_IS_WINDOWS:
            # Use WScript.Shell method which works for Windows Store apps
            result = subprocess.run([
                "powershell", "-Command", 
                "(New-Object -ComObject WScript.Shell).Run('shell:appsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App')"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return "WhatsApp desktop app opened successfully."
            else:
                return f"Failed to open WhatsApp desktop app: {result.stderr}"
        else:
            return "WhatsApp desktop app is only supported on Windows."
    except Exception as e:
        return f"Unable to open WhatsApp desktop app: {e}"

def send_whatsapp_to_number(phone_number, message):
    """Send WhatsApp message to any phone number using desktop app with automation"""
    try:
        import pyautogui
        
        # Clean phone number (remove spaces, dashes, etc.)
        clean_phone = re.sub(r"[^\d+]", "", phone_number)
        if not clean_phone.startswith('+'):
            clean_phone = '+' + clean_phone
        
        print(f"Original phone: {phone_number}")
        print(f"Cleaned phone: {clean_phone}")
        print(f"Message: {message}")
        
        # Open WhatsApp desktop app first
        print("\nOpening WhatsApp desktop app...")
        desktop_result = open_whatsapp_desktop()
        print(f"Result: {desktop_result}")
        
        # Wait a moment for the app to open
        print("Waiting 3 seconds for app to load...")
        time.sleep(3)
        
        # Copy message to clipboard
        try:
            pyperclip.copy(message)
            print("Message copied to clipboard.")
        except Exception as e:
            return f"Clipboard error: {e}"
        
        # Automate the message sending process
        print("Starting automated message sending...")
        try:
            # Step 1: Focus on WhatsApp window
            print("Step 1: Focusing on WhatsApp window...")
            time.sleep(1)
            pyautogui.click(100, 100)  # Click somewhere to focus the app
            
            # Step 2: Open new chat (Ctrl+N)
            print("Step 2: Opening new chat (Ctrl+N)...")
            pyautogui.hotkey('ctrl', 'n')
            time.sleep(1)
            
            # Step 3: Type the phone number
            print(f"Step 3: Typing phone number: {clean_phone}")
            pyautogui.hotkey('ctrl', 'a')  # Select all
            pyautogui.press('backspace')   # Clear any existing text
            pyautogui.typewrite(clean_phone, interval=0.1)
            time.sleep(1)
            
            # Step 4: Press Enter to open chat
            print("Step 4: Pressing Enter to open chat...")
            pyautogui.press('enter')
            time.sleep(2)
            
            # Step 5: Paste and send message
            print("Step 5: Pasting and sending message...")
            pyautogui.hotkey('ctrl', 'v')  # Paste message
            time.sleep(1)
            pyautogui.press('enter')       # Send message
            
            return f"\nSUCCESS: WhatsApp message sent to {clean_phone} via desktop app!"
            
        except Exception as automation_error:
            return f"\nAUTOMATION FAILED: {automation_error}\nPlease manually send the message to {clean_phone}. Message copied to clipboard."
            
    except KeyboardInterrupt:
        return "WhatsApp desktop opening cancelled by user."
    except Exception as e:
        return f"Unable to open WhatsApp desktop: {e}"

def demo():
    print("=== JARVIS WhatsApp Desktop Demo ===\n")
    
    # Demo with unknown number
    print("1. Demo: Sending to unknown number")
    print("Command: 'send whatsapp to +1234567890 saying hello world'")
    result = send_whatsapp_to_number("+1 234-567-890", "Hello world! This is a test message from JARVIS.")
    print(result)
    
    print("\n" + "="*50 + "\n")
    
    # Demo with another number
    print("2. Demo: Sending to another unknown number")
    print("Command: 'message +919876543210 on whatsapp how are you'")
    result = send_whatsapp_to_number("+91 98765-43210", "How are you? Hope you're doing well!")
    print(result)
    
    print("\n=== Demo Complete ===")
    print("\nInstructions:")
    print("1. WhatsApp desktop app should be open now")
    print("2. Your message is copied to clipboard")
    print("3. In WhatsApp desktop, click 'New Chat'")
    print("4. Enter the phone number shown above")
    print("5. Paste your message (Ctrl+V) and send")

if __name__ == "__main__":
    demo()
