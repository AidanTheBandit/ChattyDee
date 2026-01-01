"""Twitch Chat Connector"""

import asyncio
import logging
import queue
import time
import random
from collections import deque

try:
    from twitchio.ext import commands
    TWITCHIO_AVAILABLE = True
except ImportError:
    TWITCHIO_AVAILABLE = False
    commands = None
    
from groq_summarizer import GroqSummarizer
from config import (
    TWITCH_BOT_TOKEN, TWITCH_CLIENT_ID, TWITCH_CHANNEL, TWITCH_BOT_NICK,
    FAST_CHAT_THRESHOLD, CHAT_SPEED_WINDOW,
    MIN_MESSAGES_FOR_GROQ, COOLDOWN, TIMEOUT
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TwitchConnector:
    def __init__(self):
        if not TWITCHIO_AVAILABLE:
            logger.error("twitchio library not available. Install with: pip install twitchio")
            self.available = False
            return
            
        self.token = TWITCH_BOT_TOKEN
        self.channel = TWITCH_CHANNEL
        self.nick = TWITCH_BOT_NICK
        self.bot = None
        self.chat_buffer = []
        self.summary_queue = queue.Queue()
        self.connected = False
        self.message_timestamps = deque(maxlen=100)
        self.groq_summarizer = GroqSummarizer()
        self._last_process_time = time.time()
        self._last_response_time = 0
        self.available = True
        
    async def connect_to_chat(self):
        """Connect to Twitch chat"""
        if not self.available:
            logger.error("Twitch connector not available")
            return
            
        if not self.token or not self.channel:
            logger.error("Twitch credentials not configured")
            return
            
        try:
            logger.info(f"📺 Connecting to Twitch channel: {self.channel}")
            
            # Create bot instance
            self.bot = TwitchBot(
                token=self.token,
                prefix='!',
                initial_channels=[self.channel],
                connector=self
            )
            
            # Start the bot
            await self.bot.start()
            
        except Exception as e:
            logger.error(f"Failed to connect to Twitch chat: {e}")
            self.connected = False
            
    async def handle_chat_message(self, user_name, message_text):
        """Handle incoming Twitch chat message"""
        try:
            if not message_text.strip():
                return
                
            # Record timestamp for speed tracking
            current_time = time.time()
            self.message_timestamps.append(current_time)
            
            # Add to buffer
            formatted_message = f"{user_name}: {message_text}"
            self.chat_buffer.append(formatted_message)
            
            logger.info(f"Twitch Chat: {formatted_message}")
            
            # Check if we should process messages
            await self.check_and_process_messages()
            
        except Exception as e:
            logger.error(f"Error handling Twitch chat message: {e}")
            
    async def check_and_process_messages(self):
        """Process messages with cooldown"""
        buffer_length = len(self.chat_buffer)
        
        if buffer_length < 1:
            return
        
        current_time = time.time()
        time_since_last_response = current_time - self._last_response_time
        chat_speed = self.calculate_chat_speed()
        
        logger.info(f"Twitch chat speed: {chat_speed:.1f} msg/min, Buffer: {buffer_length}")
        
        # Check cooldown
        if time_since_last_response < COOLDOWN:
            remaining_cooldown = COOLDOWN - time_since_last_response
            logger.info(f"⏳ Cooldown active: {remaining_cooldown:.1f}s remaining")
            return
        
        # Processing logic
        if chat_speed >= FAST_CHAT_THRESHOLD and buffer_length >= MIN_MESSAGES_FOR_GROQ:
            logger.info(f"🚀 Using Groq (fast chat: {chat_speed:.1f} msg/min)")
            await self.process_with_groq()
        elif self._should_process_timeout():
            logger.info(f"⏰ Timeout processing ({buffer_length} messages)")
            self.process_with_random_selection()
        elif buffer_length >= 1:
            logger.info(f"🎲 Using random selection ({buffer_length} messages)")
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
                self.chat_buffer, chat_context="Twitch"
            )
            
            if summary:
                processed_text = f"Twitch chat: {summary}"
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
                simple_summary = f"Twitch chat activity from {len(self.chat_buffer)} viewers"
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
        return self.connected
        
    def disconnect(self):
        """Disconnect from Twitch chat"""
        if self.bot:
            self.connected = False
            logger.info("Disconnected from Twitch chat")


if TWITCHIO_AVAILABLE and commands:
    class TwitchBot(commands.Bot):
        """Twitch bot for handling chat messages"""
        
        def __init__(self, token, prefix, initial_channels, connector):
            super().__init__(token=token, prefix=prefix, initial_channels=initial_channels)
            self.connector = connector
            
        async def event_ready(self):
            """Called when bot is ready"""
            logger.info(f"✅ Successfully connected to Twitch as {self.nick}")
            self.connector.connected = True
            
        async def event_message(self, message):
            """Called when a message is received"""
            # Ignore messages from the bot itself
            if message.echo:
                return
                
            # Handle the message
            await self.connector.handle_chat_message(
                message.author.name,
                message.content
            )
            
            # Allow commands to be processed
            await self.handle_commands(message)
else:
    # Dummy class when twitchio is not available
    class TwitchBot:
        def __init__(self, *args, **kwargs):
            pass
