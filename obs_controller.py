"""Source-switching OBS controller - much simpler and more reliable"""

import time
import threading
import logging
from obswebsocket import obsws, requests
from config import (
    OBS_HOST, OBS_PORT, OBS_PASSWORD, MAIN_SCENE, CHATTY_SOURCE, 
    LIPS_CLOSED_SOURCE, LIPS_OPEN_SOURCE
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SourceSwitchingOBSController:
    def __init__(self):
        self.ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
        self.connected = False
        self.source_ids = {}
        self.animation_running = False
        self.animation_thread = None
        
    def connect(self):
        """Connect and setup sources"""
        try:
            self.ws.connect()
            self.connected = True
            logger.info("✅ Connected to OBS WebSocket")
            
            self._get_source_ids()
            self._set_initial_state()
            return True
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False
    
    def _get_source_ids(self):
        """Get all source IDs"""
        try:
            response = self.ws.call(requests.GetSceneItemList(sceneName=MAIN_SCENE))
            items = response.datain.get('sceneItems', [])
            
            required_sources = [
                CHATTY_SOURCE, 
                "Chatty-stretch",  # New stretched source
                LIPS_CLOSED_SOURCE, 
                LIPS_OPEN_SOURCE
            ]
            
            for item in items:
                source_name = item.get('sourceName', '')
                if source_name in required_sources:
                    self.source_ids[source_name] = item.get('sceneItemId', 0)
                    logger.info(f"Found {source_name} with ID: {self.source_ids[source_name]}")
            
            # Check for missing sources
            missing = [src for src in required_sources if src not in self.source_ids]
            if missing:
                logger.error(f"❌ Missing sources: {missing}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error getting source IDs: {e}")
            return False
    
    def _set_initial_state(self):
        """Set initial visibility state"""
        try:
            # Show normal chatty, hide stretched version
            self._set_source_visibility(CHATTY_SOURCE, True)
            self._set_source_visibility("Chatty-stretch", False)
            
            # Show closed lips, hide open lips
            self._set_source_visibility(LIPS_CLOSED_SOURCE, True)
            self._set_source_visibility(LIPS_OPEN_SOURCE, False)
            
            logger.info("✅ Set initial state")
        except Exception as e:
            logger.error(f"Error setting initial state: {e}")
    
    def start_animation(self):
        """Start the rapid source-switching animation"""
        if self.animation_running:
            return
            
        self.animation_running = True
        self.animation_thread = threading.Thread(target=self._animation_loop, daemon=True)
        self.animation_thread.start()
        logger.info("🎭 Started source-switching animation")
    
    def stop_animation(self):
        """Stop animation and reset"""
        self.animation_running = False
        if self.animation_thread:
            self.animation_thread.join(timeout=1)
        
        self._reset_to_normal()
        logger.info("⏹️ Stopped animation")
    
    def _animation_loop(self):
        """Fast animation loop - switch between sources"""
        while self.animation_running:
            # STRETCH - Show stretched chatty + open lips
            self._show_stretched_state()
            time.sleep(0.2)  # Very fast - 200ms
            
            if not self.animation_running:
                break
                
            # NORMAL - Show normal chatty + closed lips  
            self._show_normal_state()
            time.sleep(0.2)  # Very fast - 200ms
    
    def _show_stretched_state(self):
        """Show stretched version with open lips"""
        try:
            # Switch to stretched chatty
            self._set_source_visibility(CHATTY_SOURCE, False)
            self._set_source_visibility("Chatty-stretch", True)
            
            # Show open lips
            self._set_source_visibility(LIPS_CLOSED_SOURCE, False)
            self._set_source_visibility(LIPS_OPEN_SOURCE, True)
            
            logger.debug("📈 Showing stretched state")
            
        except Exception as e:
            logger.error(f"Error showing stretched state: {e}")
    
    def _show_normal_state(self):
        """Show normal version with closed lips"""
        try:
            # Switch to normal chatty
            self._set_source_visibility(CHATTY_SOURCE, True)
            self._set_source_visibility("Chatty-stretch", False)
            
            # Show closed lips
            self._set_source_visibility(LIPS_CLOSED_SOURCE, True)
            self._set_source_visibility(LIPS_OPEN_SOURCE, False)
            
            logger.debug("📉 Showing normal state")
            
        except Exception as e:
            logger.error(f"Error showing normal state: {e}")
    
    def _set_source_visibility(self, source_name, visible):
        """Set source visibility"""
        try:
            source_id = self.source_ids.get(source_name)
            if not source_id:
                logger.warning(f"No source ID found for {source_name}")
                return
                
            response = self.ws.call(requests.SetSceneItemEnabled(
                sceneName=MAIN_SCENE,
                sceneItemId=source_id,
                sceneItemEnabled=visible
            ))
            
            if response.status:
                logger.debug(f"Set {source_name} visibility: {visible}")
            else:
                logger.error(f"Failed to set {source_name} visibility")
                
        except Exception as e:
            logger.error(f"Visibility error for {source_name}: {e}")
    
    def _reset_to_normal(self):
        """Reset to normal state"""
        try:
            self._show_normal_state()
            logger.info("✅ Reset to normal state")
        except Exception as e:
            logger.error(f"Reset error: {e}")
    
    def disconnect(self):
        """Disconnect from OBS"""
        self.stop_animation()
        if self.connected:
            try:
                self.ws.disconnect()
                self.connected = False
                logger.info("Disconnected from OBS")
            except Exception as e:
                logger.error(f"Disconnect error: {e}")
    
    def is_connected(self):
        """Check connection status"""
        return self.connected
    
    # Legacy methods for compatibility
    def _apply_stretch(self, stretched=False):
        """Legacy compatibility method"""
        if stretched:
            self._show_stretched_state()
        else:
            self._show_normal_state()
