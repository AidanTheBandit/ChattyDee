# Chatty Dee

## Overview
## ✅ MULTIPLATFORM SUPPORT NOW AVAILABLE!

Chatty Dee monitors live chat messages from multiple streaming platforms and creates an animated character that:
- **Listens** to live chat messages from Barkle, YouTube, and Twitch
- **Processes** messages intelligently using Groq AI or random selection
- **Speaks** responses using Google Text-to-Speech
- **Animates** with synchronized lip movements and stretching effects in OBS Studio

## 🎪 Features

### Core Functionality
- **Multi-Platform Chat Integration**: Real-time connections to Barkle, YouTube, and Twitch
- **AI Summarization**: Uses Groq AI for intelligent chat summarization during busy periods
- **Dynamic Processing**: Switches between AI and random selection based on chat activity
- **Configurable Cooldowns**: Prevents spam with customizable response timing
- **Stream Detection**: Automatically detects when target users go live (Barkle)
- **Unified Message Queue**: Seamlessly handles messages from all platforms

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
- **Barkle Access Token**: Optional, for Barkle chat access
- **YouTube Video ID**: Optional, for YouTube live chat monitoring
- **Twitch Credentials**: Optional, for Twitch chat access (Bot Token, Client ID)
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
pip install obs-websocket-py groq pygame gtts websockets pillow numpy opencv-python pytchat twitchio requests
```

### 3. Project Structure
Create the following files in your project directory:
```
chatty_dee/
├── main.py
├── platform_manager.py
├── barkle_connector.py
├── youtube_connector.py
├── twitch_connector.py
├── groq_summarizer.py
├── tts_handler.py
├── obs_controller.py
├── stream_id_helper.py
├── config.py
├── assets/
│   ├── chatty.png
│   ├── chatty-stretch.png
│   ├── lips.png
│   └── lips-open.png
└── README.md
```

## ⚙️ Configuration

### 1. Platform Selection
Edit `config.py` to enable/disable platforms:

```python
# Platform Configuration
ENABLED_PLATFORMS = ["barkle", "youtube", "twitch"]  # Enable the platforms you want to use
```

You can enable any combination of platforms:
- `["barkle"]` - Only Barkle
- `["youtube"]` - Only YouTube
- `["twitch"]` - Only Twitch
- `["barkle", "youtube"]` - Barkle and YouTube
- `["barkle", "youtube", "twitch"]` - All platforms

### 2. Configure Platform Credentials

#### Barkle Configuration
```python
# Barkle Configuration
BARKLE_TOKEN = "your_barkle_access_token_here"
BARKLE_TARGET_USER_ID = "barkle_id" # Can be found at https://barkle.chat/settings/account-info (ex. 969n412bwp)
BARKLE_STREAM_ID = "None"  # Go to https://barkle.chat/api-console and set the endpoint to live/get then enter your id. After clicking send, in the response copy the ID (ex. 02n4Rf...)
BARKLE_AUTO_DETECT_STREAM = True
```

#### YouTube Configuration
```python
# YouTube Configuration
YOUTUBE_VIDEO_ID = None  # Will auto-detect if None, or provide specific video ID (e.g., "dQw4w9WgXcQ")
YOUTUBE_CHANNEL_ID = None  # Optional: monitor specific channel
```

**How to get YouTube Video ID:**
1. Go to your YouTube live stream
2. Copy the video ID from the URL: `youtube.com/watch?v=VIDEO_ID_HERE`
3. Paste it in the config

#### Twitch Configuration
```python
# Twitch Configuration
TWITCH_BOT_TOKEN = "your_twitch_bot_token_here"
TWITCH_CLIENT_ID = "your_twitch_client_id_here"
TWITCH_CHANNEL = "your_twitch_channel_here"
TWITCH_BOT_NICK = "your_bot_nickname"
```

**How to get Twitch credentials:**
1. Go to [dev.twitch.tv](https://dev.twitch.tv/console/apps)
2. Create an application to get your Client ID
3. Generate an OAuth token at [twitchapps.com/tmi](https://twitchapps.com/tmi/)
4. Set the channel name (without the #) and bot nickname

### 3. Additional Settings

#### Groq Configuration (Optional)
```python
# Groq Configuration (Optional)
GROQ_API_KEY = "your_groq_api_key_here"
GROQ_MODEL = "llama-3.3-70b-versatile"
```

#### Response Timing
```python
# Response Timing
COOLDOWN = 20  # Seconds between responses
TIMEOUT = 30   # Timeout for processing messages
```

#### OBS Configuration
```python
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

