"""Multi-Platform Chat Manager"""

import asyncio
import logging
import queue
from barkle_connector import EnhancedBarkleConnector
from youtube_connector import YouTubeConnector
from twitch_connector import TwitchConnector
from config import ENABLED_PLATFORMS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlatformManager:
    """Manages connections to multiple chat platforms"""
    
    def __init__(self):
        self.platforms = {}
        self.summary_queue = queue.Queue()
        self.running = False
        
        # Initialize enabled platforms
        self._initialize_platforms()
        
    def _initialize_platforms(self):
        """Initialize all enabled platforms"""
        logger.info(f"Initializing platforms: {ENABLED_PLATFORMS}")
        
        if "barkle" in ENABLED_PLATFORMS:
            try:
                self.platforms["barkle"] = EnhancedBarkleConnector()
                logger.info("✅ Barkle connector initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Barkle: {e}")
                
        if "youtube" in ENABLED_PLATFORMS:
            try:
                self.platforms["youtube"] = YouTubeConnector()
                if self.platforms["youtube"].available:
                    logger.info("✅ YouTube connector initialized")
                else:
                    logger.warning("⚠️ YouTube connector unavailable")
                    del self.platforms["youtube"]
            except Exception as e:
                logger.error(f"Failed to initialize YouTube: {e}")
                
        if "twitch" in ENABLED_PLATFORMS:
            try:
                self.platforms["twitch"] = TwitchConnector()
                if self.platforms["twitch"].available:
                    logger.info("✅ Twitch connector initialized")
                else:
                    logger.warning("⚠️ Twitch connector unavailable")
                    del self.platforms["twitch"]
            except Exception as e:
                logger.error(f"Failed to initialize Twitch: {e}")
                
        if not self.platforms:
            logger.error("❌ No platforms were successfully initialized")
            
    async def start_all_platforms(self):
        """Start connections to all enabled platforms"""
        if not self.platforms:
            logger.error("No platforms available to start")
            return
            
        self.running = True
        tasks = []
        
        logger.info(f"🚀 Starting {len(self.platforms)} platform(s)...")
        
        # Create tasks for each platform
        for platform_name, connector in self.platforms.items():
            logger.info(f"Starting {platform_name}...")
            task = asyncio.create_task(
                self._run_platform(platform_name, connector)
            )
            tasks.append(task)
            
        # Start the message aggregation loop
        aggregation_task = asyncio.create_task(self._aggregate_messages())
        tasks.append(aggregation_task)
        
        # Wait for all tasks
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error in platform tasks: {e}")
            
    async def _run_platform(self, platform_name, connector):
        """Run a single platform connector"""
        try:
            logger.info(f"📡 Connecting to {platform_name}...")
            await connector.connect_to_chat()
        except Exception as e:
            logger.error(f"Error running {platform_name}: {e}")
            
    async def _aggregate_messages(self):
        """Aggregate messages from all platforms into a single queue"""
        logger.info("🔄 Starting message aggregation...")
        
        while self.running:
            try:
                # Check each platform for new summaries
                for platform_name, connector in self.platforms.items():
                    summary = connector.get_summary()
                    if summary:
                        # Add platform tag to summary
                        tagged_summary = {
                            "platform": platform_name,
                            "text": summary
                        }
                        self.summary_queue.put(tagged_summary)
                        logger.info(f"📨 Received message from {platform_name}: {summary}")
                        
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in message aggregation: {e}")
                await asyncio.sleep(1)
                
    def get_summary(self):
        """Get next summary from any platform"""
        try:
            summary_data = self.summary_queue.get_nowait()
            # Return just the text for compatibility
            return summary_data["text"]
        except queue.Empty:
            return None
            
    def get_summary_with_platform(self):
        """Get next summary with platform information"""
        try:
            return self.summary_queue.get_nowait()
        except queue.Empty:
            return None
            
    def is_any_connected(self):
        """Check if any platform is connected"""
        return any(
            connector.is_connected() 
            for connector in self.platforms.values()
        )
        
    def get_connection_status(self):
        """Get connection status for all platforms"""
        status = {}
        for platform_name, connector in self.platforms.items():
            status[platform_name] = connector.is_connected()
        return status
        
    async def stop_all_platforms(self):
        """Stop all platform connections"""
        logger.info("🛑 Stopping all platforms...")
        self.running = False
        
        for platform_name, connector in self.platforms.items():
            try:
                if hasattr(connector, 'disconnect'):
                    connector.disconnect()
                logger.info(f"Stopped {platform_name}")
            except Exception as e:
                logger.error(f"Error stopping {platform_name}: {e}")
                
    def get_groq_status(self):
        """Check if any platform has Groq available"""
        for connector in self.platforms.values():
            if hasattr(connector, 'groq_summarizer'):
                if connector.groq_summarizer.is_available():
                    return True
        return False
