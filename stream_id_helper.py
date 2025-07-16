"""Updated stream ID helper with correct Barkle user ID format"""

import requests
import json
import asyncio
from config import BARKLE_TOKEN

class BarkleStreamHelper:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://barkle.chat/api"
        
    def format_user_id(self, user_id):
        """Ensure user ID has proper barkle: prefix"""
        if not user_id.startswith("barkle:"):
            return f"barkle:{user_id}"
        return user_id
        
    async def get_stream_data(self, user_id):
        """Get complete stream data for a specific user"""
        try:
            # Format the user ID correctly
            formatted_user_id = self.format_user_id(user_id)
            
            response = await self._make_request(
                endpoint="live/get",
                method="POST",
                data={"userId": formatted_user_id}
            )
            
            if response and response.get("isActive"):
                return response
            else:
                print(f"User {formatted_user_id} is not currently live streaming")
                return None
                
        except Exception as e:
            print(f"Error fetching stream data: {e}")
            return None
    
    async def get_stream_id(self, user_id):
        """Get just the stream ID for a user"""
        stream_data = await self.get_stream_data(user_id)
        return stream_data.get("id") if stream_data else None
    
    async def is_user_live(self, user_id):
        """Check if a user is currently live streaming"""
        stream_data = await self.get_stream_data(user_id)
        return stream_data.get("isActive", False) if stream_data else False
    
    async def get_viewer_count(self, user_id):
        """Get current viewer count for a user's stream"""
        stream_data = await self.get_stream_data(user_id)
        return stream_data.get("viewers", 0) if stream_data else 0
    
    async def _make_request(self, endpoint, method="GET", data=None):
        """Make HTTP request to Barkle API"""
        try:
            url = f"{self.base_url}/{endpoint}"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            if method == "POST":
                response = requests.post(url, headers=headers, json=data)
            else:
                response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Request error: {e}")
            return None

# Test function with multiple user ID formats
async def test_stream_api():
    """Test the stream API with proper user ID formatting"""
    helper = BarkleStreamHelper(BARKLE_TOKEN)
    
    # Test with different user ID formats
    test_user_ids = [
        "example_user_123",  # Will be formatted to barkle:example_user_123
        "barkle:another_user",  # Already properly formatted
        "USER_ID_HERE"  # Placeholder - replace with actual user ID
    ]
    
    print("Testing Barkle Stream API with proper user ID formatting...")
    
    for user_id in test_user_ids:
        print(f"\n🔍 Testing user ID: {user_id}")
        
        # Test getting stream data
        stream_data = await helper.get_stream_data(user_id)
        
        if stream_data:
            print("✅ Stream Data Retrieved:")
            print(f"   Stream ID: {stream_data.get('id')}")
            print(f"   Active: {stream_data.get('isActive')}")
            print(f"   Title: {stream_data.get('title')}")
            print(f"   Viewers: {stream_data.get('viewers')}")
            print(f"   URL: {stream_data.get('url')}")
            return stream_data.get('id')
        else:
            print(f"❌ No active stream found for {helper.format_user_id(user_id)}")
    
    return None

# Utility functions
async def get_stream_id_for_user(user_id, access_token=BARKLE_TOKEN):
    """Convenient function to get stream ID with proper formatting"""
    helper = BarkleStreamHelper(access_token)
    return await helper.get_stream_id(user_id)

async def find_live_users():
    """Helper to find users who are currently live"""
    helper = BarkleStreamHelper(BARKLE_TOKEN)
    
    # Example: Check a list of known user IDs
    known_users = [
        "popular_streamer_1",
        "gaming_channel_2", 
        "tech_creator_3"
    ]
    
    live_users = []
    
    for user_id in known_users:
        if await helper.is_user_live(user_id):
            stream_data = await helper.get_stream_data(user_id)
            live_users.append({
                "user_id": helper.format_user_id(user_id),
                "stream_id": stream_data.get("id"),
                "title": stream_data.get("title"),
                "viewers": stream_data.get("viewers")
            })
    
    return live_users

if __name__ == "__main__":
    asyncio.run(test_stream_api())
