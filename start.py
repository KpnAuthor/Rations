#!/usr/bin/env python3
"""
Rations - Combined Bot and Web Dashboard Launcher
This script allows you to run both the Discord bot and web dashboard together
"""

import asyncio
import threading
import sys
import os
import time
from multiprocessing import Process

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_bot():
    """Run the Discord bot in a separate process"""
    try:
        from src.bot import main
        print("🤖 Starting Discord Bot...")
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Bot error: {e}")

def run_web():
    """Run the Flask web application in a separate process"""
    try:
        from src.web_app import app
        from config import Config
        print("🌐 Starting Web Dashboard...")
        app.run(
            debug=Config.FLASK_ENV == 'development',
            host='0.0.0.0',
            port=5000,
            use_reloader=False  # Disable reloader to avoid conflicts
        )
    except Exception as e:
        print(f"❌ Web app error: {e}")

def main():
    """Main function to start both services"""
    print("🚀 Starting Rations - Discord Server Analytics")
    print("=" * 50)
    
    # Check if required environment variables are set
    from config import Config
    
    if not Config.DISCORD_TOKEN:
        print("❌ Error: DISCORD_TOKEN not found in environment variables!")
        print("Please create a .env file with your Discord bot token.")
        sys.exit(1)
    
    if not Config.DISCORD_CLIENT_ID:
        print("❌ Error: DISCORD_CLIENT_ID not found in environment variables!")
        print("Please create a .env file with your Discord application client ID.")
        sys.exit(1)
    
    print("✅ Environment variables loaded successfully")
    print("🤖 Discord Bot: Starting...")
    print("🌐 Web Dashboard: Starting on http://localhost:5000")
    print("=" * 50)
    
    # Start bot and web app in separate processes
    bot_process = Process(target=run_bot)
    web_process = Process(target=run_web)
    
    try:
        # Start both processes
        bot_process.start()
        time.sleep(2)  # Give bot time to start
        web_process.start()
        
        print("✅ Both services started successfully!")
        print("📊 Web Dashboard: http://localhost:5000")
        print("🤖 Discord Bot: Online and ready")
        print("\nPress Ctrl+C to stop both services...")
        
        # Wait for both processes
        bot_process.join()
        web_process.join()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        bot_process.terminate()
        web_process.terminate()
        bot_process.join()
        web_process.join()
        print("✅ All services stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        bot_process.terminate()
        web_process.terminate()

if __name__ == "__main__":
    main()
