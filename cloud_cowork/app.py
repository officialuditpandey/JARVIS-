#!/usr/bin/env python3
"""
Cloud Cowork HUD - Modern JARVIS Interface
A floating, semi-transparent HUD similar to Shreshth Kaushik's setup
"""

import sys
import os
import json
import asyncio
import threading
from datetime import datetime
from typing import Dict, List, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import reflex as rx
from services.ai_service import AIService
from services.vision_service import VisionService
from services.automation_service import AutomationService
from services.notification_service import NotificationService
from utils.database import DatabaseManager
from utils.config import Config

class CloudCoworkHUD(rx.State):
    """Main Cloud Cowork HUD State"""
    
    def __init__(self):
        super().__init__()
        self.ai_service = AIService()
        self.vision_service = VisionService()
        self.automation_service = AutomationService()
        self.notification_service = NotificationService()
        self.db_manager = DatabaseManager()
        
        # HUD State
        self.is_thinking = False
        self.thinking_message = ""
        self.current_action = "Ready"
        self.notifications = []
        self.vision_feed_active = False
        self.automation_status = {}
        
        # Load initial data
        self.load_initial_data()

    def load_initial_data(self):
        """Load initial system status and notifications"""
        try:
            self.automation_status = self.automation_service.get_system_status()
            self.notifications = self.notification_service.get_recent_notifications()
        except Exception as e:
            print(f"Error loading initial data: {e}")

    def set_thinking(self, is_thinking: bool, message: str = ""):
        """Set thinking status with neon indicator"""
        self.is_thinking = is_thinking
        self.thinking_message = message
        if is_thinking:
            self.current_action = "Processing"
        else:
            self.current_action = "Ready"

    def add_notification(self, title: str, message: str, notification_type: str = "info"):
        """Add a new notification"""
        notification = {
            "id": len(self.notifications) + 1,
            "title": title,
            "message": message,
            "type": notification_type,
            "timestamp": datetime.now().isoformat(),
            "read": False
        }
        self.notifications.insert(0, notification)
        if len(self.notifications) > 10:
            self.notifications = self.notifications[:10]

    def toggle_vision_feed(self):
        """Toggle vision feed on/off"""
        self.vision_feed_active = not self.vision_feed_active
        if self.vision_feed_active:
            self.vision_service.start_feed()
        else:
            self.vision_service.stop_feed()

    def execute_automation(self, action: str, params: Dict = None):
        """Execute automation action"""
        self.set_thinking(True, f"Executing {action}")
        try:
            result = self.automation_service.execute_action(action, params)
            self.add_notification(
                f"Automation: {action}",
                result,
                "success"
            )
            return result
        except Exception as e:
            self.add_notification(
                f"Automation Failed: {action}",
                str(e),
                "error"
            )
            return None
        finally:
            self.set_thinking(False)

    async def process_ai_command(self, command: str):
        """Process AI command with modern response"""
        self.set_thinking(True, "Thinking...")
        try:
            response = await self.ai_service.process_command(command)
            self.add_notification(
                "AI Response",
                f"Command: {command[:50]}...",
                "ai"
            )
            self.set_thinking(False)
            return response
        except Exception as e:
            self.add_notification(
                "AI Error",
                str(e),
                "error"
            )
            self.set_thinking(False)
            return f"Error processing command: {e}"

# Main HUD Layout
def hud_layout():
    """Create the main HUD layout with glassmorphism design"""
    return rx.vstack(
        rx.hstack(
            # Left Panel - Status & Controls
            rx.vstack(
                status_panel(),
                action_grid(),
                vision_card(),
                automation_card(),
                width="350px",
                spacing="1rem",
            ),
            
            # Right Panel - AI Chat & Notifications
            rx.vstack(
                ai_chat_interface(),
                notification_panel(),
                width="400px",
                spacing="1rem",
            ),
        ),
        spacing="0",
        align="center",
        min_height="100vh",
        padding="2rem",
    )

