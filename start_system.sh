#!/bin/bash

# Startup script for the complete Voice AI Agent with Avatar Cockpit
# This script starts both the Node.js frontend and the Python agent

set -e

echo "Starting Voice AI Agent with Avatar Cockpit..."
echo

# Function to start the Node.js server
start_frontend() {
    echo "Starting Node.js frontend server..."
    cd /home/dyai/Dokumente/DYAI_home/DEV/AI_LLM/Livekit_Agents/voice_ai_agent
    npm start &
    FRONTEND_PID=$!
    echo "Frontend server started with PID $FRONTEND_PID"
}

# Function to start the Python agent
start_agent() {
    echo "Starting Python agent..."
    cd /home/dyai/Dokumente/DYAI_home/DEV/AI_LLM/Livekit_Agents/agents
    uv run python ../voice_ai_agent/main.py dev &
    AGENT_PID=$!
    echo "Python agent started with PID $AGENT_PID"
}

# Function to start the LiveKit server
start_livekit() {
    echo "Starting LiveKit server..."
    cd /home/dyai/Dokumente/DYAI_home/DEV/AI_LLM/Livekit_Agents/server
    ./start_server_docker.sh
    echo "LiveKit server started"
}

# Check if we need to start the LiveKit server
if [ "$1" = "with-server" ]; then
    echo "Starting LiveKit server first..."
    start_livekit
    sleep 10  # Wait for the server to start
fi

# Start the frontend
start_frontend

# Wait a moment to ensure frontend is ready
sleep 3

# Start the Python agent
start_agent

echo
echo "All components started successfully!"
echo
echo "1. LiveKit server (if started): ws://localhost:7880"
echo "2. Avatar cockpit: http://localhost:3000"
echo "3. Python agent: Connected to LiveKit server"
echo
echo "To stop all components, run: pkill -f 'node server.js\|python.*main.py'"
echo

# Wait for both processes
wait $FRONTEND_PID $AGENT_PID