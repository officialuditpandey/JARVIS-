# JARVIS AI Assistant - Docker Deployment

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Host system with camera and microphone (for full functionality)
- GPU support recommended (but not required)

### Method 1: Using Docker Compose (Recommended)

1. **Clone and navigate to JARVIS directory:**
```bash
git clone <jarvis-repo>
cd JARVIS
```

2. **Set up environment variables:**
```bash
# Create .env file
cat > .env << EOF
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
REPLICATE_API_TOKEN=your_replicate_token_here
EOF
```

3. **Start JARVIS with Ollama:**
```bash
docker-compose up -d
```

4. **Pull required AI models:**
```bash
docker exec -it ollama ollama pull llama3.2:3b
docker exec -it ollama ollama pull moondream
docker exec -it ollama ollama pull jarvis-tiny:latest
```

5. **Access JARVIS:**
- Web Dashboard: http://localhost:5000
- API Server: http://localhost:3000
- Ollama API: http://localhost:11434

### Method 2: Manual Docker Build

1. **Build the image:**
```bash
docker build -t jarvis-ai .
```

2. **Run the container:**
```bash
docker run -it --privileged --net=host \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/memory.json:/app/memory.json \
  -v /dev/snd:/dev/snd \
  -v /dev/video0:/dev/video0 \
  -e GEMINI_API_KEY=your_key_here \
  --name jarvis-ai \
  jarvis-ai
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key for cloud AI | Optional |
| `OPENAI_API_KEY` | OpenAI API key for image generation | Optional |
| `REPLICATE_API_TOKEN` | Replicate API token for image generation | Optional |

### Volume Mounts

| Host Path | Container Path | Purpose |
|-----------|----------------|---------|
| `./data` | `/app/data` | Persistent data storage |
| `./logs` | `/app/logs` | Log files |
| `./memory.json` | `/app/memory.json` | JARVIS memory |
| `./credentials.json` | `/app/credentials.json` | Google credentials |
| `/dev/snd` | `/dev/snd` | Audio device access |
| `/dev/video0` | `/dev/video0` | Camera device access |

### Port Exposures

| Port | Service |
|------|---------|
| 5000 | Web Dashboard |
| 3000 | API Server |
| 11434 | Ollama API |

## Features in Docker

### Working Features
- **AI Chat**: Local and cloud AI models
- **Voice Recognition**: Speech-to-text via microphone
- **Text-to-Speech**: Voice responses
- **Vision System**: Camera-based object detection
- **Web Dashboard**: Browser-based interface
- **API Server**: RESTful API for integration
- **Multilingual Support**: Hindi and English
- **System Automation**: Control system functions

### Limitations
- **Audio**: Requires host audio device mounting
- **Camera**: Requires host camera device mounting
- **GPU**: Optional, but recommended for better performance
- **Network**: Host networking required for Ollama access

## Troubleshooting

### Common Issues

1. **Audio not working:**
   ```bash
   # Check audio device
   ls -la /dev/snd
   
   # Ensure proper permissions
   sudo usermod -a -G audio $USER
   ```

2. **Camera not working:**
   ```bash
   # Check camera device
   ls -la /dev/video*
   
   # Test camera
   v4l2-ctl --list-devices
   ```

3. **Ollama connection failed:**
   ```bash
   # Check Ollama status
   docker ps | grep ollama
   
   # Check logs
   docker logs ollama
   ```

4. **Permission denied:**
   ```bash
   # Run with proper privileges
   docker-compose down
   docker-compose up -d --privileged
   ```

### Logs and Debugging

```bash
# View JARVIS logs
docker logs jarvis-ai

# View Ollama logs
docker logs ollama

# View real-time logs
docker logs -f jarvis-ai
```

## Performance Optimization

### GPU Support

If you have an NVIDIA GPU, enable GPU acceleration:

```bash
# Install NVIDIA Container Toolkit
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# Run with GPU support
docker-compose up -d
```

### Resource Limits

Adjust resource limits in `docker-compose.yml`:

```yaml
services:
  jarvis:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

## Security Considerations

- JARVIS runs with privileged access for hardware control
- API keys should be stored securely in environment variables
- Network access is required for cloud AI services
- Camera and microphone access requires device mounting

## Updates and Maintenance

### Updating JARVIS

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Updating AI Models

```bash
# Update Ollama models
docker exec -it ollama ollama pull llama3.2:3b
docker exec -it ollama ollama pull moondream
```

### Backup Data

```bash
# Backup JARVIS data
docker cp jarvis-ai:/app/data ./backup/data
docker cp jarvis-ai:/app/memory.json ./backup/memory.json
```

## Support

For issues related to:
- **Docker deployment**: Check this README first
- **JARVIS functionality**: See main README.md
- **AI models**: Check Ollama documentation
- **Hardware issues**: Check system logs and device permissions
