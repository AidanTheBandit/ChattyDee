"""Lip overlay generator"""

import os
from PIL import Image, ImageDraw
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LipOverlay:
    def __init__(self, width=100, height=60):
        self.width = width
        self.height = height
        self.assets_dir = "assets"
        os.makedirs(self.assets_dir, exist_ok=True)
        self._generate_lips()
    
    def _generate_lips(self):
        """Generate lip overlay images"""
        closed_path = os.path.join(self.assets_dir, "lips_closed.png")
        
        if not os.path.exists(closed_path):
            self.create_closed_lips().save(closed_path)
            logger.info(f"Generated closed lips: {closed_path}")
    
    def create_closed_lips(self):
        """Create closed lips overlay"""
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw closed lips
        lip_color = (180, 80, 80, 255)
        outline_color = (120, 50, 50, 255)
        
        draw.ellipse([15, 25, 85, 35], fill=lip_color, outline=outline_color, width=2)
        draw.line([20, 30, 80, 30], fill=outline_color, width=1)
        
        return img
