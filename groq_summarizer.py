"""Updated Groq summarizer with version compatibility"""

import logging
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    
from config import GROQ_API_KEY, GROQ_MODEL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GroqSummarizer:
    def __init__(self):
        self.client = None
        if GROQ_AVAILABLE:
            self.initialize_client()
        
    def initialize_client(self):
        """Initialize Groq client with version compatibility"""
        try:
            if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
                logger.warning("Groq API key not configured")
                return False
            
            # Simple initialization without extra parameters
            self.client = Groq(api_key=GROQ_API_KEY)
            logger.info("Groq client initialized successfully")
            return True
        except Exception as e:
            logger.warning(f"Groq client initialization failed: {e}")
            return False
    
    def summarize_chat_messages(self, messages, chat_context="general"):
        """Summarize chat messages using Groq"""
        if not self.client or not messages:
            return None
            
        try:
            chat_text = "\n".join(messages)
            
            prompt = f"""
            Create a brief, natural summary of this chat conversation from the {chat_context} channel. 
            Focus on main topics and participants. Keep it conversational and under 20 words.
            
            Chat messages:
            {chat_text}
            
            Summary:"""
            
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that summarizes chat conversations concisely."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                model=GROQ_MODEL,
                max_tokens=50,
                temperature=0.7
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"Groq summary generated: {summary}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating Groq summary: {e}")
            return None
    
    def is_available(self):
        """Check if Groq is available"""
        return GROQ_AVAILABLE and self.client is not None
