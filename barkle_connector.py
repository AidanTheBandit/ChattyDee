"""Enhanced Barkle connector with configurable cooldown system"""

import asyncio
import websockets
import json
import queue
import logging
import time
import random
from collections import deque
from groq_summarizer import GroqSummarizer
from stream_id_helper import BarkleStreamHelper
from config import (
    BARKLE_TOKEN, BARKLE_TARGET_USER_ID, BARKLE_STREAM_ID, 
    BARKLE_AUTO_DETECT_STREAM, FAST_CHAT_THRESHOLD, CHAT_SPEED_WINDOW, 
    MIN_MESSAGES_FOR_GROQ, RANDOM_SAMPLE_SIZE, STREAM_CHECK_INTERVAL,
    COOLDOWN, TIMEOUT  # New cooldown imports
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedBarkleConnector:
    def __init__(self):
        self.token = BARKLE_TOKEN
        self.target_user_id = BARKLE_TARGET_USER_ID
        self.ws_url = "wss://barkle.chat/streaming"
        self.chat_buffer = []
        self.summary_queue = queue.Queue()
        self.connected = False
        self.message_timestamps = deque(maxlen=100)
        self.groq_summarizer = GroqSummarizer()
        self.connection_id = f"chatty-{int(time.time())}-{random.randint(1000, 9999)}"
        self._last_process_time = time.time()
        self._last_response_time = 0  # Track when we last responded
        
        # Stream ID configuration
        self.current_stream_id = BARKLE_STREAM_ID
        self.stream_helper = BarkleStreamHelper(self.token) if BARKLE_AUTO_DETECT_STREAM else None
        
    async def connect_to_chat(self):
        """Enhanced connection with dynamic stream ID detection"""
        # Step 1: Get stream ID if not configured
        if not self.current_stream_id and BARKLE_AUTO_DETECT_STREAM:
            logger.info("🔍 No stream ID configured, detecting automatically...")
            await self._detect_stream_id()
        
        # Step 2: Validate we have a stream ID
        if not self.current_stream_id:
            logger.error("❌ No stream ID available. Please configure BARKLE_STREAM_ID or enable auto-detection.")
            return
        
        # Step 3: Connect to WebSocket
        await self._websocket_connection_loop()
    
    async def _detect_stream_id(self):
        """Detect stream ID dynamically"""
        if not self.stream_helper or not self.target_user_id:
            logger.warning("Stream detection requires BARKLE_TARGET_USER_ID to be configured")
            return
        
        logger.info(f"🎯 Checking if {self.target_user_id} is live...")
        
        try:
            stream_data = await self.stream_helper.get_stream_data(self.target_user_id)
            
            if stream_data and stream_data.get("isActive"):
                self.current_stream_id = stream_data.get("id")
                logger.info(f"🔴 Found live stream!")
                logger.info(f"   Stream ID: {self.current_stream_id}")
                logger.info(f"   Title: {stream_data.get('title', 'Untitled')}")
                logger.info(f"   Viewers: {stream_data.get('viewers', 0)}")
            else:
                logger.warning(f"⚫ {self.target_user_id} is not currently live")
                
                if BARKLE_AUTO_DETECT_STREAM:
                    logger.info("⏳ Waiting for user to go live...")
                    await self._monitor_for_live_stream()
                    
        except Exception as e:
            logger.error(f"Error detecting stream: {e}")
    
    async def _monitor_for_live_stream(self):
        """Monitor target user until they go live"""
        while not self.current_stream_id:
            try:
                await asyncio.sleep(STREAM_CHECK_INTERVAL)
                
                stream_data = await self.stream_helper.get_stream_data(self.target_user_id)
                
                if stream_data and stream_data.get("isActive"):
                    self.current_stream_id = stream_data.get("id")
                    logger.info(f"🎉 {self.target_user_id} went live! Stream ID: {self.current_stream_id}")
                    break
                else:
                    logger.info(f"⏳ Still waiting for {self.target_user_id} to go live...")
                    
            except Exception as e:
                logger.error(f"Error monitoring for live stream: {e}")
                await asyncio.sleep(STREAM_CHECK_INTERVAL)
    
    async def _websocket_connection_loop(self):
        """Main WebSocket connection loop"""
        logger.info(f"📡 Connecting to stream chat: {self.current_stream_id}")
        
        while True:
            try:
                uri = f"{self.ws_url}?i={self.token}"
                logger.info(f"Connecting to Barkle streaming: {uri}")
                
                async with websockets.connect(uri) as websocket:
                    self.connected = True
                    logger.info("✅ Successfully connected to Barkle streaming")
                    
                    # Subscribe to stream chat
                    await self.subscribe_to_stream_chat(websocket)
                    
                    # Listen for messages
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            await self.process_streaming_message(data)
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON decode error: {e}")
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
    
    async def subscribe_to_stream_chat(self, websocket):
        """Subscribe to the stream chat channel"""
        try:
            subscribe_message = {
                "type": "connect",
                "body": {
                    "channel": "streamChat",
                    "id": self.connection_id,
                    "params": {
                        "streamId": self.current_stream_id
                    }
                }
            }
            
            await websocket.send(json.dumps(subscribe_message))
            logger.info(f"📺 Subscribed to stream chat for stream ID: {self.current_stream_id}")
            
        except Exception as e:
            logger.error(f"Failed to subscribe to stream chat: {e}")
    
    async def process_streaming_message(self, data):
        """Process incoming streaming messages"""
        try:
            message_type = data.get("type")
            
            if message_type == "connected" and data.get("body", {}).get("id") == self.connection_id:
                logger.info("✅ Successfully connected to stream chat channel")
                
            elif message_type == "channel" and data.get("body", {}).get("id") == self.connection_id:
                body = data.get("body", {})
                
                if body.get("type") == "message":
                    await self.handle_stream_chat_message(body.get("body", {}))
                elif body.get("type") == "deleted":
                    await self.handle_message_deletion(body.get("body", {}))
                    
        except Exception as e:
            logger.error(f"Error processing streaming message: {e}")
    
    async def handle_stream_chat_message(self, message_data):
        """Handle incoming stream chat messages"""
        try:
            user_info = message_data.get("user", {})
            user_name = user_info.get("name", user_info.get("username", "Anonymous"))
            message_text = message_data.get("text", "")
            
            if not message_text.strip():
                return
                
            # Record timestamp for speed tracking
            current_time = time.time()
            self.message_timestamps.append(current_time)
            
            # Add to buffer
            formatted_message = f"{user_name}: {message_text}"
            self.chat_buffer.append(formatted_message)
            
            logger.info(f"Stream Chat: {formatted_message}")
            
            # Check if we should process messages
            await self.check_and_process_messages()
                
        except Exception as e:
            logger.error(f"Error handling stream chat message: {e}")
    
    async def handle_message_deletion(self, deletion_data):
        """Handle message deletion events"""
        message_id = deletion_data.get("messageId", "")
        logger.info(f"Message {message_id} deleted")
    
    async def check_and_process_messages(self):
        """Enhanced processing logic with cooldown"""
        buffer_length = len(self.chat_buffer)
        
        if buffer_length < 1:
            return
        
        current_time = time.time()
        time_since_last_response = current_time - self._last_response_time
        chat_speed = self.calculate_chat_speed()
        
        logger.info(f"Chat speed: {chat_speed:.1f} msg/min, Buffer: {buffer_length}")
        
        # Check cooldown - prevent too frequent responses
        if time_since_last_response < COOLDOWN:
            remaining_cooldown = COOLDOWN - time_since_last_response
            logger.info(f"⏳ Cooldown active: {remaining_cooldown:.1f}s remaining")
            return
        
        # Processing logic with configurable thresholds
        if chat_speed >= FAST_CHAT_THRESHOLD and buffer_length >= MIN_MESSAGES_FOR_GROQ:
            logger.info(f"🚀 Using Groq (fast chat: {chat_speed:.1f} msg/min)")
            await self.process_with_groq()
        elif buffer_length >= 1:
            logger.info(f"🎲 Using random selection ({buffer_length} messages)")
            self.process_with_random_selection()
        
        # Fallback timeout processing (after cooldown expires)
        elif buffer_length >= 1 and self._should_process_timeout():
            logger.info(f"⏰ Timeout processing ({buffer_length} messages)")
            self.process_with_random_selection()
    
    def _should_process_timeout(self):
        """Check if we should process due to timeout"""
        current_time = time.time()
        time_since_last_response = current_time - self._last_response_time
        time_since_last_process = current_time - self._last_process_time
        
        # Only timeout if cooldown has expired and we haven't processed in a while
        return (time_since_last_response >= COOLDOWN and 
                time_since_last_process >= TIMEOUT)
    
    async def process_with_groq(self):
        """Process with Groq summarization"""
        if not self.groq_summarizer.is_available():
            logger.warning("Groq not available, using random selection")
            self.process_with_random_selection()
            return
            
        try:
            summary = self.groq_summarizer.summarize_chat_messages(self.chat_buffer)
            
            if summary:
                processed_text = f"Chat buzz: {summary}"
                self.summary_queue.put(processed_text)
                logger.info(f"Groq summary: {processed_text}")
                
                # Update response time
                self._last_response_time = time.time()
            else:
                self.process_with_random_selection()
            
            self.chat_buffer.clear()
            self._last_process_time = time.time()
            
        except Exception as e:
            logger.error(f"Error in Groq processing: {e}")
            self.process_with_random_selection()
    
    def process_with_random_selection(self):
        """Process with actual message content - SINGLE MESSAGE ONLY"""
        try:
            if not self.chat_buffer:
                return
            
            # Always pick just ONE message, regardless of buffer size
            selected_message = random.choice(self.chat_buffer)
            
            if ":" in selected_message:
                user_name = selected_message.split(':', 1)[0].strip()
                content = selected_message.split(':', 1)[1].strip()
                summary = f"{content}"  # Just the content
            else:
                summary = f"{selected_message}"
            
            self.summary_queue.put(summary)
            logger.info(f"Random selection: {summary}")
            
            # Update response time
            self._last_response_time = time.time()
            
            self.chat_buffer.clear()
            self._last_process_time = time.time()
            
        except Exception as e:
            logger.error(f"Error in random selection: {e}")
            if self.chat_buffer:
                simple_summary = f"Chat activity from {len(self.chat_buffer)} viewers"
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
    
    def get_current_stream_info(self):
        """Get current stream information"""
        return {
            "stream_id": self.current_stream_id,
            "connected": self.connected,
            "target_user": self.target_user_id,
            "auto_detect": BARKLE_AUTO_DETECT_STREAM,
            "cooldown": COOLDOWN,
            "timeout": TIMEOUT
        }
    
    def get_cooldown_status(self):
        """Get current cooldown status"""
        current_time = time.time()
        time_since_last_response = current_time - self._last_response_time
        remaining_cooldown = max(0, COOLDOWN - time_since_last_response)
        
        return {
            "cooldown_active": remaining_cooldown > 0,
            "remaining_seconds": remaining_cooldown,
            "last_response_time": self._last_response_time
        }
