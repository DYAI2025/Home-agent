#!/usr/bin/env python3
"""
Main Entry Point for the Voice AI Agent

This script starts the complete voice AI agent system with all features.
"""

import asyncio
import os
import sys
import logging
from dotenv import load_dotenv

from livekit.agents import WorkerOptions, cli

# Add the voice_ai_agent directory to the path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from voice_ai_agent.integrated_agent import LiveKitVoiceAgent


# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main function to start the voice AI agent"""
    logger.info("Starting Voice AI Agent with all features...")
    
    # Create the agent
    agent = LiveKitVoiceAgent()
    
    # Set up worker options for LiveKit
    worker_options = WorkerOptions(
        entrypoint_fnc=agent.entrypoint,
    )
    
    # Start the agent
    logger.info("Voice AI Agent is starting...")
    await cli.run_app(worker_options)


if __name__ == "__main__":
    # Run the agent
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Voice AI Agent stopped by user")
    except Exception as e:
        logger.error(f"Error running Voice AI Agent: {e}")
        raise