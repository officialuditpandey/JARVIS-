import os
import subprocess
import platform

def open_whatsapp_desktop():
    """Open WhatsApp desktop app on Windows only"""
    try:
        if platform.system() == "Windows":
            # Use WScript.Shell method which works for Windows Store apps
            result = subprocess.run([
                "powershell", "-Command", 
                "(New-Object -ComObject WScript.Shell).Run('shell:appsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App')"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("WhatsApp desktop app opened successfully.")
                return True
            else:
                print(f"Failed to open WhatsApp desktop app: {result.stderr}")
                return False
        else:
            print("WhatsApp desktop app is only supported on Windows.")
            return False
    except Exception as e:
        print(f"Unable to open WhatsApp desktop app: {e}")
        return False

if __name__ == "__main__":
    open_whatsapp_desktop()
