#!/usr/bin/env python3
"""
Basic LiveKit Agent for Local Development

This agent connects to a local LiveKit server and responds to users.
"""

import asyncio
import os
from livekit import rtc
from livekit.agents import (
    JobContext,
    WorkerOptions,
    cli,
    JobProcess,
)
from livekit.agents.llm import ChatContext
from livekit.plugins import openai, silero


async def entrypoint(ctx: JobContext):
    """Entrypoint for the agent"""
    print(f"Agent connected to room: {ctx.room.name}")
    
    # Connect to the room
    await ctx.connect()
    
    # Create an agent session when a participant joins
    participant = ctx.room.local_participant
    
    # Publish a track to indicate the agent is active
    source = rtc.AudioSource(rtc.AudioFrame.sample_rate, rtc.AudioFrame.num_channels)
    track = rtc.LocalAudioTrack.create_audio_track("agent-waiting", source)
    options = rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_MICROPHONE)
    publication = await participant.publish_track(track, options)
    
    print("Agent is ready and waiting for participants...")
    
    # Simple interaction when participants join
    @ctx.room.on("participant_connected")
    def on_participant_connected(participant: rtc.RemoteParticipant):
        print(f"New participant connected: {participant.identity}")
        # You could start an interaction here


def prewarm_process(proc: JobProcess) -> None:
    """Called when the worker process is initialized"""
    print("Process initialized, loading models...")
    # Pre-load any required models here if needed
    # For example, silero.VAD.load() could be called here


if __name__ == "__main__":
    # Set environment variables for local development
    os.environ.setdefault("LIVEKIT_URL", "ws://localhost:7880")
    os.environ.setdefault("LIVEKIT_API_KEY", "devkey")
    os.environ.setdefault("LIVEKIT_API_SECRET", "secret")
    
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm_process,
        ),
    )