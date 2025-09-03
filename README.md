# Rations - Discord Server Analytics Bot

A comprehensive Discord bot for server analytics with a beautiful web dashboard. Track member activity, message statistics, voice channel usage, and much more with real-time monitoring and detailed insights.

## 🚀 Features

### Discord Bot
- **Real-time Analytics**: Track server metrics automatically
- **Member Monitoring**: Monitor member count, growth, and activity
- **Message Statistics**: Analyze message volume and channel activity
- **Voice Activity**: Track voice channel usage and peak hours
- **User Activity**: Monitor user engagement and behavior patterns
- **Command Interface**: Easy-to-use Discord commands for quick stats

### Web Dashboard
- **Beautiful Interface**: Modern, responsive web dashboard
- **Discord OAuth**: Secure login with Discord authentication
- **Interactive Charts**: Visualize data with Chart.js graphs
- **Multi-Server Support**: Manage analytics for multiple servers
- **Real-time Updates**: Live data updates every 5 minutes
- **Mobile Friendly**: Responsive design for all devices

## 📋 Prerequisites

- Python 3.8 or higher
- Discord Bot Token
- Discord Application (for OAuth)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Rations
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Discord Bot Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section and create a bot
4. Copy the bot token
5. Go to the "OAuth2" section and note your Client ID and Client Secret

### 4. Environment Configuration

Create a `.env` file in the project root:

```env
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_CLIENT_ID=your_discord_client_id_here
DISCORD_CLIENT_SECRET=your_discord_client_secret_here

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=development

# Database
DATABASE_URL=sqlite:///rations.db

# Discord OAuth
DISCORD_REDIRECT_URI=http://localhost:5000/callback
```

### 5. Bot Permissions

When inviting the bot to your server, make sure it has these permissions:
- Read Messages
- Send Messages
- Read Message History
- View Channels
- Connect (for voice activity)
- Speak (for voice activity)

## 🚀 Running the Application

### Option 1: Run Both Services Together (Recommended)
```bash
python start.py
```

This will start both the Discord bot and web dashboard simultaneously.

### Option 2: Run Services Separately

**Discord Bot Only:**
```bash
python run_bot.py
```

**Web Dashboard Only:**
```bash
python run_web.py
```

## 📊 Usage

### Discord Commands

- `!analytics` or `!stats` - View server analytics
- `!help` - Show help information
- `!invite` - Get bot invite link

### Web Dashboard

1. Visit `http://localhost:5000`
2. Click "Login with Discord"
3. Authorize the application
4. View your server analytics in the dashboard

## 🏗️ Project Structure

```
Rations/
├── src/
│   ├── __init__.py
│   ├── bot.py              # Discord bot implementation
│   ├── web_app.py          # Flask web application
│   ├── database.py         # Database operations
│   └── templates/          # HTML templates
│       ├── base.html
│       ├── index.html
│       ├── dashboard.html
│       ├── analytics.html
│       ├── 404.html
│       └── 500.html
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── run_bot.py             # Bot launcher
├── run_web.py             # Web app launcher
├── start.py               # Combined launcher
├── .env.example           # Environment variables template
├── .gitignore
└── README.md
```

## 🔧 Configuration

### Bot Settings
- `BOT_PREFIX`: Command prefix (default: `!`)
- `MAX_MESSAGE_HISTORY`: Maximum messages to track (default: 1000)
- `ANALYTICS_UPDATE_INTERVAL`: Update interval in seconds (default: 300)

### Database
The bot uses SQLite by default. The database file (`rations.db`) will be created automatically.

### Web Dashboard
- Default port: 5000
- OAuth redirect URI: `http://localhost:5000/callback`
- Session management with secure tokens

## 📈 Analytics Data

The bot tracks the following metrics:

### Server Analytics
- Member count over time
- Channel count
- Message count
- Voice activity

### Message Analytics
- Message length
- Channel activity
- User message patterns

### User Activity
- Message sending
- Voice channel joins/leaves
- Activity timestamps

## 🔒 Security

- Discord OAuth2 authentication
- Secure session management
- Environment variable protection
- SQL injection prevention
- CSRF protection

## 🐛 Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check if the bot token is correct
   - Verify bot permissions in Discord
   - Ensure the bot is online

2. **Web dashboard not loading**
   - Check if port 5000 is available
   - Verify environment variables
   - Check Flask logs for errors

3. **OAuth not working**
   - Verify Client ID and Client Secret
   - Check redirect URI configuration
   - Ensure Discord application settings are correct

### Logs
Check the console output for detailed error messages and debugging information.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section
2. Review the Discord.py documentation
3. Check Flask documentation for web-related issues
4. Open an issue on GitHub

## 🔮 Future Features

- [ ] Advanced filtering and search
- [ ] Export analytics data
- [ ] Custom dashboard themes
- [ ] API endpoints for external integrations
- [ ] Advanced user behavior analytics
- [ ] Automated reports and alerts
- [ ] Multi-language support

---

**Made with ❤️ for the Discord community**
