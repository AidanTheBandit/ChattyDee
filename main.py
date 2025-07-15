"""Main application using source switching"""

import asyncio
import logging
import signal
import sys
from barkle_connector import EnhancedBarkleConnector
from tts_handler import SimplifiedTTSHandler
from obs_controller import SourceSwitchingOBSController
from config import SUMMARY_DELAY

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SourceSwitchingChattyDee:
    def __init__(self):
        self.barkle = EnhancedBarkleConnector()
        self.obs = SourceSwitchingOBSController()
        self.tts = SimplifiedTTSHandler()
        self.running = False
        self.processing = False
        
        # Connect TTS to OBS
        self.tts.set_obs_controller(self.obs)
        
    async def start(self):
        """Start the application"""
        logger.info("🚀 Starting Source-Switching Chatty Dee...")
        
        # Connect to OBS
        if not self.obs.connect():
            logger.error("❌ Failed to connect to OBS")
            return False
        
        self.running = True
        
        # Start Barkle connection
        barkle_task = asyncio.create_task(self.barkle.connect_to_chat())
        
        try:
            await self.main_loop()
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            await self.cleanup()
            barkle_task.cancel()
    
    async def main_loop(self):
        """Main processing loop"""
        logger.info("🎤 Chatty Dee is running with source switching...")
        
        while self.running:
            try:
                if not self.processing:
                    summary = self.barkle.get_summary()
                    if summary:
                        await self.process_summary(summary)
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Main loop error: {e}")
                await asyncio.sleep(1)
    
    async def process_summary(self, summary):
        """Process summary with source switching animation"""
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
        self.obs.disconnect()

def signal_handler(signum, frame):
    logger.info("Received termination signal")
    sys.exit(0)

async def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    chatty = SourceSwitchingChattyDee()
    await chatty.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
