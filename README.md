# JARVIS - Hybrid AI Assistant

<div align="center">

![JARVIS Logo](https://img.shields.io/badge/JARVIS-Hybrid%20AI%20Assistant-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.12+-green?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-red?style=for-the-badge)

*A sophisticated voice-activated AI assistant combining cloud and local intelligence*

</div>

## 📖 Project Overview

JARVIS is a cutting-edge hybrid AI assistant that seamlessly integrates multiple AI models and services to provide an intelligent, responsive personal assistant experience. By combining Google's Gemini AI for cloud processing with Ollama's local models, JARVIS offers both privacy-focused local computation and powerful cloud-based capabilities.

### 🧠 Hybrid Intelligence Architecture
- **Cloud Processing**: Google Gemini API for complex reasoning and web-connected tasks
- **Local Processing**: Ollama integration with multiple models (Llama, Moondream, custom JARVIS models)
- **Smart Routing**: Automatic selection between cloud and local based on task complexity and privacy requirements

## ✨ Key Features

### 🎯 Core Capabilities
- **Voice Interaction**: Full speech-to-text and text-to-speech with natural language processing
- **Multi-Model AI**: Access to 7+ AI models including specialized JARVIS-trained models
- **System Automation**: Control your computer through voice commands
- **Smart Memory**: Context-aware conversation with persistent memory system

### 👁️ Computer Vision
- **Moondream Integration**: Advanced visual understanding and analysis
- **Real-time Processing**: Live camera feed analysis for security and assistance
- **Object Detection**: Identify and track objects in your environment
- **Face Recognition**: Secure authentication with whitelisted faces

### ☁️ Cloud Synchronization
- **Google Drive Integration**: Upload/download files, manage documents
- **Google Calendar Sync**: Schedule management and event reminders
- **Cross-Device Sync**: Access your data from anywhere
- **Automatic Backup**: Continuous backup of important files and memories

### 🤖 System Automation
- **PyWhatKit Integration**: WhatsApp automation, YouTube control, web searches
- **Desktop Control**: Application launching, window management
- **Security Features**: PC lock, privacy screen, motion detection
- **Smart Home Ready**: Extensible architecture for IoT integration

### 📊 Dashboard & Monitoring
- **Web Dashboard**: Real-time monitoring at `http://localhost:5000`
- **Resource Monitoring**: CPU, memory, disk usage tracking
- **Activity Logs**: Comprehensive logging of all assistant activities
- **Health Checks**: Automated system diagnostics and optimization

## 🚀 Installation Guide

### Prerequisites
- Python 3.12 or higher
- Windows 10/11 (Primary platform), Linux (Experimental)
- At least 8GB RAM recommended
- Webcam and microphone for full functionality

### Step 1: Clone Repository
```bash
git clone https://github.com/your-username/jarvis.git
cd jarvis
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration

#### 4.1 Create `.env` File
Create a `.env` file in root directory with your configuration:

```env
# JARVIS Environment Variables

# API Keys (Required for cloud features)
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# File Paths (relative to project root)
MEMORY_FILE=memory.json
CREDENTIALS_FILE=credentials.json
GOOGLE_CREDENTIALS_FILE=google_credentials.pkl
VISION_LOGS_FILE=vision_system_logs.json
DAILY_NOTES_FILE=logs/daily_notes.json
SECURITY_LOGS_DIR=security_logs

# Configuration
LOCAL_MODEL=llama3-small:latest
VISION_MODEL=moondream
```

#### 4.2 Google Cloud Setup (Optional but Recommended)

1. **Create Google Cloud Project**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable APIs**
   - Google Drive API
   - Google Calendar API
   - Google OAuth2 API

3. **Create Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Select "Desktop app"
   - Download JSON file and rename it to `credentials.json`

4. **Configure OAuth Consent Screen**
   - Set User Type to "External"
   - Add required scopes:
     - `https://www.googleapis.com/auth/drive.file`
     - `https://www.googleapis.com/auth/calendar.readonly`
     - `https://www.googleapis.com/auth/calendar.events`

### Step 5: Ollama Setup (Local AI)

1. **Install Ollama**
   ```bash
   # Windows (PowerShell)
   iwr -useb https://ollama.ai/install.ps1 | iex
   
   # Linux/Mac
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Download Models**
   ```bash
   ollama pull llama3.1
   ollama pull moondream
   ollama pull llama3.2:3b
   ```

### Step 6: First Launch

```bash
python jarvis_final.py
```

JARVIS will perform initial system checks and guide you through any missing configurations.

## 🔒 Privacy & Security

### Zero-Trust Architecture
JARVIS is built on a **Zero-Trust security model** where:

- ✅ **No Personal Keys Shared**: All API keys and credentials are stored locally in your `.env` file
- ✅ **Local Processing Priority**: Sensitive operations prefer local AI models over cloud services
- ✅ **Encrypted Storage**: All local data files use secure storage practices
- ✅ **Privacy by Design**: Camera and microphone access requires explicit activation

### Data Protection
- **Local Memory**: Personal memories and preferences stored locally
- **Selective Cloud Sync**: Only explicitly shared data goes to cloud services
- **No Telemetry**: JARVIS does not collect or transmit usage data
- **Open Source**: Full code transparency allows security auditing

### Security Features
- **Face Recognition**: Whitelist-based authentication
- **Motion Detection**: Automated security monitoring
- **PC Lock**: Remote and automatic locking capabilities
- **Privacy Screen**: Instant screen blur for privacy

### Recommended Practices
1. **Keep `.env` Private**: Never commit `.env` to version control
2. **Regular Backups**: Use cloud sync for important data only
3. **Model Selection**: Choose local models for sensitive conversations
4. **Network Awareness**: Monitor what data is being synchronized

## 🛠️ Usage

### Basic Commands
```bash
# Start JARVIS
python jarvis_final.py

# Access Dashboard
# Open http://localhost:5000 in your browser

# Voice Commands
"Hey JARVIS, start security mode"
"JARVIS, upload my daily review to Drive"
"Hey JARVIS, what's on my calendar today?"
```

### Advanced Features
- **Study Mode**: Focused learning environment with note-taking
- **Security Mode**: Activates camera monitoring and alerts
- **Cloud Sync**: Manual and automatic synchronization
- **Custom Commands**: Extensible command system

## 📁 Project Structure

```
jarvis/
├── jarvis_final.py          # Main application entry point
├── services/                # Core service modules
├── config/                  # Configuration files
├── logs/                    # Application logs
├── security_logs/           # Security event logs
├── data/                    # Local data storage
├── .env                     # Environment variables (DO NOT COMMIT)
├── credentials.json          # Google OAuth credentials (DO NOT COMMIT)
├── requirements.txt          # Python dependencies
└── README.md               # This file
```

## 🤝 Contributing

1. Fork repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google** - Gemini API and Cloud services
- **Ollama** - Local AI model hosting
- **OpenAI** - Whisper and additional AI services
- **PyWhatKit** - System automation capabilities
- **OpenCV** - Computer vision and face detection

## 📞 Support

For issues, questions, or contributions:
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/officialuditpandey/JARVIS-/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/officialuditpandey/JARVIS-/discussions)
- 🔒 **Security Issues**: uditpandey9621@gmail.com

---

<div align="center">

**JARVIS** - *Your Intelligent Personal Assistant*

Made with ❤️ by [Udit Pandey](https://github.com/officialuditpandey)

</div>
