"""Test the source switching animation"""

from obs_controller import SourceSwitchingOBSController
import time

def test_source_switching():
    print("Testing source switching functionality...")
    obs = SourceSwitchingOBSController()
    
    if obs.connect():
        print("✅ Connected - testing source switching...")
        
        
        # Test full animation
        print("🎭 Testing full animation for 5 seconds...")
        obs.start_animation()
        time.sleep(5)
        obs.stop_animation()
        
        obs.disconnect()
        print("✅ Test completed")
    else:
        print("❌ Connection failed")

if __name__ == "__main__":
    test_source_switching()
