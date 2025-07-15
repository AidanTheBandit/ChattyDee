"""Test the complete chat processing pipeline"""

import asyncio
import time
from barkle_connector import EnhancedBarkleConnector
from obs_controller import SourceSwitchingOBSController
from tts_handler import SimplifiedTTSHandler
from groq_summarizer import GroqSummarizer

class FullPipelineTest:
    def __init__(self):
        self.obs = SourceSwitchingOBSController()
        self.tts = SimplifiedTTSHandler()
        self.groq = GroqSummarizer()
        
        # Connect components
        self.tts.set_obs_controller(self.obs)
        
    def test_groq_summarization(self):
        """Test Groq summarization with TTS"""
        print("🧠 Testing Groq Summarization + TTS")
        
        # Sample chat messages
        sample_messages = [
            "Alice: Hey everyone, how's the stream going today?",
            "Bob: This game looks amazing, loving the graphics!",
            "Charlie: @Alice the stream is fantastic, thanks for asking",
            "Diana: Just followed, this content is incredible!",
            "Eve: Can't wait to see what happens next",
            "Frank: The chat is so active today, love this community",
            "Grace: @Bob I agree, the graphics are stunning",
            "Henry: This is my first time watching, really impressed"
        ]
        
        if self.groq.is_available():
            summary = self.groq.summarize_chat_messages(sample_messages)
            if summary:
                print(f"📝 Groq Summary: {summary}")
                
                # Speak the summary
                if self.obs.is_connected():
                    audio_file = self.tts.text_to_speech(f"Chat summary: {summary}")
                    if audio_file:
                        print("🔊 Playing summary with animation...")
                        self.tts.play_speech(audio_file)
                        
                        # Wait for completion
                        while self.tts.is_playing():
                            time.sleep(0.1)
                        
                        print("✅ Groq test completed!")
                    else:
                        print("❌ TTS generation failed")
                else:
                    print("⚠️ OBS not connected - skipping animation")
            else:
                print("❌ Groq summarization failed")
        else:
            print("❌ Groq not available")
    
    def test_random_selection(self):
        """Test random message selection with TTS"""
        print("\n🎲 Testing Random Selection + TTS")
        
        import random
        sample_messages = [
            "Alice: Just hit a new high score!",
            "Bob: That was an epic play right there",
            "Charlie: Can someone explain the strategy?"
        ]
        
        selected = random.sample(sample_messages, 2)
        summary = f"Recent chat: {', '.join([msg.split(':', 1)[1].strip() for msg in selected])}"
        
        print(f"📝 Random Summary: {summary}")
        
        if self.obs.is_connected():
            audio_file = self.tts.text_to_speech(summary)
            if audio_file:
                print("🔊 Playing random selection with animation...")
                self.tts.play_speech(audio_file)
                
                # Wait for completion
                while self.tts.is_playing():
                    time.sleep(0.1)
                
                print("✅ Random selection test completed!")
    
    def run_tests(self):
        """Run all tests"""
        print("🚀 Starting Full Pipeline Tests")
        print("="*50)
        
        # Connect to OBS
        if not self.obs.connect():
            print("❌ Failed to connect to OBS")
            print("💡 Tests will run without animation")
        else:
            print("✅ Connected to OBS!")
        
        # Test Groq
        self.test_groq_summarization()
        
        # Wait between tests
        time.sleep(2)
        
        # Test random selection
        self.test_random_selection()
        
        # Cleanup
        if self.obs.is_connected():
            self.obs.disconnect()
        
        print("\n🎉 All tests completed!")

if __name__ == "__main__":
    test = FullPipelineTest()
    test.run_tests()
