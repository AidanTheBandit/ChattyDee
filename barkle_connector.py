"""Enhanced Barkle connector with speed detection"""

import asyncio
import websockets
import json
import queue
import logging
import time
import random
from collections import deque
from groq_summarizer import GroqSummarizer
from config import (
    BARKLE_TOKEN, BARKLE_WS_URL, FAST_CHAT_THRESHOLD, 
    CHAT_SPEED_WINDOW, MIN_MESSAGES_FOR_GROQ, RANDOM_SAMPLE_SIZE
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedBarkleConnector:
    def __init__(self):
        self.token = BARKLE_TOKEN
        self.ws_url = BARKLE_WS_URL
        self.chat_buffer = []
        self.summary_queue = queue.Queue()
        self.connected = False
        self.message_timestamps = deque(maxlen=100)
        self.groq_summarizer = GroqSummarizer()
        
    async def connect_to_chat(self):
        """Connect to Barkle chat with reconnection"""
        while True:
            try:
                uri = f"{self.ws_url}?token={self.token}"
                logger.info(f"Connecting to Barkle chat")
                
                async with websockets.connect(uri) as websocket:
                    self.connected = True
                    logger.info("Successfully connected to Barkle chat")
                    
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            await self.process_message(data)
                        except Exception as e:
                            logger.error(f"Message processing error: {e}")
                            
            except websockets.exceptions.ConnectionClosed:
                logger.warning("WebSocket connection closed, reconnecting...")
                self.connected = False
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Connection error: {e}")
                self.connected = False
                await asyncio.sleep(5)
    
    async def process_message(self, data):
        """Process incoming messages"""
        message_type = data.get("type")
        
        if message_type == "chat":
            await self.handle_chat_message(data)
        elif message_type == "error":
            logger.error(f"Barkle error: {data.get('message', 'Unknown error')}")
    
    async def handle_chat_message(self, data):
        """Handle chat messages with speed detection"""
        try:
            user_data = data.get("user", {})
            user_name = user_data.get("name", "Anonymous")
            message_text = data.get("text", "")
            
            if not message_text.strip():
                return
            
            # Record timestamp for speed tracking
            current_time = time.time()
            self.message_timestamps.append(current_time)
            
            # Add to buffer
            formatted_message = f"{user_name}: {message_text}"
            self.chat_buffer.append(formatted_message)
            
            logger.info(f"Chat: {formatted_message}")
            
            # Check if we should process messages
            await self.check_and_process_messages()
                
        except Exception as e:
            logger.error(f"Error handling chat message: {e}")
    
    async def check_and_process_messages(self):
        """Decide processing method based on chat speed"""
        if len(self.chat_buffer) < 3:
            return
            
        chat_speed = self.calculate_chat_speed()
        logger.info(f"Chat speed: {chat_speed:.1f} messages/minute")
        
        if chat_speed >= FAST_CHAT_THRESHOLD and len(self.chat_buffer) >= MIN_MESSAGES_FOR_GROQ:
            await self.process_with_groq()
        elif len(self.chat_buffer) >= 5:
            self.process_with_random_selection()
    
    async def process_with_groq(self):
        """Process with Groq summarization"""
        if not self.groq_summarizer.is_available():
            logger.warning("Groq not available, using random selection")
            self.process_with_random_selection()
            return
            
        try:
            summary = self.groq_summarizer.summarize_chat_messages(self.chat_buffer)
            
            if summary:
                processed_text = f"Chat summary: {summary}"
                self.summary_queue.put(processed_text)
                logger.info(f"Groq summary: {processed_text}")
            else:
                self.process_with_random_selection()
            
            self.chat_buffer.clear()
            
        except Exception as e:
            logger.error(f"Error in Groq processing: {e}")
            self.process_with_random_selection()
    
    def process_with_random_selection(self):
        """Process with random message selection"""
        if len(self.chat_buffer) < 3:
            return
            
        try:
            sample_size = min(RANDOM_SAMPLE_SIZE, len(self.chat_buffer))
            selected_messages = random.sample(self.chat_buffer, sample_size)
            
            if len(selected_messages) == 1:
                summary = f"Recent chat: {selected_messages[0]}"
            else:
                users = [msg.split(":", 1)[0] for msg in selected_messages if ":" in msg]
                unique_users = list(set(users))
                
                if len(unique_users) == 1:
                    summary = f"{unique_users[0]} is chatting"
                else:
                    summary = f"{len(unique_users)} people chatting"
            
            self.summary_queue.put(summary)
            logger.info(f"Random selection: {summary}")
            self.chat_buffer.clear()
            
        except Exception as e:
            logger.error(f"Error in random selection: {e}")
    
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
