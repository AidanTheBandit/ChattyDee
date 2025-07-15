"""Quick TTS and animation test script"""

import time
import asyncio
from obs_controller import SourceSwitchingOBSController
from tts_handler import SimplifiedTTSHandler

def test_tts_with_animation():
    print("🎤 Testing TTS with Source Switching Animation")
    print("="*50)
    
    # Initialize components
    obs = SourceSwitchingOBSController()
    tts = SimplifiedTTSHandler()
    
    # Connect TTS to OBS
    tts.set_obs_controller(obs)
    
    # Test phrases
    test_phrases = [
        "Hello everyone, welcome to the stream!",
        "Chat is looking really active today!",
        "Thanks for all the follows and subscriptions!",
        "We're having such an amazing time here!",
        "Don't forget to hit that notification bell!"
    ]
    
    # Connect to OBS
    if not obs.connect():
        print("❌ Failed to connect to OBS")
        print("💡 Make sure OBS is running with the WebSocket server enabled")
        return
    
    print("✅ Connected to OBS!")
    print("🎭 Testing TTS with animation...\n")
    
    for i, phrase in enumerate(test_phrases, 1):
        print(f"[{i}/{len(test_phrases)}] Speaking: \"{phrase}\"")
        
        # Generate and play TTS with animation
        audio_file = tts.text_to_speech(phrase)
        if audio_file:
            tts.play_speech(audio_file)
            
            # Wait for completion
            while tts.is_playing():
                time.sleep(0.1)
        else:
            print(f"❌ Failed to generate TTS for phrase {i}")
        
        print(f"✅ Completed phrase {i}")
        time.sleep(1)  # Brief pause between phrases
    
    # Disconnect
    obs.disconnect()
    print("\n🎉 All TTS animation tests completed!")

if __name__ == "__main__":
    test_tts_with_animation()