### 4. Chat Processing Settings
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
# Start the multi-platform application
python main.py
```

The application will:
1. Connect to OBS Studio
2. Connect to all enabled platforms (Barkle, YouTube, Twitch)
3. Start monitoring chat messages from all connected platforms
4. Process and speak messages using TTS with animated character

### 2. Platform-Specific Usage

#### Single Platform
To use only one platform, edit your `config.py`:
```python
ENABLED_PLATFORMS = ["youtube"]  # Only YouTube
```

#### Multiple Platforms
To use multiple platforms simultaneously:
```python
ENABLED_PLATFORMS = ["barkle", "youtube", "twitch"]  # All platforms
```

Messages from all enabled platforms will be processed together in a unified queue.

## Configuration Examples

### Multi-Platform Setup
```python
# Enable all platforms
ENABLED_PLATFORMS = ["barkle", "youtube", "twitch"]

# Configure each platform
BARKLE_TOKEN = "your_barkle_token"
YOUTUBE_VIDEO_ID = "your_video_id"
TWITCH_CHANNEL = "your_channel"
```

### YouTube-Only Setup
```python
ENABLED_PLATFORMS = ["youtube"]
YOUTUBE_VIDEO_ID = "dQw4w9WgXcQ"  # Your live stream video ID
GROQ_API_KEY = "your_key_here"    # Optional: for AI summaries
```

### Twitch-Only Setup
```python
ENABLED_PLATFORMS = ["twitch"]
TWITCH_BOT_TOKEN = "oauth:your_token"
TWITCH_CLIENT_ID = "your_client_id"
TWITCH_CHANNEL = "your_channel"
TWITCH_BOT_NICK = "ChattyDeeBot"
```

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

### AI-Enhanced Setup
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

## 🔧 Troubleshooting

### Platform-Specific Issues

#### YouTube
- **"pytchat library not available"**: Install with `pip install pytchat`
- **"Failed to connect to YouTube chat"**: Ensure the video ID is correct and the stream is live
- **No messages appearing**: Check if the stream has chat enabled and is actually live

#### Twitch
- **"twitchio library not available"**: Install with `pip install twitchio`
- **Authentication failed**: Verify your OAuth token and Client ID are correct
- **Can't connect to channel**: Ensure channel name doesn't include the # symbol

#### Barkle
- **"No stream ID available"**: Make sure the user is live or set a specific stream ID
- **Connection closed**: Check your Barkle access token is valid

### General Issues
- **No platforms connecting**: Check `ENABLED_PLATFORMS` in config.py
- **OBS connection failed**: Verify OBS WebSocket is enabled and port is correct
- **No speech output**: Check your audio device settings and pygame installation

## 🚀 Advanced Features

### Running Multiple Platforms Simultaneously
Chatty Dee can monitor all platforms at once and process messages from any platform in a unified queue:

```python
ENABLED_PLATFORMS = ["barkle", "youtube", "twitch"]
```

All messages are processed with the same cooldown and processing logic, regardless of which platform they came from.

### Platform Priority
Messages are processed in the order they arrive, regardless of platform. The unified queue ensures fair processing across all platforms.

## 📝 Notes

- Each platform connector runs independently with its own connection
- The platform manager aggregates all messages into a single queue
- All platforms share the same cooldown timer to prevent spam
- Messages include platform identification in logs for debugging
- You can enable/disable platforms on the fly by editing `config.py` and restarting
