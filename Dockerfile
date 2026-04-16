# JARVIS AI Assistant Docker Container
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    build-essential \
    cmake \
    pkg-config \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk-3-dev \
    libatlas-base-dev \
    gfortran \
    espeak \
    espeak-data \
    libespeak1 \
    libespeak-dev \
    portaudio19-dev \
    python3-dev \
    libasound2-dev \
    libportaudio2 \
    libportaudiocpp0 \
    ffmpeg \
    libsm6 \
    libxext6 \
    libfontconfig1 \
    libxrender1 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy JARVIS application
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/temp /app/data

# Set permissions
RUN chmod +x /app/*.py

# Expose ports for web services
EXPOSE 5000 3000 7860

# Create entrypoint script
RUN echo '#!/bin/bash\n\
echo "Starting JARVIS AI Assistant..."\n\
echo "Checking Ollama connection..."\n\
if ! curl -f http://localhost:11434/api/tags >/dev/null 2>&1; then\n\
    echo "WARNING: Ollama not detected. Please ensure Ollama is running on host."\n\
fi\n\
echo "Starting JARVIS..."\n\
python jarvis_final.py\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command
CMD ["python", "jarvis_final.py"]