def status_panel():
    """Status panel with neon thinking indicator"""
    return rx.card(
        rx.vstack(
            rx.heading("System Status", size="md"),
            rx.hstack(
                rx.text("●", color="#00ff88", font_size="1.5rem"),  # Neon dot
                rx.text("JARVIS Online", font_weight="bold"),
            ),
            rx.text(
                f"Status: {CloudCoworkHUD.current_action}",
                color="#00ff88" if CloudCoworkHUD.is_thinking else "#ffffff",
                font_weight="bold"
            ),
            rx.cond(
                CloudCoworkHUD.is_thinking,
                lambda: rx.text(
                    CloudCoworkHUD.thinking_message,
                    color="#00ffff",
                    font_style="italic"
                ),
                lambda: rx.text("")
            ),
        ),
        style=card_style(),
    )

def action_grid():
    """Interactive action grid with modern buttons"""
    return rx.card(
        rx.vstack(
            rx.heading("Action Center", size="md"),
            rx.grid(
                rx.button(
                    "🔍 System Scan",
                    on_click=lambda: execute_system_scan(),
                    style=action_button_style(),
                    size="3"
                ),
                rx.button(
                    "📱 WhatsApp",
                    on_click=lambda: execute_whatsapp_action(),
                    style=action_button_style(),
                    size="3"
                ),
                rx.button(
                    "🎵 Volume",
                    on_click=lambda: execute_volume_control(),
                    style=action_button_style(),
                    size="3"
                ),
                rx.button(
                    "💡 Brightness",
                    on_click=lambda: execute_brightness_control(),
                    style=action_button_style(),
                    size="3"
                ),
                columns="2",
                spacing="0.5rem",
            ),
        ),
        style=card_style(),
    )

def vision_card():
    """Vision card with live Moondream feed"""
    return rx.card(
        rx.vstack(
            rx.heading("Vision Portal", size="md"),
            rx.cond(
                CloudCoworkHUD.vision_feed_active,
                lambda: rx.vstack(
                    rx.text("📹 Vision Feed Active", color="#00ff88"),
                    rx.button(
                        "Stop Feed",
                        on_click=CloudCoworkHUD.toggle_vision_feed,
                        style=secondary_button_style(),
                        size="2"
                    ),
                ),
                lambda: rx.vstack(
                    rx.text("📹 Vision Feed Inactive", color="#666666"),
                    rx.button(
                        "Start Feed",
                        on_click=CloudCoworkHUD.toggle_vision_feed,
                        style=primary_button_style(),
                        size="2"
                    ),
                ),
            ),
        ),
        style=card_style(),
    )

def automation_card():
    """Automation card with system controls"""
    return rx.card(
        rx.vstack(
            rx.heading("Automation", size="md"),
            rx.vstack(
                rx.foreach(
                    CloudCoworkHUD.automation_status.items(),
                    lambda item: rx.hstack(
                        rx.text(f"• {item['name']}", width="150px"),
                        rx.text(
                            item['status'],
                            color="#00ff88" if item['active'] else "#ffffff"
                        ),
                    ),
                ),
                rx.button(
                    "⚙️ Settings",
                    on_click=lambda: open_automation_settings(),
                    style=secondary_button_style(),
                    size="2"
                ),
            ),
        ),
        style=card_style(),
    )

def ai_chat_interface():
    """Modern AI chat interface"""
    return rx.card(
        rx.vstack(
            rx.heading("JARVIS AI", size="md"),
            rx.vstack(
                rx.foreach(
                    CloudCoworkHUD.notifications,
                    lambda notification: rx.vstack(
                        rx.hstack(
                            rx.text(
                                f"[{notification['type'].upper()}]",
                                color=notification_color(notification['type']),
                                font_weight="bold",
                                width="80px"
                            ),
                            rx.text(notification['message']),
                        ),
                        style=notification_style(),
                        width="100%"
                    ),
                ),
                rx.form(
                    rx.input(
                        placeholder="Ask JARVIS anything...",
                        id="ai_input",
                        style=input_style(),
                    ),
                    rx.button(
                        "Send",
                        on_click=lambda: send_ai_command(),
                        style=primary_button_style(),
                        size="2"
                    ),
                ),
            ),
        ),
        style=card_style(),
    )

