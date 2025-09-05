import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Discord Bot Configuration
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
    DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
    DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', f'https://{os.getenv("REPLIT_DEV_DOMAIN", "localhost:5000")}/callback')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///rations.db')
    
    # Bot Settings
    BOT_PREFIX = '!'
    MAX_MESSAGE_HISTORY = 1000
    ANALYTICS_UPDATE_INTERVAL = 300  # 5 minutes
