# Multi-stage build to include LiveKit server
FROM golang:1.21-alpine AS livekit-builder

# Install dependencies for building LiveKit
RUN apk add --no-cache git build-base

# Copy the Server SDK
COPY ./serverSDK/server-sdk-go /go/src/livekit-server

# Build the LiveKit server from source
WORKDIR /go/src/livekit-server
RUN go build -o /usr/local/bin/livekit-server ./cmd/server

# Use an official Python runtime as the final image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        ffmpeg \
        nodejs \
        npm \
    && rm -rf /var/lib/apt/lists/*

# Copy the compiled LiveKit server
COPY --from=livekit-builder /usr/local/bin/livekit-server /usr/local/bin/livekit-server

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r voice_ai_agent/requirements.txt

# Install Node.js dependencies
WORKDIR /app/voice_ai_agent
RUN npm install

# Create a startup script that runs all components
RUN echo '#!/bin/bash\n\
\n\
echo "Starting Voice AI Agent with all components..."\n\
\n\
# Start LiveKit server in background\n\
echo "Starting LiveKit server..."\n\
nohup /usr/local/bin/livekit-server \\\n\
  --config-body="port: 7880\nlog_level: debug\nrtc:\n  tcp_port: 7881\n  port_range_start: 50000\n  port_range_end: 60000\n  use_external_ip: false\nkeys:\n  devkey: secret" > livekit.log 2>&1 &\n\
\n\
# Wait for LiveKit server to start\n\
sleep 10\n\
\n\
# Start the Python agent in background\n\
echo "Starting Python agent..."\n\
cd /app/agents\n\
nohup uv run python ../voice_ai_agent/main.py start > agent.log 2>&1 &\n\
\n\
# Wait for agent to start\n\
sleep 5\n\
\n\
# Start the Node.js frontend\n\
echo "Starting frontend..."\n\
cd /app/voice_ai_agent\n\
exec npm start\n\
' > /app/startup.sh && chmod +x /app/startup.sh

# Create a non-root user (after startup script is created)
RUN adduser --disabled-password --gecos '\'''\'' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose ports (LiveKit server ports and frontend)
EXPOSE 3000 7880 7881

# Set the startup script as the CMD
CMD ["/app/startup.sh"]