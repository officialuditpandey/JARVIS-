#!/usr/bin/env python3
import re
import time
import subprocess
import platform
import pyautogui
import pyperclip

# Constants
OS_IS_WINDOWS = platform.system() == 'Windows'

def open_whatsapp_desktop():
    try:
        if OS_IS_WINDOWS:
            result = subprocess.run([
                'powershell', '-Command', 
                '(New-Object -ComObject WScript.Shell).Run("shell:appsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App")'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return 'WhatsApp desktop app opened successfully.'
            else:
                return f'Failed to open WhatsApp desktop app: {result.stderr}'
        else:
            return 'WhatsApp desktop app is only supported on Windows.'
    except Exception as e:
        return f'Unable to open WhatsApp desktop app: {e}'

def send_whatsapp_to_number(phone_number, message):
    try:
        # Clean phone number
        clean_phone = re.sub(r'[^\d+]', '', phone_number)
        if not clean_phone.startswith('+'):
            clean_phone = '+' + clean_phone
        
        print(f'Sending WhatsApp message to {clean_phone}: "{message}"')
        
        # Open WhatsApp desktop app
        desktop_result = open_whatsapp_desktop()
        print(f'Desktop result: {desktop_result}')
        
        # Wait for app to open
        print('Waiting 3 seconds for app to load...')
        time.sleep(3)
        
        # Copy message to clipboard
        pyperclip.copy(message)
        print('Message copied to clipboard.')
        
        # Wait for WhatsApp to be fully loaded
        print('Waiting for WhatsApp to fully load...')
        time.sleep(5)  # Increased wait time for app loading
        
        # Check if WhatsApp window is active
        try:
            whatsapp_window = None
            for i in range(10):  # Try for 10 seconds
                windows = pyautogui.getAllWindows()
                for window in windows:
                    if 'whatsapp' in window.title.lower():
                        whatsapp_window = window
                        break
                if whatsapp_window:
                    break
                time.sleep(1)
            
            if not whatsapp_window:
                return f'WhatsApp window not found. Message copied to clipboard for manual sending to {clean_phone}.'
            
            print('WhatsApp window detected. Starting automation...')
            
        except Exception as window_error:
            print(f'Window detection failed: {window_error}. Proceeding with automation...')
        
        # Automate message sending
        try:
            # Step 1: Focus window
            time.sleep(1)
            pyautogui.click(200, 200)  # Click in center area to focus app
            
            # Step 2: Wait a bit more for UI to be ready
            time.sleep(2)
            
            # Step 3: Open new chat
            print('Opening new chat...')
            pyautogui.hotkey('ctrl', 'n')
            time.sleep(2)  # Wait for new chat dialog
            
            # Step 4: Type phone number
            print(f'Typing phone number: {clean_phone}')
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            time.sleep(0.5)
            pyautogui.typewrite(clean_phone, interval=0.15)
            time.sleep(2)  # Wait for number validation
            
            # Step 5: Press Enter
            print('Opening chat...')
            pyautogui.press('enter')
            time.sleep(3)  # Wait for chat to open
            
            # Step 6: Paste and send
            print('Sending message...')
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(1)
            pyautogui.press('enter')
            
            return f'SUCCESS: WhatsApp message sent to {clean_phone}!'
            
        except Exception as automation_error:
            return f'AUTOMATION FAILED: {automation_error}. Message copied to clipboard for manual sending to {clean_phone}.'
            
    except Exception as e:
        return f'Error: {e}'

# Send the message
if __name__ == "__main__":
    result = send_whatsapp_to_number('+917518881628', 'hello')
    print(result)
