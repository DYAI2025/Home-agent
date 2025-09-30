#!/bin/bash

# Complete Voice AI Agent Startup Script
# This script starts all components of the Voice AI Agent system

set -e

echo \"=================================\"
echo \"Voice AI Agent Startup Script\"
echo \"=================================\"

# Function to start the LiveKit server
start_livekit() {
    echo
    echo \"Starting LiveKit Server...\"
    cd /home/dyai/Dokumente/DYAI_home/DEV/AI_LLM/Livekit_Agents/server
    
    # Check if Docker is accessible
    if docker info > /dev/null 2>&1; then
        echo \"Docker is accessible. Starting LiveKit server...\"
        
        # Stop any existing container
        if docker ps -a --format \"table {{.Names}}\" | grep -q \"^livekit-server-dev$\"; then
            echo \"Stopping existing LiveKit server container...\"
            docker stop livekit-server-dev > /dev/null 2>&1 || true
            docker rm livekit-server-dev > /dev/null 2>&1 || true
        fi
        
        # Start the LiveKit server
        docker run -d \\
          --name livekit-server-dev \\
          --restart unless-stopped \\
          -p 7880:7880 \\
          -p 7881:7881 \\
          -p 50000-60000:50000-60000/udp \\
          -e LIVEKIT_PORT=7880 \\
          -e LIVEKIT_RTC_UDPPORT=50000-60000 \\
          -e LIVEKIT_RTC_TCPPORT=7881 \\
          -e LIVEKIT_KEYS='{\"devkey\": \"secret\"}' \\
          -e LIVEKIT_LOG_LEVEL=debug \\
          -e LIVEKIT_ENABLE_TURN=true \\
          -e LIVEKIT_TURN_PORT_RANGE_START=30000 \\
          -e LIVEKIT_TURN_PORT_RANGE_END=40000 \\
          -e LIVEKIT_TURN_LISTEN_ADDRESSES=0.0.0.0 \\
          -v \"$(pwd)/config.yaml:/config.yaml\" \\
          livekit/livekit-server:latest \\
          --config /config.yaml
        
        # Wait for server to start
        echo \"LiveKit server starting... waiting 10 seconds...\"
        sleep 10
        
        # Test the connection
        if curl -f http://localhost:7880/ > /dev/null 2>&1; then
            echo \"✓ LiveKit Server is running and accessible!\"
            echo \"  URL: ws://localhost:7880\"
            echo \"  Dashboard: http://localhost:7880\"
            return 0
        else
            echo \"! Warning: Could not reach the server at http://localhost:7880\"
            echo \"Check server logs with: docker logs -f livekit-server-dev\"
            return 1
        fi
    else
        echo \"Docker is not accessible. You may need to log out and log back in.\"
        echo \"Make sure your user is in the docker group:\"
        echo \"  sudo usermod -aG docker $USER\"
        echo \"Then log out and log back in.\"
        return 1
    fi
}

# Function to start the Node.js frontend
start_frontend() {
    echo
    echo \"Starting Node.js Frontend...\"
    cd /home/dyai/Dokumente/DYAI_home/DEV/AI_LLM/Livekit_Agents/voice_ai_agent
    
    # Check if npm is available
    if command -v npm &> /dev/null; then
        echo \"  - Installing Node.js dependencies (if not already installed)...\"
        npm install > /dev/null 2>&1 || echo \"  - Dependencies already installed or error occurred\"
        
        echo \"  - Starting Node.js server in background...\"
        nohup npm start > frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo \"  - Frontend started with PID $FRONTEND_PID\"
        echo \"  - Frontend logs at: $(pwd)/frontend.log\"
        echo \"  - Access at: http://localhost:3000\"
    else
        echo \"  - npm not available\"
        return 1
    fi
}

# Function to start the Python agent
start_agent() {
    echo
    echo \"Starting Python Agent...\"
    cd /home/dyai/Dokumente/DYAI_home/DEV/AI_LLM/Livekit_Agents/agents
    
    # Check if Python dependencies are available
    echo \"  - Checking Python dependencies...\"
    
    echo \"  - Starting Python agent in background...\"
    nohup uv run python ../voice_ai_agent/main.py dev > agent.log 2>&1 &
    AGENT_PID=$!
    echo \"  - Agent started with PID $AGENT_PID\"
    echo \"  - Agent logs at: $(pwd)/agent.log\"
}

# Check if user is in docker group
if groups $USER | grep -q docker; then
    echo \"✓ User is in Docker group\"
else
    echo \"! User is not in Docker group - Docker commands will fail\"
    echo \"  Run: sudo usermod -aG docker $USER\"
    echo \"  Then log out and back in\"
    exit 1
fi

# Try to start LiveKit server
if start_livekit; then
    echo \"✓ LiveKit server started successfully\"
else
    echo \"! LiveKit server failed to start\"
    echo \"  This is likely due to Docker permissions.\"
    echo \"  You need to log out and back in after adding user to docker group.\"
fi

# Start the frontend
start_frontend

# Give frontend a moment to start
sleep 3

# Start the agent
start_agent

echo
echo \"=================================\"
echo \"System startup complete!\"
echo \"=================================\"
echo \"1. LiveKit server: ws://localhost:7880 (if started)\"
echo \"2. Avatar cockpit: http://localhost:3000\"
echo \"3. Agent logs: $(pwd)/agent.log\"
echo \"4. Frontend logs: $(pwd)/voice_ai_agent/frontend.log\"
echo
echo \"To stop all components, use:\"
echo \"  pkill -f 'node server.js' 2>/dev/null || true\"
echo \"  pkill -f 'python.*main.py' 2>/dev/null || true\"
echo \"  docker stop livekit-server-dev 2>/dev/null || true\"
echo \"=================================\"