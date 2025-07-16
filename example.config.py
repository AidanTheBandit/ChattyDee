"""Enhanced configuration with multi-platform support"""

# Platform Configuration
ENABLED_PLATFORMS = ["barkle", "youtube", "twitch"]  # Enable/disable platforms

# Barkle API Configuration
BARKLE_TOKEN = "your_barkle_token_here"
BARKLE_TARGET_USER_ID = "username_to_monitor"  

# Stream Configuration Options
BARKLE_STREAM_ID = "target_stream_id_here" 
BARKLE_AUTO_DETECT_STREAM = True

# YouTube Configuration
YOUTUBE_VIDEO_ID = None  # Will auto-detect if None, or provide specific video ID
YOUTUBE_CHANNEL_ID = None  # Optional: monitor specific channel

# Twitch Configuration
TWITCH_BOT_TOKEN = "your_twitch_bot_token_here"
TWITCH_CLIENT_ID = "your_twitch_client_id_here"
TWITCH_CHANNEL = "your_twitch_channel_here"
TWITCH_BOT_NICK = "your_bot_nickname"

# Groq API Configuration  
GROQ_API_KEY = "your_groq_api_key_here"
GROQ_MODEL = "llama-3.3-70b-versatile"

# Chat Speed Detection
FAST_CHAT_THRESHOLD = 5    
CHAT_SPEED_WINDOW = 60
MIN_MESSAGES_FOR_GROQ = 4  
RANDOM_SAMPLE_SIZE = 3

# OBS Configuration
OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = ""

# Scene and Source Names
MAIN_SCENE = "chatty"
CHATTY_SOURCE = "Chatty"
LIPS_CLOSED_SOURCE = "lips"
LIPS_OPEN_SOURCE = "lips-open"

# Animation Settings
ANIMATION_SPEED = 0.2

# TTS Settings
TTS_LANGUAGE = "en"
TTS_SLOW = False
SUMMARY_DELAY = 2

# Stream Monitoring
STREAM_CHECK_INTERVAL = 30 
