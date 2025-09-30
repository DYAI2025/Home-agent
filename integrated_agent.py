"""
Integrated Voice AI Agent

This module brings together all components of the voice AI agent system.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import os

from livekit import rtc
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
)
from livekit.agents import vad
from livekit.plugins import openai, silero

from .agents.voice_agent import VoiceAIAgent
from .agents.avatar_manager import AvatarManager
from .utils.screen_observer import ScreenObserver
from .utils.nlp_processor import NLUProcessor
from .utils.voice_command_processor import VoiceCommandProcessor
from .utils.translation_engine import MultilingualProcessor
from .utils.feedback_processor import FeedbackProcessor, FeedbackIntegration
from .utils.recommendation_engine import RecommendationEngine
from .memory.semantic_memory import SemanticMemory
from .memory.episodic_memory import EpisodicMemory
from .database.mongodb_handler import MongoDBHandler
from .utils.task_manager import TaskManager
from .utils.scheduler import Scheduler


class IntegratedVoiceAgent:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize all system components
        self.voice_agent = VoiceAIAgent()
        self.avatar_manager = AvatarManager()
        self.screen_observer = ScreenObserver()
        self.nlp_processor = NLUProcessor()
        self.voice_command_processor = VoiceCommandProcessor()
        self.translation_processor = MultilingualProcessor()
        self.feedback_processor = FeedbackProcessor()
        self.feedback_integration = FeedbackIntegration(self.feedback_processor)
        self.recommendation_engine = RecommendationEngine()
        
        # Initialize memory and storage systems
        self.semantic_memory = SemanticMemory()
        self.episodic_memory = EpisodicMemory()
        self.db_handler = MongoDBHandler()
        self.task_manager = TaskManager()
        self.scheduler = Scheduler()
        
        # Session-specific data
        self.current_session_data = {}
        
        # Initialize components
        self._initialize_system()

    def _initialize_system(self):
        """Initialize the complete system"""
        self.logger.info("Initializing integrated voice AI agent...")
        
        # Initialize database connection
        asyncio.create_task(self.db_handler.connect())
        
        self.logger.info("Integrated voice AI agent initialized successfully")

    async def process_user_input(self, user_input: str, user_id: str = "default_user") -> Dict[str, Any]:
        """Process user input through all system components"""
        
        # 1. Detect language and translate if necessary
        lang_processing = await self.translation_processor.process_multilingual_input(
            user_input, user_id
        )
        
        # 2. Process natural language understanding
        nlp_result = await self.nlp_processor.process_query(lang_processing["processed_text"])
        
        # 3. Check for voice commands
        voice_command_result = await self.voice_command_processor.process_text(user_input)
        
        # 4. If it's a voice command, execute it and return
        if voice_command_result:
            cmd_name, result = voice_command_result
            return {
                "type": "command_response",
                "command": cmd_name,
                "result": result,
                "processed_at": datetime.now().isoformat()
            }
        
        # 5. Store interaction in episodic memory
        await self.episodic_memory.store_interaction(user_id, user_input)
        
        # 6. Process through the main voice agent
        response = await self.voice_agent.process_user_query(
            lang_processing["processed_text"], user_id
        )
        
        # 7. Generate recommendations based on the interaction
        recommendations = await self.recommendation_engine.generate_recommendations(
            user_id, 
            context=user_input
        )
        
        # 8. Translate response back to user's preferred language
        response_translation = await self.translation_processor.translate_response(
            response, user_id
        )
        
        # 9. Package the complete result
        result = {
            "type": "conversation_response",
            "original_input": user_input,
            "processed_input": lang_processing["processed_text"],
            "nlp_analysis": nlp_result,
            "response": response_translation["final_response"],
            "recommendations": [rec.content for rec in recommendations],
            "processed_at": datetime.now().isoformat(),
            "user_preferences_applied": lang_processing["target_language"] != "en"
        }
        
        # 10. Store the response in episodic memory
        await self.episodic_memory.store_interaction(
            user_id, response_translation["final_response"], is_response=True
        )
        
        return result

    async def handle_screen_observation(self, screen_data: Dict[str, Any]):
        """Handle screen observation data"""
        # In a real implementation, this would:
        # 1. Analyze the screen content
        # 2. Determine if user needs assistance
        # 3. Generate appropriate response
        
        self.logger.info(f"Screen observation received: {screen_data.get('timestamp')}")
        
        # For now, just log the event
        # In the future, implement computer vision to understand screen content
        pass

    async def start_session(self, user_id: str, session_id: str):
        """Start a new interaction session"""
        self.current_session_data[session_id] = {
            "user_id": user_id,
            "start_time": datetime.now(),
            "interactions": [],
            "context": {}
        }
        
        self.logger.info(f"Started session {session_id} for user {user_id}")

    async def end_session(self, session_id: str):
        """End a session and perform cleanup"""
        if session_id in self.current_session_data:
            session_data = self.current_session_data[session_id]
            user_id = session_data["user_id"]
            
            # Summarize the session for episodic memory
            await self.episodic_memory.summarize_session(
                user_id,
                session_data["start_time"],
                datetime.now()
            )
            
            # Clean up session data
            del self.current_session_data[session_id]
            
            self.logger.info(f"Ended session {session_id} for user {user_id}")

    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user profile including all system data"""
        # Get data from all components
        user_data = await self.db_handler.get_user_data(user_id)
        satisfaction_score = self.feedback_processor.get_user_satisfaction_score(user_id)
        task_summary = await self.task_manager.get_task_summary(user_id)
        event_summary = await self.scheduler.get_event_summary(user_id)
        personalization_summary = await self.recommendation_engine.personalization_summary(user_id)
        
        profile = {
            "user_id": user_id,
            "satisfaction_score": satisfaction_score,
            "task_summary": task_summary,
            "event_summary": event_summary,
            "personalization_data": personalization_summary,
            "system_data": user_data
        }
        
        return profile

    async def generate_periodic_report(self) -> Dict[str, Any]:
        """Generate a system-wide report combining all component analytics"""
        feedback_report = await self.feedback_processor.generate_feedback_report()
        active_users = len(set([fb.user_id for fb in self.feedback_processor.feedback_store]))
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "active_users": active_users,
            "feedback_analytics": feedback_report["analytics"],
            "improvement_suggestions": feedback_report["improvement_suggestions"],
            "system_health": {
                "components_initialized": 12,  # All our components
                "database_connected": self.db_handler._connected,
                "last_error": None
            },
            "usage_metrics": {
                "total_interactions": len(self.feedback_processor.feedback_store),
                "avg_session_length": 0,  # Would need to track sessions
                "most_popular_features": []  # Would need to track feature usage
            }
        }
        
        return report

    async def request_user_feedback(self, user_id: str) -> Optional[str]:
        """Intelligently request feedback from a user"""
        feedback_request = await self.feedback_integration.get_personalized_feedback_request(user_id)
        return feedback_request

    async def submit_user_feedback(self, user_id: str, feedback_type: str, content: Any):
        """Submit feedback through the integrated system"""
        # Map feedback types to our system types
        from .utils.feedback_processor import FeedbackType
        
        if feedback_type == "rating":
            rating = content.get("rating")
            comment = content.get("comment", "")
            await self.feedback_processor.submit_rating(user_id, rating, comment)
        elif feedback_type == "text":
            await self.feedback_processor.submit_text_feedback(user_id, content)
        elif feedback_type == "issue":
            await self.feedback_processor.submit_issue_report(user_id, content)

    async def get_avatar_config(self) -> Dict[str, Any]:
        """Get avatar configuration for the frontend"""
        return await self.avatar_manager.get_avatar_config()

    async def get_recommendations(self, user_id: str) -> List[str]:
        """Get personalized recommendations for a user"""
        recommendations = await self.recommendation_engine.generate_recommendations(user_id)
        return [rec.content for rec in recommendations]

    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """Update user preferences across all systems"""
        # Update in recommendation engine
        await self.recommendation_engine.update_user_preferences(user_id, preferences)
        
        # Update in database
        await self.db_handler.store_user_preferences(user_id, preferences)
        
        # Update language preference in translation processor
        if "language" in preferences:
            self.translation_processor.set_user_language_preference(user_id, preferences["language"])

    async def perform_system_maintenance(self):
        """Perform routine system maintenance"""
        # Clear old episodic memories
        await self.episodic_memory.clear_old_interactions("default_user", days_to_keep=30)
        
        # Maintain database connections
        # Perform other maintenance tasks
        pass


