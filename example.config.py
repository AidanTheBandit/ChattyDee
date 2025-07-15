"""Enhanced configuration for Chatty Dee Barkle with Groq"""

# Barkle API Configuration
BARKLE_TOKEN = "TOKEN_PLACEHOLDER"  # Replace with your actual token
BARKLE_WS_URL = "wss://barkle.chat/ws/chat"

# Groq API Configuration
GROQ_API_KEY = "GROQ_HERE"  # Get from https://console.groq.com
GROQ_MODEL = "llama-3.3-70b-versatile"  # Fast model for summarization

# Chat Speed Detection
FAST_CHAT_THRESHOLD = 10  # Messages per minute to trigger Groq summarization
CHAT_SPEED_WINDOW = 60    # Time window in seconds to measure chat speed
MIN_MESSAGES_FOR_GROQ = 8 # Minimum messages needed before using Groq
RANDOM_SAMPLE_SIZE = 3    # Number of random messages to select for slow chat

# OBS Configuration (Updated for your setup)
OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = "PASSWORD_PLACEHOLDER"  # Replace with your actual OBS password

# Scene and Source Names
MAIN_SCENE = "chatty"
CHATTY_SOURCE = "Chatty"              # Normal character
CHATTY_STRETCH_SOURCE = "Chatty-stretch"  # Stretched character
LIPS_CLOSED_SOURCE = "lips"           # Closed lips
LIPS_OPEN_SOURCE = "lips-open"        # Open lips

# Animation Settings
ANIMATION_SPEED = 0.5  # 200ms switching interval

# TTS Settings
TTS_LANGUAGE = "en"
TTS_SLOW = False
SUMMARY_DELAY = 2