# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Voice AI Agent with Avatar Cockpit - a multi-modal AI assistant that combines voice interaction, visual avatar representation (Ready Player Me), and comprehensive AI features including memory systems, task management, and real-time translation. The system is built on LiveKit for real-time communication.

**NEW: Personalization Support**
- The system now supports full personalization with custom voice cloning (ElevenLabs & Coqui TTS)
- Users can configure their own Ready Player Me avatar
- Customizable agent personality, language, and greetings
- See `PERSONALIZATION_GUIDE.md` for setup instructions

## Architecture

The system consists of three main components that work together:

1. **Python Backend** (`voice_ai_agent/`): Orchestrates all AI subsystems including memory, NLP, task management, and voice command processing
2. **Node.js Frontend** (`server.js`, `index.html`): Serves the web-based avatar cockpit interface and handles LiveKit room connections
3. **LiveKit Server**: External real-time communication server (self-hosted or LiveKit Cloud)

### Core Integration Pattern

The `IntegratedVoiceAgent` class (in `voice_ai_agent/integrated_agent.py`) is the central orchestrator that coordinates:
- **VoiceAIAgent**: Core LLM conversation handler (uses OpenAI GPT-4o-mini by default)
- **AvatarManager**: Ready Player Me avatar integration
- **Memory Systems**: SemanticMemory and EpisodicMemory for knowledge retention
- **Utility Processors**: NLUProcessor, VoiceCommandProcessor, MultilingualProcessor, FeedbackProcessor, RecommendationEngine
- **Task Systems**: TaskManager and Scheduler for user task/appointment management
- **Screen Observer**: Real-time screen monitoring capabilities
- **MongoDBHandler**: Optional persistent storage (requires MongoDB URI)

The `LiveKitVoiceAgent` class (also in `integrated_agent.py`) wraps the IntegratedVoiceAgent and provides the LiveKit-specific entrypoint for real-time voice sessions.

## Development Commands

### Starting the System Locally

**Complete system startup:**
```bash
./start_all.sh  # Starts LiveKit server (Docker), frontend, and Python agent
```

**Individual components:**
```bash
# Node.js frontend (avatar cockpit)
npm start                    # Runs on http://localhost:3000

# Python agent (main voice AI)
python main.py dev           # Or: uv run python main.py dev

# Google Gemini agent (alternative to Python agent)
npm run agent:google         # Requires GOOGLE_REALTIME_MODEL env var
```

**Stop all components:**
```bash
./stop_all.sh
```

### Dependency Management

**Python dependencies:**
```bash
# Install minimal runtime dependencies
pip install -r requirements.txt

# Install full feature set (MongoDB, translation pipeline, etc.)
pip install -r requirements-optional.txt

# Using uv (preferred in this project)
uv sync
```

**Node.js dependencies:**
```bash
npm install
```

### LiveKit Server (Docker)

The system requires a LiveKit server. For local development:
```bash
# Start LiveKit server in Docker
cd server
docker run -d \
  --name livekit-server-dev \
  -p 7880:7880 \
  -p 7881:7881 \
  -p 50000-60000:50000-60000/udp \
  -e LIVEKIT_KEYS='{"devkey": "secret"}' \
  -v "$(pwd)/config.yaml:/config.yaml" \
  livekit/livekit-server:latest \
  --config /config.yaml

# Verify it's running
curl http://localhost:7880/
```

## Personalization Setup

The agent can be fully personalized with custom voice and avatar:

### Quick Setup

1. **Create user profile:**
   ```bash
   cp user_profile.example.json user_profile.json
   ```

2. **Configure your settings** in `user_profile.json`:
   - Voice provider (OpenAI, ElevenLabs, or Coqui)
   - Avatar URL from Ready Player Me
   - Personality and language preferences

3. **For voice cloning:**
   - **ElevenLabs**: Set `ELEVENLABS_API_KEY` in `.env`
   - **Coqui TTS**: Install with `pip install TTS`

4. **Full guide:** See `PERSONALIZATION_GUIDE.md` for detailed instructions

## Environment Variables

Required environment variables (set in `.env` or deployment platform):

