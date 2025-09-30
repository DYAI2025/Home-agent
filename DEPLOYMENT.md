# Voice AI Agent - Deployment Guide

This package allows you to deploy the Voice AI Agent with all features to cloud platforms like fly.io or Render.

## Architecture Overview

The system consists of:
1. LiveKit Server for real-time communication
2. Node.js frontend for avatar cockpit interface
3. Python agent with all AI features
4. MongoDB for data persistence (external service)

## Deployment Options

### Option 1: Deploy to Fly.io

#### Prerequisites:
- Fly.io account
- Fly CLI installed (`flyctl`)

#### Steps:
1. Initialize the app:
   ```bash
   fly launch
   ```

2. Set environment variables:
   ```bash
   fly secrets set LIVEKIT_URL=your_livekit_url
   fly secrets set LIVEKIT_API_KEY=your_livekit_api_key
   fly secrets set LIVEKIT_API_SECRET=your_livekit_api_secret
   fly secrets set OPENAI_API_KEY=your_openai_api_key
   fly secrets set MONGODB_URI=your_mongodb_connection_string
   ```

3. Deploy:
   ```bash
   fly deploy
   ```

### Option 2: Deploy to Render

#### Prerequisites:
- Render account

#### Steps:
1. Create a new Web Service on Render
2. Connect to your GitHub/GitLab repository
3. Use the Dockerfile for building
4. Set environment variables in the Render dashboard:
   - LIVEKIT_URL (your LiveKit server URL)
   - LIVEKIT_API_KEY
   - LIVEKIT_API_SECRET
   - OPENAI_API_KEY
   - MONGODB_URI
   - PORT (set to 3000)

## Important Notes

1. **LiveKit Server**: For production, you'll need a separate LiveKit server instance (can be self-hosted or use LiveKit Cloud)

2. **Database**: MongoDB connection needs to be configured separately

3. **API Keys**: All required API keys need to be set as environment variables

4. **Scaling**: Consider the resource requirements for audio processing

## Environment Variables

Required:
- `LIVEKIT_URL` - WebSocket URL for LiveKit server
- `LIVEKIT_API_KEY` - LiveKit API key
- `LIVEKIT_API_SECRET` - LiveKit API secret
- `OPENAI_API_KEY` - OpenAI API key for LLM functionality
- `MONGODB_URI` - MongoDB connection string

Optional:
- `PORT` - Port to run the server on (default: 3000)

## Features Included

All 12 requested features are included:
1. Avatar integration with Ready Player Me
2. MongoDB database
3. Semantic memory
4. Episodic memory 
5. Screen observation
6. Natural language processing
7. Task management
8. Scheduling
9. Personalized recommendations
10. Voice commands
11. Translation
12. Feedback mechanism

## Customization

You can customize the deployment by modifying:
- `Dockerfile` - Build and runtime configuration
- `fly.toml` - Fly.io specific settings
- `render.yaml` - Render specific settings

## Troubleshooting

If facing issues:
1. Check all environment variables are set correctly
2. Verify network connectivity between components
3. Check logs in the platform dashboard for errors