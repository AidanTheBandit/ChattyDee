"""Enhanced configuration with dynamic stream ID support"""

# Barkle API Configuration
BARKLE_TOKEN = "your_barkle_token_here"
BARKLE_TARGET_USER_ID = "barkle:username_to_monitor"  

# Stream Configuration Options
BARKLE_STREAM_ID = None 
BARKLE_AUTO_DETECT_STREAM = True

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
