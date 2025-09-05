# Rations - Discord Server Analytics Bot

## Overview

Rations is a comprehensive Discord analytics bot that provides real-time monitoring and detailed insights for Discord servers. The system consists of a Discord bot that collects server metrics and a web dashboard that presents the data through interactive visualizations. The bot tracks member activity, message statistics, voice channel usage, and server growth patterns, making it valuable for Discord server administrators who want to understand their community's engagement and growth trends.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Architecture
- **Discord.py Framework**: Uses discord.py 2.3.2 with comprehensive intents (message_content, members, guilds, voice_states) to monitor server activities
- **Event-Driven Data Collection**: Real-time event handlers for message tracking, member joins/leaves, and voice channel activity
- **Background Task System**: Automated analytics updates every 5 minutes using discord.py's task loops
- **Multi-Server Support**: Single bot instance can monitor multiple Discord servers simultaneously

### Web Dashboard Architecture
- **Flask Web Framework**: Flask 3.0.0 application serving a responsive web interface
- **Discord OAuth Integration**: Secure authentication using Discord's OAuth2 flow for user login and server access
- **Template-Based UI**: Jinja2 templates with Bootstrap 5 for responsive design and Chart.js for data visualization
- **Session Management**: Flask-Session for maintaining user authentication state

### Data Storage
- **SQLite Database**: Local SQLite database for storing analytics data with tables for server analytics, message analytics, and user activity
- **Thread-Safe Operations**: Thread-local database connections to handle concurrent access from both bot and web application
- **Time-Series Data**: Timestamped records for historical trend analysis and growth tracking

### Deployment Architecture
- **Multi-Process Design**: Separate entry points for bot (`run_bot.py`) and web app (`run_web.py`) with combined launcher (`start.py`)
- **Environment Configuration**: Centralized configuration system using python-dotenv for environment variable management
- **Replit Compatibility**: Automatic domain detection and configuration for Replit deployment environment

### Authentication & Security
- **Discord OAuth2**: Uses Discord's official OAuth2 implementation for secure user authentication
- **Guild Permission Verification**: Checks user's server permissions before displaying analytics
- **Session Security**: Secure session management with configurable secret keys

## External Dependencies

### Core Services
- **Discord API**: Primary integration for bot functionality and OAuth authentication
- **Discord CDN**: For serving user avatars and server icons in the web interface

### Python Libraries
- **discord.py 2.3.2**: Discord bot framework and API wrapper
- **Flask 3.0.0**: Web application framework for the dashboard
- **flask-session 0.5.0**: Session management for user authentication
- **requests 2.31.0**: HTTP client for Discord OAuth token exchange
- **python-dotenv 1.0.0**: Environment variable management

### Frontend Dependencies
- **Bootstrap 5.1.3**: CSS framework for responsive UI design
- **Font Awesome 6.0.0**: Icon library for UI elements
- **Chart.js**: JavaScript charting library for data visualization

### Database
- **SQLite**: Embedded database for local data storage (with potential for PostgreSQL upgrade)

### Development Tools
- **tarsafe**: Security scanning and dependency management