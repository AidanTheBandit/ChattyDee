"""Test stretch functionality"""

from obs_controller import FixedOBSController
import time

def test_stretch():
    obs = FixedOBSController()
    
    if obs.connect():
        print("✅ Connected - testing stretch...")
        
        # Test stretch on
        obs._apply_stretch(True)
        time.sleep(2)
        
        # Test stretch off
        obs._apply_stretch(False)
        time.sleep(2)
        
        obs.disconnect()
        print("✅ Test completed")
    else:
        print("❌ Connection failed")

if __name__ == "__main__":
    test_stretch()
