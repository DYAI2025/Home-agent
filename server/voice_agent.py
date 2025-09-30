#!/usr/bin/env python3
"""
Voice Agent for Local LiveKit Server

This agent demonstrates voice interaction capabilities with STT, LLM, and TTS.
"""

import asyncio
import os
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
    VAD,
)
from livekit.plugins import openai, silero


async def entrypoint(ctx: JobContext):
    """Entrypoint for the voice agent"""
    print(f"Voice agent connected to room: {ctx.room.name}")
    
    # Connect to the room
    await ctx.connect()

    # Create an agent with OpenAI GPT and voice capabilities
    agent = Agent(
        # Simple instructions for the agent
        instructions="You are a helpful assistant. Greet the user and have a friendly conversation.",
    )
    
    # Create a session with voice capabilities
    # Using Silero for voice activity detection, OpenAI for STT/LLM/TTS
    session = AgentSession(
        vad=silero.VAD.load(),  # Voice Activity Detection
        stt=openai.STT(),       # Speech-to-Text
        llm=openai.LLM(model="gpt-4o-mini"),  # Language Model
        tts=openai.TTS(),       # Text-to-Speech
    )

    # Start the session with the agent
    await session.start(agent=agent, room=ctx.room)
    
    # Generate an initial greeting
    await session.generate_reply(instructions="Greet the user warmly and introduce yourself as a helpful assistant")


if __name__ == "__main__":
    # Set environment variables for local development
    os.environ.setdefault("LIVEKIT_URL", "ws://localhost:7880")
    os.environ.setdefault("LIVEKIT_API_KEY", "devkey")
    os.environ.setdefault("LIVEKIT_API_SECRET", "secret")
    
    # Note: For this to work properly, you'll need to set these environment variables too:
    # os.environ.setdefault("OPENAI_API_KEY", "your-openai-api-key")
    
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        ),
    )