```bash
# LiveKit Configuration
LIVEKIT_URL=wss://your-livekit-server    # WebSocket URL
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# OpenAI (for Python agent)
OPENAI_API_KEY=your_openai_key

# MongoDB (optional, for persistence)
MONGODB_URI=mongodb+srv://...

# Google Gemini Agent (optional, for npm run agent:google)
GOOGLE_API_KEY=your_google_key           # Or GOOGLE_GENAI_API_KEY
GOOGLE_REALTIME_MODEL=gemini-2.0-flash-exp
GOOGLE_GEMINI_VOICE=Puck

# Voice Cloning (optional)
ELEVENLABS_API_KEY=your_elevenlabs_key   # For ElevenLabs voice cloning
ELEVENLABS_VOICE_ID=your_voice_id        # Your cloned voice ID

# Optional customization
PORT=3000                                # Frontend server port
AGENT_INSTRUCTIONS="Custom prompt..."    # For Google agent
LIVEKIT_AGENT_CONCURRENCY=1             # For Google agent
```

## Code Structure

### Python Backend (`voice_ai_agent/`)

- **`agents/`**: Core agent implementations
  - `voice_agent.py`: VoiceAIAgent - simple LLM orchestrator with OpenAI integration
  - `avatar_manager.py`: Ready Player Me avatar integration

- **`memory/`**: Memory systems for knowledge retention
  - `semantic_memory.py`: Knowledge base and fact storage
  - `episodic_memory.py`: Personal experience and interaction tracking

- **`database/`**: Data persistence layer
  - `mongodb_handler.py`: MongoDB connection and operations

- **`utils/`**: Specialized processors and utilities
  - `nlp_processor.py`: Natural language understanding
  - `voice_command_processor.py`: Voice command recognition
  - `translation_engine.py`: Multi-language support
  - `feedback_processor.py`: User feedback handling
  - `recommendation_engine.py`: Personalized suggestions
  - `task_manager.py`: Task tracking and management
  - `scheduler.py`: Calendar and appointment handling
  - `screen_observer.py`: Screen monitoring capabilities
  - `voice_profile_manager.py`: **NEW** - User profile and personalization management
  - `custom_tts.py`: **NEW** - Multi-provider TTS wrapper (OpenAI, ElevenLabs, Coqui)

- **`integrated_agent.py`**: Main orchestrator that coordinates all subsystems (now with personalization support)

### Node.js Frontend

- **`server.js`**: Express server serving the avatar cockpit UI and LiveKit token endpoints
- **`index.html`**: Web interface with avatar rendering and chat capabilities
- **`google_voice_agent.mjs`**: Alternative agent using Google Gemini Realtime API
- **`libs/`**: Client-side LiveKit SDK files

### Server Components (`server/`)

- **`voice_agent.py`**: Standalone Python agent implementation
- **`basic_agent.py`**: Simplified agent for testing
- **`test_connection.py`**: LiveKit connection testing utility

## Deployment

This project supports deployment to Fly.io and Render. See `DEPLOYMENT.md` for detailed instructions.

**Key deployment notes:**
- LiveKit server must be deployed separately (self-hosted or LiveKit Cloud)
- Set all required environment variables as secrets
- Optional features require `requirements-optional.txt` - use `--build-arg INSTALL_OPTIONAL=true` with Fly.io
- MongoDB URI must point to external MongoDB service (MongoDB Atlas, etc.)

**Fly.io deployment:**
```bash
fly launch
fly secrets set LIVEKIT_URL=... LIVEKIT_API_KEY=... LIVEKIT_API_SECRET=... OPENAI_API_KEY=...
fly deploy                                    # Minimal features
fly deploy --build-arg INSTALL_OPTIONAL=true  # Full features
```

## Important Notes

- The `main.py` entry point automatically defaults to "start" command if none provided
- Python agent uses `uv` package manager (but pip also works)
- Frontend requires LiveKit URL to be set or token minting will fail
- The Google agent (`.mjs`) and Python agent serve the same purpose - run one or the other, not both
- MongoDB and screen observer features require `requirements-optional.txt` dependencies
- All 12 originally requested features are implemented (avatar, memory, NLP, tasks, scheduling, translation, feedback, etc.)

## Testing

The project currently has minimal test coverage. Key test file:
- `server/test_connection.py`: LiveKit connection verification

No formal test framework is configured yet (no pytest.ini or test suite).
