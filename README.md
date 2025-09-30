# Voice AI Agent with Avatar Cockpit
Complete implementation with all requested features and a web-based interface

## Features Implemented:

1. **Avatar Integration**: Ready Player Me avatar integration through AvatarManager
2. **MongoDB Database**: Complete database handling via MongoDBHandler
3. **Semantic Memory**: Knowledge storage and retrieval via SemanticMemory
4. **Episodic Memory**: Personal experience tracking via EpisodicMemory
5. **Real-Time Screen Observation**: Screen monitoring via ScreenObserver
6. **Natural Language Processing**: Understanding via NLUProcessor
7. **Task Management**: Task handling via TaskManager
8. **Scheduling**: Calendar and appointment management via Scheduler
9. **Personalized Recommendations**: Tailored suggestions via RecommendationEngine
10. **Voice Command Functionality**: Voice command recognition via VoiceCommandProcessor
11. **Real-Time Translation**: Multilingual support via TranslationEngine
12. **Feedback Mechanism**: User feedback processing via FeedbackProcessor

## Project Structure:
- agents/: Main agent classes and avatar management
- memory/: Semantic and episodic memory systems
- database/: MongoDB integration
- utils/: Various utility classes (NLP, commands, translation, etc.)
- config/: Configuration (to be added as needed)

## Setup and Installation:

### 1. Python Agent Setup:
```bash
# Install Python dependencies
cd /path/to/Livekit_Agents/agents
uv sync

# Install additional dependencies for the voice agent
cd /path/to/Livekit_Agents/voice_ai_agent
pip install -r requirements.txt
```

### 2. JavaScript Frontend Setup:
```bash
# Install Node.js dependencies (already done if you followed the above)
cd /path/to/Livekit_Agents/voice_ai_agent
npm install
```

### 3. Environment Configuration:
```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file to add your API keys and configuration
nano .env
```

### 4. Start the Local LiveKit Server:
```bash
# Navigate to the server directory
cd /path/to/Livekit_Agents/server

# Start the LiveKit server using Docker
./start_server_docker.sh
```

## Running the Complete System:

### 1. Start the JavaScript Frontend (Avatar Cockpit):
```bash
cd /path/to/Livekit_Agents/voice_ai_agent

# Start the Node.js server
npm start
# Or use: node server.js
```

This will start the web interface at http://localhost:3000

### 2. Start the Python Agent:
```bash
cd /path/to/Livekit_Agents/agents

# Run the voice AI agent
uv run python ../voice_ai_agent/main.py dev
```

### 3. Using the Avatar Cockpit:
1. Open your browser and navigate to http://localhost:3000
2. Enter a room name and your identity
3. Select and load your Ready Player Me avatar
4. Connect to the LiveKit room
5. Interact with the AI agent via voice or text

## Key Components Integration:
The IntegratedVoiceAgent class brings together all features into a cohesive system,
with the LiveKitVoiceAgent providing the actual voice interface through LiveKit.
The JavaScript frontend provides a user-friendly interface to interact with the agent,
including avatar visualization and chat capabilities.

## Notes:
- Ensure MongoDB is running if you want to use the memory and user data features
- The agent connects to the same LiveKit server as specified in your .env file
- The avatar cockpit uses your local client SDK at ../client_SDK.js

This implementation provides a solid foundation that can be extended with more
sophisticated models and services as needed.