def notification_panel():
    """Notification panel"""
    return rx.card(
        rx.vstack(
            rx.heading("Notifications", size="md"),
            rx.foreach(
                CloudCoworkHUD.notifications,
                lambda notification: rx.vstack(
                    rx.hstack(
                        rx.text("•", color="#00ff88"),
                        rx.text(notification['title'], font_weight="bold"),
                    ),
                    rx.text(notification['message'], color="#cccccc"),
                ),
                style=notification_style(),
                width="100%"
            ),
        ),
        style=card_style(),
    )

# Style definitions
def card_style():
    return {
        "background": "rgba(255, 255, 255, 0.1)",
        "backdrop_filter": "blur(10px)",
        "border": "1px solid rgba(255, 255, 255, 0.2)",
        "border_radius": "15px",
        "padding": "1.5rem",
        "box_shadow": "0 8px 32px rgba(0, 0, 0, 0.1)",
    }

def action_button_style():
    return {
        "background": "linear-gradient(45deg, #00ff88, #00cc66)",
        "color": "white",
        "border": "none",
        "border_radius": "10px",
        "padding": "0.75rem 1.5rem",
        "font_weight": "600",
        "cursor": "pointer",
        "transition": "all 0.3s ease",
        "_hover": {"background": "linear-gradient(45deg, #00cc66, #009944)"},
    }

def primary_button_style():
    return {
        "background": "linear-gradient(45deg, #00ff88, #00cc66)",
        "color": "white",
        "border": "none",
        "border_radius": "10px",
        "padding": "0.75rem 1.5rem",
        "font_weight": "600",
        "cursor": "pointer",
        "transition": "all 0.3s ease",
    }

def secondary_button_style():
    return {
        "background": "rgba(255, 255, 255, 0.1)",
        "color": "#00ff88",
        "border": "1px solid #00ff88",
        "border_radius": "10px",
        "padding": "0.75rem 1.5rem",
        "font_weight": "600",
        "cursor": "pointer",
        "transition": "all 0.3s ease",
    }

def input_style():
    return {
        "background": "rgba(255, 255, 255, 0.05)",
        "border": "1px solid rgba(255, 255, 255, 0.1)",
        "border_radius": "10px",
        "padding": "1rem",
        "color": "white",
        "font_size": "1rem",
    }

def notification_style():
    return {
        "background": "rgba(0, 255, 255, 0.1)",
        "border": "1px solid rgba(0, 255, 255, 0.2)",
        "border_radius": "8px",
        "padding": "0.75rem",
        "margin_bottom": "0.5rem",
    }

def notification_color(notification_type):
    colors = {
        "info": "#00ff88",
        "success": "#00ff00",
        "error": "#ff0000",
        "ai": "#00ffff",
        "warning": "#ffaa00",
    }
    return colors.get(notification_type, "#ffffff")

# Event handlers
async def execute_system_scan():
    await CloudCoworkHUD.execute_automation("system_scan")

async def execute_whatsapp_action():
    await CloudCoworkHUD.execute_automation("whatsapp_send")

async def execute_volume_control():
    await CloudCoworkHUD.execute_automation("volume_control")

async def execute_brightness_control():
    await CloudCoworkHUD.execute_automation("brightness_control")

async def open_automation_settings():
    await CloudCoworkHUD.execute_automation("open_settings")

async def send_ai_command():
    input_text = rx.get_state().get("ai_input", "")
    if input_text:
        await CloudCoworkHUD.process_ai_command(input_text)
        rx.set_value("ai_input", "")

# Main App
app = rx.App()
app.add_page(hud_layout())

if __name__ == "__main__":
    app._compile()
