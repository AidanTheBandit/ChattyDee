"""YouTube Live Chat Connector"""

import asyncio
import logging
import queue
import time
import random
from collections import deque

try:
    import pytchat
    PYTCHAT_AVAILABLE = True
except ImportError:
    PYTCHAT_AVAILABLE = False
    
from groq_summarizer import GroqSummarizer
from config import (
    YOUTUBE_VIDEO_ID, YOUTUBE_CHANNEL_ID,
    FAST_CHAT_THRESHOLD, CHAT_SPEED_WINDOW,
    MIN_MESSAGES_FOR_GROQ, COOLDOWN, TIMEOUT
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YouTubeConnector:
    def __init__(self):
        if not PYTCHAT_AVAILABLE:
            logger.error("pytchat library not available. Install with: pip install pytchat")
            self.available = False
            return
            
        self.video_id = YOUTUBE_VIDEO_ID
        self.channel_id = YOUTUBE_CHANNEL_ID
        self.chat = None
        self.chat_buffer = []
        self.summary_queue = queue.Queue()
        self.connected = False
        self.message_timestamps = deque(maxlen=100)
        self.groq_summarizer = GroqSummarizer()
        self._last_process_time = time.time()
        self._last_response_time = 0
        self.available = True
        self.running = False
        
    async def connect_to_chat(self):
        """Connect to YouTube live chat"""
        if not self.available:
            logger.error("YouTube connector not available")
            return
            
        if not self.video_id:
            logger.error("YouTube video ID not configured")
            return
            
        try:
            logger.info(f"📺 Connecting to YouTube live chat: {self.video_id}")
            self.chat = pytchat.create(video_id=self.video_id)
            self.connected = True
            self.running = True
            logger.info("✅ Successfully connected to YouTube live chat")
            
            # Start listening to chat
            await self._listen_to_chat()
            
        except Exception as e:
            logger.error(f"Failed to connect to YouTube chat: {e}")
            self.connected = False
            
    async def _listen_to_chat(self):
        """Listen to YouTube chat messages"""
        while self.running and self.chat.is_alive():
            try:
                for chat_data in self.chat.get().sync_items():
                    await self.handle_chat_message(chat_data)
                    
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error listening to YouTube chat: {e}")
                await asyncio.sleep(1)
                
    async def handle_chat_message(self, chat_data):
        """Handle incoming YouTube chat message"""
        try:
            user_name = chat_data.author.name
            message_text = chat_data.message
            
            if not message_text.strip():
                return
                
            # Record timestamp for speed tracking
            current_time = time.time()
            self.message_timestamps.append(current_time)
            
            # Add to buffer
            formatted_message = f"{user_name}: {message_text}"
            self.chat_buffer.append(formatted_message)
            
            logger.info(f"YouTube Chat: {formatted_message}")
            
            # Check if we should process messages
            await self.check_and_process_messages()
            
        except Exception as e:
            logger.error(f"Error handling YouTube chat message: {e}")
            
    async def check_and_process_messages(self):
        """Process messages with cooldown"""
        buffer_length = len(self.chat_buffer)
        
        if buffer_length < 1:
            return
        
        current_time = time.time()
        time_since_last_response = current_time - self._last_response_time
        chat_speed = self.calculate_chat_speed()
        
        logger.info(f"YouTube chat speed: {chat_speed:.1f} msg/min, Buffer: {buffer_length}")
        
        # Check cooldown
        if time_since_last_response < COOLDOWN:
            remaining_cooldown = COOLDOWN - time_since_last_response
            logger.info(f"⏳ Cooldown active: {remaining_cooldown:.1f}s remaining")
            return
        
        # Processing logic
        if chat_speed >= FAST_CHAT_THRESHOLD and buffer_length >= MIN_MESSAGES_FOR_GROQ:
            logger.info(f"🚀 Using Groq (fast chat: {chat_speed:.1f} msg/min)")
            await self.process_with_groq()
        elif buffer_length >= 1:
            logger.info(f"🎲 Using random selection ({buffer_length} messages)")
            self.process_with_random_selection()
        elif buffer_length >= 1 and self._should_process_timeout():
            logger.info(f"⏰ Timeout processing ({buffer_length} messages)")
            self.process_with_random_selection()
            
    def _should_process_timeout(self):
        """Check if we should process due to timeout"""
        current_time = time.time()
        time_since_last_response = current_time - self._last_response_time
        time_since_last_process = current_time - self._last_process_time
        
        return (time_since_last_response >= COOLDOWN and 
                time_since_last_process >= TIMEOUT)
                
    async def process_with_groq(self):
        """Process with Groq summarization"""
        if not self.groq_summarizer.is_available():
            logger.warning("Groq not available, using random selection")
            self.process_with_random_selection()
            return
            
        try:
            summary = self.groq_summarizer.summarize_chat_messages(
                self.chat_buffer, chat_context="YouTube"
            )
            
            if summary:
                processed_text = f"YouTube chat: {summary}"
                self.summary_queue.put(processed_text)
                logger.info(f"Groq summary: {processed_text}")
                self._last_response_time = time.time()
            else:
                self.process_with_random_selection()
            
            self.chat_buffer.clear()
            self._last_process_time = time.time()
            
        except Exception as e:
            logger.error(f"Error in Groq processing: {e}")
            self.process_with_random_selection()
            
    def process_with_random_selection(self):
        """Process with random message selection"""
        try:
            if not self.chat_buffer:
                return
            
            selected_message = random.choice(self.chat_buffer)
            
            if ":" in selected_message:
                content = selected_message.split(':', 1)[1].strip()
                summary = f"{content}"
            else:
                summary = f"{selected_message}"
            
            self.summary_queue.put(summary)
            logger.info(f"Random selection: {summary}")
            
            self._last_response_time = time.time()
            self.chat_buffer.clear()
            self._last_process_time = time.time()
            
        except Exception as e:
            logger.error(f"Error in random selection: {e}")
            if self.chat_buffer:
                simple_summary = f"YouTube chat activity from {len(self.chat_buffer)} viewers"
                self.summary_queue.put(simple_summary)
                self._last_response_time = time.time()
                self.chat_buffer.clear()
                self._last_process_time = time.time()
                
    def calculate_chat_speed(self):
        """Calculate messages per minute"""
        current_time = time.time()
        cutoff_time = current_time - CHAT_SPEED_WINDOW
        recent_messages = [ts for ts in self.message_timestamps if ts >= cutoff_time]
        return len(recent_messages) * (60 / CHAT_SPEED_WINDOW)
        
    def get_summary(self):
        """Get next summary from queue"""
        try:
            return self.summary_queue.get_nowait()
        except queue.Empty:
            return None
            
    def is_connected(self):
        """Check connection status"""
        return self.connected and self.chat and self.chat.is_alive()
        
    def disconnect(self):
        """Disconnect from YouTube chat"""
        self.running = False
        if self.chat:
            self.chat.terminate()
            self.connected = False
            logger.info("Disconnected from YouTube chat")
