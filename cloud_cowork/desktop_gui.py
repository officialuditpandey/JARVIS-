#!/usr/bin/env python3
"""
JARVIS Desktop GUI - Native Windows Overlay
PyQt6 implementation with glass effect and Ollama integration
"""

import sys
import os
import asyncio
import threading
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTextEdit, QLabel, QFrame, QScrollArea, QSizePolicy,
    QSystemTrayIcon, QMenu
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, 
    pyqtSignal, QObject, QThread, QSize, QPoint, pyqtProperty
)
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QPalette, 
    QLinearGradient, QPolygonF, QPainterPath, QRegion, QIcon
)

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from services.ai_service_local import LocalAIService
    LOCAL_AI_AVAILABLE = True
except ImportError as e:
    print(f"Local AI service not available: {e}")
    LOCAL_AI_AVAILABLE = False

# Import speak function from jarvis_final for consistent TTS
try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from jarvis_final import speak
    JARVIS_SPEAK_AVAILABLE = True
except ImportError as e:
    print(f"JARVIS speak function not available: {e}")
    JARVIS_SPEAK_AVAILABLE = False

class ArcReactor(QWidget):
    """Circular Arc Reactor element with pulsing animation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 120)
        self._angle = 0
        self._pulse_scale = 1.0
        self.is_active = False
        
        # Setup animations
        self.rotation_animation = QPropertyAnimation(self, b"angle")
        self.rotation_animation.setDuration(4000)
        self.rotation_animation.setStartValue(0)
        self.rotation_animation.setEndValue(360)
        self.rotation_animation.setLoopCount(-1)
        self.rotation_animation.setEasingCurve(QEasingCurve.Type.Linear)
        
        self.pulse_animation = QPropertyAnimation(self, b"pulse_scale")
        self.pulse_animation.setDuration(1000)
        self.pulse_animation.setStartValue(1.0)
        self.pulse_animation.setEndValue(1.2)
        self.pulse_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # Start rotation after a delay
        QTimer.singleShot(1000, self.rotation_animation.start)
    
    def set_active(self, active):
        """Set active state for pulsing"""
        self.is_active = active
        if active:
            self.pulse_animation.setDirection(QPropertyAnimation.Direction.Forward)
            self.pulse_animation.start()
        else:
            self.pulse_animation.setDirection(QPropertyAnimation.Direction.Backward)
            self.pulse_animation.start()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = int(40 * self._pulse_scale)
        
        # Outer ring (neon blue)
        pen = QPen(QColor(0, 200, 255), 3)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        # Inner rotating arc
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self._angle)
        
        pen = QPen(QColor(0, 255, 200), 2)
        painter.setPen(pen)
        painter.drawArc(-radius + 10, -radius + 10, (radius - 10) * 2, (radius - 10) * 2, 30, 270)
        painter.restore()
        
        # Center core
        if self.is_active:
            brush = QBrush(QColor(0, 255, 200))
        else:
            brush = QBrush(QColor(0, 150, 150))
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center_x - 8, center_y - 8, 16, 16)
        
        # J text in center
        painter.setPen(QPen(QColor(255, 255, 255)))
        font = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "J")
    
    def get_angle(self):
        return self._angle
    
    def set_angle(self, angle):
        self._angle = angle
        self.update()
    
    def get_pulse_scale(self):
        return self._pulse_scale
    
    def set_pulse_scale(self, scale):
        self._pulse_scale = scale
        self.update()
    
    angle = pyqtProperty(float, get_angle, set_angle)
    pulse_scale = pyqtProperty(float, get_pulse_scale, set_pulse_scale)

class AIWorker(QObject):
    """Worker thread for AI processing"""
    response_ready = pyqtSignal(str, str)
    status_changed = pyqtSignal(str)
    
    def __init__(self, ai_service):
        super().__init__()
        self.ai_service = ai_service
        self.is_processing = False
    
    def process_command(self, command):
        if self.is_processing:
            self.response_ready.emit("JARVIS is currently processing...", "Processing")
            return
        
        self.is_processing = True
        self.status_changed.emit("Thinking...")
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                response, source = loop.run_until_complete(
                    self.ai_service.process_command(command)
                )
                self.response_ready.emit(response, source)
            finally:
                loop.close()
                
        except Exception as e:
            self.response_ready.emit(f"Error: {e}", "Error")
        finally:
            self.is_processing = False
            self.status_changed.emit("Ready")

class JARVISDesktopGUI(QMainWindow):
    """Main JARVIS Desktop GUI"""
    
    def __init__(self):
        super().__init__()
        self.ai_service = None
        self.ai_worker = None
        self.ai_thread = None
        
        self.init_ai_service()
        self.init_ui()
        self.init_animations()
        self.init_system_tray()
        
        # Position window at bottom center
        self.position_window()
    
    def init_ai_service(self):
        """Initialize AI service"""
        if LOCAL_AI_AVAILABLE:
            try:
                self.ai_service = LocalAIService()
                self.ai_worker = AIWorker(self.ai_service)
                self.ai_thread = QThread()
                
                self.ai_worker.moveToThread(self.ai_thread)
                self.ai_worker.response_ready.connect(self.on_ai_response)
                self.ai_worker.status_changed.connect(self.on_status_changed)
                
                self.ai_thread.start()
                print("AI service initialized successfully")
            except Exception as e:
                print(f"AI service initialization failed: {e}")
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("JARVIS Desktop HUD")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(0.85)
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header with Arc Reactor
        header_layout = QHBoxLayout()
        
        # Arc Reactor
        self.arc_reactor = ArcReactor()
        header_layout.addWidget(self.arc_reactor)
        
        # Title
        title_label = QLabel("JARVIS DESKTOP HUD")
        title_label.setStyleSheet("""
            QLabel {
                color: #00ffff;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI';
                background: transparent;
            }
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Status indicator
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #00ff88;
                font-size: 12px;
                font-family: 'Segoe UI';
                background: transparent;
            }
        """)
        header_layout.addWidget(self.status_label)
        
        # Window controls
        self.create_window_controls(header_layout)
        
        layout.addLayout(header_layout)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ffff, stop:1 #0088ff);
                height: 2px;
                border: none;
            }
        """)
        layout.addWidget(separator)
        
        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMaximumHeight(300)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background: rgba(10, 10, 30, 200);
                border: 1px solid #00ffff;
                border-radius: 10px;
                color: #ffffff;
                font-family: 'Consolas';
                font-size: 11px;
                padding: 10px;
            }
            QTextEdit::scrollbar:vertical {
                background: rgba(0, 255, 255, 50);
                width: 8px;
                border-radius: 4px;
            }
            QTextEdit::scrollbar::handle:vertical {
                background: #00ffff;
                border-radius: 4px;
                min-height: 20px;
            }
        """)
        layout.addWidget(self.chat_display)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.input_field = QTextEdit()
        self.input_field.setMaximumHeight(40)
        self.input_field.setPlaceholderText("Ask JARVIS anything...")
        self.input_field.setStyleSheet("""
            QTextEdit {
                background: rgba(10, 10, 30, 200);
                border: 1px solid #00ff88;
                border-radius: 8px;
                color: #ffffff;
                font-family: 'Segoe UI';
                font-size: 12px;
                padding: 8px;
            }
            QTextEdit:focus {
                border: 2px solid #00ffff;
            }
        """)
        self.input_field.textChanged.connect(self.on_input_changed)
        input_layout.addWidget(self.input_field)
        
        # Send button
        self.send_button = QPushButton("SEND")
        self.send_button.setFixedSize(80, 40)
        self.send_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ff88, stop:1 #00cc66);
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                font-family: 'Segoe UI';
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00cc66, stop:1 #009944);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #009944, stop:1 #006633);
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        # Music button
        self.music_button = QPushButton("🎵")
        self.music_button.setFixedSize(50, 35)
        self.music_button.setStyleSheet("""
            QPushButton {
                background: rgba(255, 0, 255, 100);
                border: 1px solid #ff00ff;
                border-radius: 17px;
                color: white;
                font-size: 16px;
            }
            QPushButton:hover {
                background: rgba(255, 100, 255, 150);
            }
        """)
        self.music_button.clicked.connect(self.play_music)
        control_layout.addWidget(self.music_button)
        
        # WhatsApp button
        self.whatsapp_button = QPushButton("📱")
        self.whatsapp_button.setFixedSize(50, 35)
        self.whatsapp_button.setStyleSheet("""
            QPushButton {
                background: rgba(0, 255, 0, 100);
                border: 1px solid #00ff00;
                border-radius: 17px;
                color: white;
                font-size: 16px;
            }
            QPushButton:hover {
                background: rgba(100, 255, 100, 150);
            }
        """)
        self.whatsapp_button.clicked.connect(self.open_whatsapp)
        control_layout.addWidget(self.whatsapp_button)
        
        # YouTube button
        self.youtube_button = QPushButton("📺")
        self.youtube_button.setFixedSize(50, 35)
        self.youtube_button.setStyleSheet("""
            QPushButton {
                background: rgba(255, 0, 0, 100);
                border: 1px solid #ff0000;
                border-radius: 17px;
                color: white;
                font-size: 16px;
            }
            QPushButton:hover {
                background: rgba(255, 100, 100, 150);
            }
        """)
        self.youtube_button.clicked.connect(self.open_youtube)
        control_layout.addWidget(self.youtube_button)
        
        # Voice button
        self.voice_button = QPushButton("🎤")
        self.voice_button.setFixedSize(50, 35)
        self.voice_button.setStyleSheet("""
            QPushButton {
                background: rgba(0, 200, 255, 100);
                border: 1px solid #00ccff;
                border-radius: 17px;
                color: white;
                font-size: 16px;
            }
            QPushButton:hover {
                background: rgba(0, 255, 200, 150);
            }
        """)
        self.voice_button.clicked.connect(self.toggle_voice)
        control_layout.addWidget(self.voice_button)
        
        # Vision button
        self.vision_button = QPushButton("👁️")
        self.vision_button.setFixedSize(50, 35)
        self.vision_button.setStyleSheet("""
            QPushButton {
                background: rgba(0, 255, 136, 100);
                border: 1px solid #00ff88;
                border-radius: 17px;
                color: white;
                font-size: 16px;
            }
            QPushButton:hover {
                background: rgba(0, 255, 200, 150);
            }
        """)
        self.vision_button.clicked.connect(self.analyze_screen)
        control_layout.addWidget(self.vision_button)
        
        # Settings button
        self.settings_button = QPushButton("⚙️")
        self.settings_button.setFixedSize(50, 35)
        self.settings_button.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 20);
                border: 1px solid #888888;
                border-radius: 17px;
                color: white;
                font-size: 16px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 40);
            }
        """)
        self.settings_button.clicked.connect(self.show_settings)
        control_layout.addWidget(self.settings_button)
        
        control_layout.addStretch()
        
        # Exit button
        self.exit_button = QPushButton("✕")
        self.exit_button.setFixedSize(30, 30)
        self.exit_button.setStyleSheet("""
            QPushButton {
                background: rgba(255, 0, 0, 100);
                border: 1px solid #ff0000;
                border-radius: 15px;
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(255, 0, 0, 150);
            }
        """)
        self.exit_button.clicked.connect(self.close)
        control_layout.addWidget(self.exit_button)
        
        layout.addLayout(control_layout)
        
        # Set main widget style
        main_widget.setStyleSheet("""
            QWidget {
                background: rgba(10, 10, 30, 220);
                border-radius: 15px;
                border: 2px solid rgba(0, 255, 255, 100);
            }
        """)
        
        # Add initial message
        self.add_message("System", "JARVIS Desktop HUD initialized with local Ollama integration", "system")
    
    def init_animations(self):
        """Initialize animations"""
        # Fade in animation
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(1000)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(0.85)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.fade_animation.start()
    
    def create_window_controls(self, layout):
        """Create custom window controls (minimize, close)"""
        # Minimize button
        self.minimize_btn = QPushButton(" _ ")
        self.minimize_btn.setFixedSize(30, 25)
        self.minimize_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 255, 136, 0.2);
                border: 1px solid #00ff88;
                border-radius: 4px;
                color: #00ff88;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI';
            }
            QPushButton:hover {
                background: rgba(0, 255, 136, 0.4);
                border: 1px solid #00ffaa;
            }
            QPushButton:pressed {
                background: rgba(0, 255, 136, 0.6);
            }
        """)
        self.minimize_btn.clicked.connect(self.minimize_window)
        layout.addWidget(self.minimize_btn)
        
        # Close button
        self.close_btn = QPushButton(" X ")
        self.close_btn.setFixedSize(30, 25)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 68, 68, 0.2);
                border: 1px solid #ff4444;
                border-radius: 4px;
                color: #ff4444;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI';
            }
            QPushButton:hover {
                background: rgba(255, 68, 68, 0.4);
                border: 1px solid #ff6666;
            }
            QPushButton:pressed {
                background: rgba(255, 68, 68, 0.6);
            }
        """)
        self.close_btn.clicked.connect(self.close)
        layout.addWidget(self.close_btn)
    
    def init_system_tray(self):
        """Initialize system tray icon"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            # Create system tray icon
            self.tray_icon = QSystemTrayIcon(self)
            
            # Create a simple icon using Qt's built-in icons
            icon = self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)
            self.tray_icon.setIcon(icon)
            
            # Create tray menu
            tray_menu = QMenu()
            
            # Show/Hide action
            show_action = tray_menu.addAction("Show JARVIS")
            show_action.triggered.connect(self.show_window)
            
            # Minimize action
            minimize_action = tray_menu.addAction("Minimize")
            minimize_action.triggered.connect(self.minimize_window)
            
            # Exit action
            exit_action = tray_menu.addAction("Exit")
            exit_action.triggered.connect(self.close)
            
            self.tray_icon.setContextMenu(tray_menu)
            
            # Connect double-click to show window
            self.tray_icon.activated.connect(self.tray_icon_activated)
            
            # Show tray icon
            self.tray_icon.show()
            
            print("System tray icon initialized")
        else:
            print("System tray not available")
    
    def tray_icon_activated(self, reason):
        """Handle system tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()
    
    def show_window(self):
        """Show and restore the window"""
        self.showNormal()
        self.raise_()
        self.activateWindow()
    
    def minimize_window(self):
        """Minimize the window to taskbar"""
        self.showMinimized()
    
    def closeEvent(self, event):
        """Handle close event"""
        # Minimize instead of closing if system tray is available
        if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            event.ignore()
            self.showMinimized()
        else:
            super().closeEvent(event)
    
    def position_window(self):
        """Position window at bottom center of screen"""
        screen = QApplication.primaryScreen().geometry()
        window_width = 600
        window_height = 500
        
        x = (screen.width() - window_width) // 2
        y = screen.height() - window_height - 50
        
        self.setGeometry(x, y, window_width, window_height)
    
    def send_message(self):
        """Send message to AI"""
        message = self.input_field.toPlainText().strip()
        if not message:
            return
        
        self.add_message("You", message, "user")
        self.input_field.clear()
        
        if self.ai_worker:
            self.ai_worker.process_command(message)
        else:
            self.add_message("JARVIS", "AI service not available", "error")
    
    def on_ai_response(self, response, source):
        """Handle AI response"""
        self.arc_reactor.set_active(False)
        self.add_message(f"JARVIS [{source}]", response, "ai")
    
    def on_status_changed(self, status):
        """Handle status change"""
        self.status_label.setText(status)
        if status == "Thinking...":
            self.arc_reactor.set_active(True)
        else:
            self.arc_reactor.set_active(False)
    
    def on_input_changed(self):
        """Handle input text change"""
        # Limit input length
        text = self.input_field.toPlainText()
        if len(text) > 500:
            self.input_field.setPlainText(text[:500])
            cursor = self.input_field.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.input_field.setTextCursor(cursor)
    
    def add_message(self, sender, message, msg_type="user"):
        """Add message to chat display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if msg_type == "system":
            color = "#00ff88"
            prefix = "[SYSTEM]"
        elif msg_type == "user":
            color = "#ffffff"
            prefix = "[YOU]"
        elif msg_type == "ai":
            color = "#00ffff"
            prefix = "[JARVIS]"
            # Use jarvis_final speak function directly for AI responses
            if JARVIS_SPEAK_AVAILABLE and len(message) < 200:  # Only speak shorter messages
                try:
                    # Import and use jarvis_final speak function
                    import sys
                    import os
                    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
                    from jarvis_final import speak
                    speak(message)
                except Exception as e:
                    print(f"Speak error: {e}")
        else:  # error
            color = "#ff4444"
            prefix = "[ERROR]"
        
        formatted_message = f'<span style="color: {color}; font-weight: bold;">{prefix}</span> <span style="color: #888888;">[{timestamp}]</span><br><span style="color: #ffffff;">{message}</span><br><br>'
        
        self.chat_display.append(formatted_message)
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())
    
    def toggle_voice(self):
        """Toggle voice input"""
        if not self.ai_service or not self.ai_service.voice:
            self.add_message("System", "Voice service not available", "error")
            return
        
        self.voice_button.setText("🔴")
        self.add_message("System", "Listening for voice command...", "system")
        
        def voice_thread():
            result = self.ai_service.start_listening(timeout=5)
            if result:
                self.add_message("Voice", f"Heard: {result}", "user")
                if self.ai_worker:
                    self.ai_worker.process_command(result)
            else:
                self.add_message("Voice", "No speech detected", "system")
            
            # Reset button
            self.voice_button.setText("🎤")
        
        threading.Thread(target=voice_thread, daemon=True).start()
    
    def analyze_screen(self):
        """Analyze screen"""
        if not self.ai_service or not self.ai_service.vision:
            self.add_message("System", "Vision service not available", "error")
            return
        
        self.add_message("System", "Analyzing screen...", "system")
        
        def vision_thread():
            result = self.ai_service.analyze_vision("What is on my screen? Describe everything you see.")
            if result:
                self.add_message("Vision", result, "ai")
            else:
                self.add_message("Vision", "Screen analysis failed", "error")
        
        threading.Thread(target=vision_thread, daemon=True).start()
    
    def play_music(self):
        """Play music"""
        self.add_message("System", "What song would you like to play?", "system")
        # You can also trigger a default song or ask for input
        if self.ai_worker:
            self.ai_worker.process_command("play music")
    
    def open_youtube(self):
        """Open YouTube"""
        self.add_message("System", "Opening YouTube...", "system")
        if self.ai_worker:
            self.ai_worker.process_command("open youtube")
    
    def open_whatsapp(self):
        """Open WhatsApp desktop app"""
        self.add_message("System", "Opening WhatsApp desktop...", "system")
        if self.ai_worker:
            self.ai_worker.process_command("open whatsapp desktop")
    
    def show_settings(self):
        """Show settings dialog"""
        self.add_message("System", "Settings panel would open here", "system")
    
    def remember_fact(self, fact):
        """Remember a fact"""
        if self.ai_worker:
            self.ai_worker.process_command(f"remember that {fact}")
        else:
            self.add_message("System", f"Remembered: {fact}", "system")
    
    def recall_facts(self):
        """Recall remembered facts"""
        if self.ai_worker:
            self.ai_worker.process_command("what do you remember")
        else:
            self.add_message("System", "Memory recall not available", "error")
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if not self.input_field.hasFocus():
                self.input_field.setFocus()
            else:
                self.send_message()
        elif event.key() == Qt.Key.Key_Escape:
            self.close()
    
    def mousePressEvent(self, event):
        """Handle mouse press for window dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
    
    def closeEvent(self, event):
        """Handle close event"""
        if self.ai_thread:
            self.ai_thread.quit()
            self.ai_thread.wait()
        event.accept()

def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show GUI
    gui = JARVISDesktopGUI()
    gui.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
