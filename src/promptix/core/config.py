import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

class Config:
    """Configuration management for Promptix."""
    
    @classmethod
    def get_promptix_key(cls):
        """Get the Promptix key from environment variables."""
        return os.getenv("PROMPTIX_KEY", "")
    