"""Multi-platform main application"""

import asyncio
import logging
import signal
import sys
from platform_manager import PlatformManager
from tts_handler import SimplifiedTTSHandler
from obs_controller import SourceSwitchingOBSController
from config import SUMMARY_DELAY, ENABLED_PLATFORMS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StreamingChattyDee:
    def __init__(self):
        self.platform_manager = PlatformManager()
        self.obs = SourceSwitchingOBSController()
        self.tts = SimplifiedTTSHandler()
        self.running = False
        self.processing = False
        
        # Connect TTS to OBS
        self.tts.set_obs_controller(self.obs)
        
    async def start(self):
        """Start the streaming application"""
        logger.info("🚀 Starting Multi-Platform Chatty Dee...")
        logger.info(f"📡 Enabled platforms: {', '.join(ENABLED_PLATFORMS)}")
        
        # Connect to OBS
        if not self.obs.connect():
            logger.error("❌ Failed to connect to OBS")
            return False
        
        # Check Groq availability
        if self.platform_manager.get_groq_status():
            logger.info("✅ Groq summarization enabled")
        else:
            logger.warning("⚠️ Groq not available - using random selection only")
        
        self.running = True
        
        # Start all platform connections
        platform_task = asyncio.create_task(self.platform_manager.start_all_platforms())
        
        try:
            await self.main_loop()
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            await self.cleanup()
            platform_task.cancel()
    
    async def main_loop(self):
        """Main processing loop"""
        logger.info("🎤 Multi-Platform Chatty Dee is running...")
        
        # Wait for at least one platform to connect
        max_wait = 30
        wait_time = 0
        while self.running and not self.platform_manager.is_any_connected() and wait_time < max_wait:
            logger.info("⏳ Waiting for platform connections...")
            await asyncio.sleep(2)
            wait_time += 2
            
        if not self.platform_manager.is_any_connected():
            logger.error("❌ No platforms connected after waiting")
            return
            
        connection_status = self.platform_manager.get_connection_status()
        logger.info(f"✅ Platform status: {connection_status}")
        
        while self.running:
            try:
                if not self.processing:
                    summary = self.platform_manager.get_summary()
                    if summary:
                        await self.process_summary(summary)
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Main loop error: {e}")
                await asyncio.sleep(1)
    
    async def process_summary(self, summary):
        """Process summary with animation"""
        if self.processing:
            return
            
        self.processing = True
        
        try:
            logger.info(f"🎭 Processing: {summary}")
            
            # Generate speech
            audio_file = self.tts.text_to_speech(summary)
            
            if audio_file:
                # Play with animation
                await asyncio.get_event_loop().run_in_executor(
                    None, self.tts.play_speech, audio_file
                )
                logger.info("✅ Speech and animation completed")
            else:
                logger.warning("❌ Failed to generate speech")
            
            # Wait before next
            await asyncio.sleep(SUMMARY_DELAY)
            
        except Exception as e:
            logger.error(f"Processing error: {e}")
        finally:
            self.processing = False
    
    async def cleanup(self):
        """Cleanup"""
        logger.info("🧹 Cleaning up...")
        self.running = False
        self.tts.stop_speech()
        await self.platform_manager.stop_all_platforms()
        self.obs.disconnect()

def signal_handler(signum, frame):
    logger.info("Received termination signal")
    sys.exit(0)

async def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    chatty = StreamingChattyDee()
    await chatty.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
