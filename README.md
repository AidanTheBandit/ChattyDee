# Chatty Dee

## Overview

Chatty Dee monitors live chat messages from streams and creates an animated character that:
- **Listens** to live chat messages via WebSocket
- **Processes** messages intelligently using Groq AI or random selection
- **Speaks** responses using Google Text-to-Speech
- **Animates** with synchronized lip movements and stretching effects in OBS Studio

## 🎪 Features

### Core Functionality
- **Live Chat Integration**: Real-time WebSocket connection to Barkle streaming
- **AI Summarization**: Uses Groq AI for intelligent chat summarization during busy periods
- **Dynamic Processing**: Switches between AI and random selection based on chat activity
- **Configurable Cooldowns**: Prevents spam with customizable response timing
- **Stream Detection**: Automatically detects when target users go live

### Animation System
- **Source Switching**: Smooth transitions between normal and stretched character states
- **Lip Sync**: Synchronized open/closed lip animations during speech
- **OBS Integration**: Direct control of OBS Studio sources via WebSocket
- **Responsive Timing**: 200ms animation cycles for smooth visual feedback

## Prerequisites

### Software Requirements
- **Python 3.8+**
- **OBS Studio 28+** (with WebSocket server support)
- **Active internet connection** for TTS and API services

### API Keys & Tokens
- **Barkle Access Token**: Required for chat access
- **Groq API Key**: Optional, for AI summarization (get from [console.groq.com](https://console.groq.com))

## Installation

### 1. Clone and Setup Environment
```bash
# Create project directory
mkdir chatty_dee_barkle
cd chatty_dee_barkle

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install obs-websocket-py groq pygame gtts websockets pillow numpy opencv-python
```

### 3. Project Structure
Create the following files in your project directory:
```
chatty_dee_barkle/
├── main.py
├── barkle_connector.py
├── groq_summarizer.py
├── tts_handler.py
├── obs_controller.py
├── lip_overlay.py
├── stream_id_helper.py
├── config.py
├── cli_mode.py
├── assets/
│   ├── chatty.png
│   ├── chatty-stretch.png
│   ├── lips.png
│   └── lips-open.png
└── README.md
```

## ⚙️ Configuration

### 1. Configure API Keys
Edit `config.py` with your actual credentials:

```python
# Barkle Configuration
BARKLE_TOKEN = "your_barkle_access_token_here"
BARKLE_TARGET_USER_ID = "barkle_id" # Can be found at https://barkle.chat/settings/account-info (ex. 969n412bwp)
BARKLE_STREAM_ID = "None"  # Go to https://barkle.chat/api-console and set the endpoint to live/get then enter your id. After clicking send, in the response copy the ID (ex. 02n4Rf...)
BARKLE_AUTO_DETECT_STREAM = True

# Groq Configuration (Optional)
GROQ_API_KEY = "your_groq_api_key_here"
GROQ_MODEL = "llama-3.3-70b-versatile"

# Response Timing
COOLDOWN = 20  # Seconds between responses
TIMEOUT = 30   # Timeout for processing messages

# OBS Configuration
OBS_HOST = "localhost"
OBS_PORT = 4455  # Use 4455 for OBS 30+, 4444 for older versions
OBS_PASSWORD = ""  # Set if OBS WebSocket has password

# Scene and Source Names
MAIN_SCENE = "chatty"
CHATTY_SOURCE = "Chatty"
LIPS_CLOSED_SOURCE = "lips"
LIPS_OPEN_SOURCE = "lips-open"
```

### 2. Chat Processing Settings
```python
# Chat Speed Detection
FAST_CHAT_THRESHOLD = 5      # Messages/minute to trigger Groq
MIN_MESSAGES_FOR_GROQ = 4    # Minimum messages for AI processing
RANDOM_SAMPLE_SIZE = 3       # Messages to sample for selection

# TTS Settings
TTS_LANGUAGE = "en"
TTS_SLOW = False
```

## 🎬 OBS Studio Setup

### 1. Enable WebSocket Server
1. Open **OBS Studio**
2. Go to **Tools → WebSocket Server Settings**
3. ✅ **Enable WebSocket Server**
4. Set **Server Port**: `4455` (for OBS 30+) or `4444` (older versions)
5. Set **Server Password** (optional, update config if used)
6. Click **Apply** and **OK**

### 2. Create Scene and Sources
1. **Create Scene**:
   - Name: `chatty` (must match `MAIN_SCENE` in config)

2. **Add Character Sources**:
   - **Source Name**: `Chatty` (normal character image)
   - **Source Name**: `Chatty-stretch` (stretched character image)
   - Position both sources in the exact same location
   - Initially show `Chatty`, hide `Chatty-stretch`

3. **Add Lip Sources**:
   - **Source Name**: `lips` (closed lips overlay)
   - **Source Name**: `lips-open` (open lips overlay)
   - Position both over the character's mouth area
   - Initially show `lips`, hide `lips-open`

### 3. Source Positioning
- **Chatty Sources**: Position where you want the character to appear
- **Lip Sources**: Overlay precisely on the character's mouth area
- **Initial State**: Only `Chatty` and `lips` should be visible

### 4. Using
- Anywhere you want Chatty to appear you can add your Chatty scene as a source and it will work!

## Usage

### 1. Basic Operation
```bash
# Start the main application
python main.py
```

## Configuration Examples

### Conservative Setup (Less Frequent Responses)
```python
COOLDOWN = 30          # 30 seconds between responses
TIMEOUT = 60           # 1 minute timeout
FAST_CHAT_THRESHOLD = 8 # Higher threshold for AI
```

### Responsive Setup (More Frequent Responses)
```python
COOLDOWN = 10          # 10 seconds between responses
TIMEOUT = 20           # 20 second timeout
FAST_CHAT_THRESHOLD = 3 # Lower threshold for AI
```

### AI Setup
```python
GROQ_API_KEY = "your_key_here"
MIN_MESSAGES_FOR_GROQ = 2  # Use AI more frequently
FAST_CHAT_THRESHOLD = 3    # Lower threshold
```

## Customization

### Creating Character Assets
1. **Chatty.png**: Your normal character image
2. **Chatty-stretch.png**: Vertically stretched version (same width)
3. **lips.png**: Closed lips overlay (transparent background)
4. **lips-open.png**: Open lips overlay (transparent background)

### Animation Timing
```python
ANIMATION_SPEED = 0.2  # Animation cycle speed (seconds)
SUMMARY_DELAY = 2      # Pause after speech completion
```

### Message Processing
```python
# Customize how messages are processed
RANDOM_SAMPLE_SIZE = 3     # How many messages to sample
CHAT_SPEED_WINDOW = 60     # Time window for speed calculation
```