# Main agent implementation that integrates with LiveKit
class LiveKitVoiceAgent:
    def __init__(self):
        self.integrated_agent = IntegratedVoiceAgent()
        self.logger = logging.getLogger(self.__class__.__name__)

    async def entrypoint(self, ctx: JobContext):
        """Entrypoint for the LiveKit agent"""
        print(f"Voice agent connected to room: {ctx.room.name}")
        
        # Connect to the room
        await ctx.connect()

        # Create an agent session with voice capabilities
        agent_session = AgentSession(
            vad=silero.VAD.load(),  # Voice Activity Detection
            stt=openai.STT(),       # Speech-to-Text
            llm=openai.LLM(model="gpt-4o-mini"),  # Language Model
            tts=openai.TTS(),       # Text-to-Speech
        )

        # Start the session
        await agent_session.start(agent=self, room=ctx.room)
        
        # Initial greeting
        await agent_session.generate_reply(
            instructions="Greet the user and offer assistance"
        )

        # Process incoming audio
        async for event in agent_session.stream():
            if event.type == "user_started_speaking":
                self.logger.info("User started speaking")
            elif event.type == "user_stopped_speaking":
                self.logger.info("User stopped speaking")
            elif event.type == "user_speech_committed":
                # Process user speech
                user_text = event.alternatives[0].text
                self.logger.info(f"User said: {user_text}")
                
                # Process through our integrated system
                response = await self.integrated_agent.process_user_input(user_text)
                
                # Generate AI response
                if response["type"] == "conversation_response":
                    await agent_session.generate_reply(
                        instructions=response["response"]
                    )

    async def get_agent_response(self, user_input: str, user_id: str = "default_user"):
        """Get response from the integrated agent"""
        return await self.integrated_agent.process_user_input(user_input, user_id)


# Example usage function
async def run_example():
    """Example of how to use the integrated agent"""
    agent = IntegratedVoiceAgent()
    
    # Simulate a conversation
    user_id = "example_user"
    
    # Start a session
    await agent.start_session(user_id, "session_1")
    
    # Process some inputs
    response1 = await agent.process_user_input("Hello, how are you?", user_id)
    print(f"Response 1: {response1['response']}")
    
    response2 = await agent.process_user_input("Can you remind me to call John at 3 PM?", user_id)
    print(f"Response 2: {response2['response']}")
    
    # End session
    await agent.end_session("session_1")
    
    # Generate a report
    report = await agent.generate_periodic_report()
    print(f"System report generated at: {report['timestamp']}")


if __name__ == "__main__":
    # Run the example
    asyncio.run(run_example())