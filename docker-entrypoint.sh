#!/bin/bash

# JARVIS Docker Entrypoint Script
echo "=================================="
echo "JARVIS AI Assistant - Docker Container"
echo "=================================="

# Set up environment
export PYTHONPATH=/app
export PYTHONUNBUFFERED=1

# Create necessary directories
mkdir -p /app/logs /app/temp /app/data

# Check for required files
if [ ! -f "/app/memory.json" ]; then
    echo "Creating default memory.json..."
    echo '{"facts": []}' > /app/memory.json
fi

# Check Ollama connection
echo "Checking Ollama connection..."
if curl -f http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "Ollama is running and accessible."
else
    echo "WARNING: Ollama not detected on localhost:11434"
    echo "Please ensure Ollama is running on the host system"
    echo "or use 'docker-compose up' to start Ollama container."
fi

# Check for GPU support
if [ -d "/dev/dri" ]; then
    echo "GPU device detected at /dev/dri"
else
    echo "No GPU device detected. CPU mode will be used."
fi

# Check for audio devices
if [ -d "/dev/snd" ]; then
    echo "Audio devices detected at /dev/snd"
else
    echo "WARNING: No audio devices detected. Speech recognition may not work."
fi

# Check for camera devices
if [ -e "/dev/video0" ]; then
    echo "Camera device detected at /dev/video0"
else
    echo "WARNING: No camera device detected. Vision features may not work."
fi

# Display environment information
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"
echo "Container ID: $(hostname)"

# Display port information
echo "Exposed ports:"
echo "  - 5000: Web dashboard"
echo "  - 3000: API server"
echo "  - 11434: Ollama API (if running)"

# Check for API keys
if [ -n "$GEMINI_API_KEY" ]; then
    echo "Gemini API key is set"
else
    echo "WARNING: GEMINI_API_KEY not set. Cloud features may be limited."
fi

if [ -n "$OPENAI_API_KEY" ]; then
    echo "OpenAI API key is set"
else
    echo "OpenAI API key not set. Image generation may not work."
fi

echo ""
echo "Starting JARVIS AI Assistant..."
echo "Press Ctrl+C to stop"
echo "=================================="

# Start JARVIS
exec python jarvis_final.py
