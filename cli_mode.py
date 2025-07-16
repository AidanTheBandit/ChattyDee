"""Enhanced CLI mode with TTS testing for source switching"""

import asyncio
import time
import random
import threading
from groq_summarizer import GroqSummarizer
from tts_handler import SimplifiedTTSHandler
from obs_controller import SourceSwitchingOBSController
from config import (
    FAST_CHAT_THRESHOLD, MIN_MESSAGES_FOR_GROQ, 
    RANDOM_SAMPLE_SIZE
)

class CLIChattyDeeWithTTS:
    def __init__(self):
        self.groq_summarizer = GroqSummarizer()
        self.obs = SourceSwitchingOBSController()
        self.tts = SimplifiedTTSHandler()
        self.chat_buffer = []
        self.message_timestamps = []
        
        # Connect TTS to OBS
        self.tts.set_obs_controller(self.obs)
        
        self.sample_users = [
            "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", 
            "Grace", "Henry", "Ivy", "Jack", "Kate", "Leo"
        ]
        
        self.sample_messages = [
            "Hey everyone! How's the stream going?",
            "Just finished an amazing game session",
            "Anyone want to team up for co-op later?",
            "I absolutely love this new update!",
            "The weather is really beautiful today",
            "Working on some exciting coding projects",
            "What's everyone planning for the weekend?",
            "Just grabbed some fresh coffee, feeling great",
            "This stream content is absolutely fantastic",
            "Can't wait to see what happens next",
            "Learning some cool new skills today",
            "Such an awesome community here",
            "Thanks for all the helpful tips everyone",
            "Really excited about the upcoming event",
            "Having such a productive day so far",
            "These new features look incredible",
            "Good morning chat, hope you're all well",
            "Time for a well-deserved break",
            "Really enjoying this discussion",
            "Let's keep this positive energy going"
        ]
    
    def print_banner(self):
        """Print enhanced CLI banner"""
        print("\n" + "="*70)
        print("🎤 CHATTY DEE BARKLE - CLI TESTING WITH TTS & ANIMATION 🎤")
        print("="*70)
        print("Commands:")
        print("  'sim fast' - Simulate fast chat (triggers Groq + TTS)")
        print("  'sim slow' - Simulate slow chat (random selection + TTS)")
        print("  'sim <number>' - Simulate specific number with TTS")
        print("  'add <user> <message>' - Add custom message")
        print("  'process' - Process current buffer with TTS")
        print("  'tts <text>' - Test TTS directly with custom text")
        print("  'test-phrases' - Test with pre-made phrases")
        print("  'connect-obs' - Connect to OBS for animation")
        print("  'clear' - Clear message buffer")
        print("  'status' - Show current status")
        print("  'help' - Show this help")
        print("  'quit' - Exit")
        print("="*70 + "\n")
    
    def connect_obs(self):
        """Connect to OBS for testing"""
        print("🔌 Connecting to OBS...")
        if self.obs.connect():
            print("✅ Connected to OBS - animation ready!")
            return True
        else:
            print("❌ Failed to connect to OBS")
            print("💡 Make sure OBS is running with WebSocket server enabled")
            return False
    
    def simulate_chat_messages(self, count=5, fast_mode=False):
        """Simulate chat messages"""
        print(f"\n📨 Simulating {count} messages...")
        
        for i in range(count):
            user = random.choice(self.sample_users)
            message = random.choice(self.sample_messages)
            
            # Add some variation
            if random.random() < 0.3:
                variations = [
                    f"@{random.choice(self.sample_users)} {message}",
                    f"{message} 😊",
                    f"LOL {message}",
                    f"{message} What do you think?",
                    f"Honestly, {message.lower()}"
                ]
                message = random.choice(variations)
            
            self.add_message(user, message)
            
            if not fast_mode:
                print(f"  [{i+1}/{count}] {user}: {message}")
            
            if fast_mode:
                time.sleep(0.1)
    
    def add_message(self, user, text):
        """Add message to buffer"""
        current_time = time.time()
        self.message_timestamps.append(current_time)
        
        formatted_message = f"{user}: {text}"
        self.chat_buffer.append(formatted_message)
        
        # Keep recent timestamps
        cutoff_time = current_time - 60
        self.message_timestamps = [
            ts for ts in self.message_timestamps if ts >= cutoff_time
        ]
    
    def calculate_chat_speed(self):
        """Calculate chat speed"""
        if not self.message_timestamps:
            return 0.0
        return len(self.message_timestamps)
    
    def process_messages(self):
        """Process current buffer with TTS"""
        if not self.chat_buffer:
            print("❌ No messages to process")
            return
        
        chat_speed = self.calculate_chat_speed()
        
        print(f"\n⚡ Processing {len(self.chat_buffer)} messages...")
        print(f"📊 Chat speed: {chat_speed:.1f} messages/minute")
        
        # Show messages
        print("\n📝 Messages:")
        for i, msg in enumerate(self.chat_buffer, 1):
            print(f"  {i}. {msg}")
        
        # Process with TTS - Updated thresholds
        if chat_speed >= FAST_CHAT_THRESHOLD and len(self.chat_buffer) >= MIN_MESSAGES_FOR_GROQ:
            print(f"\n🚀 Using Groq (fast chat)")
            self.process_with_groq_and_tts()
        elif len(self.chat_buffer) >= 2:  # Lowered threshold
            print(f"\n🎲 Using random selection")
            self.process_with_random_and_tts()
        else:
            print(f"\n⚠️ Not enough messages (need at least 2)")
    
    def process_with_groq_and_tts(self):
        """Process with Groq and speak result"""
        if not self.groq_summarizer.is_available():
            print("❌ Groq not available")
            self.process_with_random_and_tts()
            return
        
        print("🧠 Generating Groq summary...")
        summary = self.groq_summarizer.summarize_chat_messages(self.chat_buffer)
        
        if summary:
            processed_text = f"Chat summary: {summary}"
            print(f"✅ Groq: {processed_text}")
            self.speak_with_animation(processed_text)
        else:
            print("❌ Groq failed")
            self.process_with_random_and_tts()
        
        self.chat_buffer.clear()
    
    def process_with_random_and_tts(self):
        """Process with random selection and speak result"""
        if len(self.chat_buffer) < 1:
            return
        
        sample_size = min(RANDOM_SAMPLE_SIZE, len(self.chat_buffer))
        selected = random.sample(self.chat_buffer, sample_size)
        
        print(f"🎯 Selected {sample_size} messages:")
        for i, msg in enumerate(selected, 1):
            print(f"  {i}. {msg}")
        
        if len(selected) == 1:
            summary = f"Recent chat: {selected[0]}"
        else:
            users = [msg.split(":", 1)[0] for msg in selected if ":" in msg]
            unique_users = list(set(users))
            if len(unique_users) == 1:
                summary = f"{unique_users[0]} is chatting"
            else:
                summary = f"{len(unique_users)} people are chatting"
        
        print(f"✅ Summary: {summary}")
        self.speak_with_animation(summary)
        self.chat_buffer.clear()
    
    def speak_with_animation(self, text):
        """Speak text with full animation"""
        print(f"\n🔊 Speaking: \"{text}\"")
        
        if self.obs.is_connected():
            print("🎭 Starting animation...")
            
            # Run TTS in a separate thread to avoid blocking
            def tts_thread():
                audio_file = self.tts.text_to_speech(text)
                if audio_file:
                    self.tts.play_speech(audio_file)
                else:
                    print("❌ TTS generation failed")
            
            threading.Thread(target=tts_thread, daemon=True).start()
            
        else:
            print("⚠️ OBS not connected - TTS only")
            audio_file = self.tts.text_to_speech(text)
            if audio_file:
                self.tts.play_speech(audio_file)
        
        print("="*50)
    
    def test_direct_tts(self, text):
        """Test TTS directly"""
        print(f"\n🔊 Testing TTS with: \"{text}\"")
        self.speak_with_animation(text)
    
    def test_predefined_phrases(self):
        """Test with predefined phrases"""
        phrases = [
            "Welcome to the stream everyone!",
            "Thanks for following, really appreciate it!",
            "Chat is getting really active today",
            "Someone just asked a great question",
            "We're having an amazing time here",
            "Don't forget to hit that subscribe button"
        ]
        
        print("\n🎪 Testing predefined phrases...")
        for i, phrase in enumerate(phrases, 1):
            print(f"\n[{i}/{len(phrases)}] Testing: {phrase}")
            self.speak_with_animation(phrase)
            
            # Wait for completion
            while self.tts.is_playing():
                time.sleep(0.1)
            
            time.sleep(1)  # Brief pause between phrases
        
        print("✅ All phrase tests completed!")
    
    def show_status(self):
        """Show enhanced status"""
        print(f"\n📊 SYSTEM STATUS:")
        print(f"  Messages in buffer: {len(self.chat_buffer)}")
        print(f"  Chat speed: {self.calculate_chat_speed():.1f} msg/min")
        print(f"  Groq available: {'✅' if self.groq_summarizer.is_available() else '❌'}")
        print(f"  TTS ready: {'✅' if self.tts else '❌'}")
        print(f"  OBS connected: {'✅' if self.obs.is_connected() else '❌'}")
        print(f"  Animation ready: {'✅' if self.obs.is_connected() else '❌'}")
        print(f"  Fast chat threshold: {FAST_CHAT_THRESHOLD} msg/min")
        print(f"  Min messages for Groq: {MIN_MESSAGES_FOR_GROQ}")
    
    def clear_buffer(self):
        """Clear buffer"""
        self.chat_buffer.clear()
        self.message_timestamps.clear()
        print("🧹 Buffer cleared")
    
    async def run(self):
        """Run enhanced CLI interface"""
        self.print_banner()
        
        while True:
            try:
                user_input = input("chatty-tts-cli> ").strip()
                
                if not user_input:
                    continue
                
                parts = user_input.split()
                command = parts[0].lower()
                
                if command in ["quit", "exit"]:
                    print("👋 Goodbye!")
                    if self.obs.is_connected():
                        self.obs.disconnect()
                    break
                
                elif command == "help":
                    self.print_banner()
                
                elif command == "status":
                    self.show_status()
                
                elif command == "clear":
                    self.clear_buffer()
                
                elif command == "connect-obs":
                    self.connect_obs()
                
                elif command == "process":
                    self.process_messages()
                
                elif command == "test-phrases":
                    if not self.obs.is_connected():
                        print("⚠️ Consider connecting to OBS first with 'connect-obs'")
                    self.test_predefined_phrases()
                
                elif command == "tts":
                    if len(parts) < 2:
                        print("❌ Usage: tts <your text here>")
                        continue
                    
                    text = " ".join(parts[1:])
                    self.test_direct_tts(text)
                
                elif command == "sim":
                    if len(parts) < 2:
                        print("❌ Usage: sim <fast|slow|number>")
                        continue
                    
                    subcommand = parts[1].lower()
                    
                    if subcommand == "fast":
                        self.simulate_chat_messages(10, fast_mode=True)  # More messages for fast mode
                    elif subcommand == "slow":
                        self.simulate_chat_messages(3, fast_mode=False)  # Fewer messages for slow mode
                    else:
                        try:
                            count = int(subcommand)
                            self.simulate_chat_messages(count)
                        except ValueError:
                            print("❌ Invalid number")
                
                elif command == "add":
                    if len(parts) < 3:
                        print("❌ Usage: add <user> <message>")
                        continue
                    
                    user = parts[1]
                    message = " ".join(parts[2:])
                    self.add_message(user, message)
                    print(f"✅ Added: {user}: {message}")
                
                else:
                    print(f"❌ Unknown command: {command}")
                    print("💡 Type 'help' for available commands")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                if self.obs.is_connected():
                    self.obs.disconnect()
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    cli = CLIChattyDeeWithTTS()
    asyncio.run(cli.run())
