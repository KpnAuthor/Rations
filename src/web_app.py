"""
Rations Web Dashboard - Flask Application
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from urllib.parse import urlencode
from flask_session import Session
import requests
from datetime import datetime, timedelta
import json

from config import Config
from src.database import db

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Discord OAuth URLs
DISCORD_API_BASE = 'https://discord.com/api/v10'
DISCORD_OAUTH_URL = f'{DISCORD_API_BASE}/oauth2/authorize'
DISCORD_TOKEN_URL = f'{DISCORD_API_BASE}/oauth2/token'

@app.route('/')
def index():
    """Home page"""
    user = session.get('user')
    guilds = session.get('guilds', [])
    return render_template('index.html', user=user, guilds=guilds)

@app.route('/login')
def login():
    """Redirect to Discord OAuth"""
    if not Config.DISCORD_CLIENT_ID:
        return render_template('error.html', 
            error='Discord OAuth not configured',
            message='Please configure DISCORD_CLIENT_ID in your environment variables.'
        )
    
    # Build OAuth URL with proper encoding
    params = {
        'client_id': Config.DISCORD_CLIENT_ID,
        'redirect_uri': Config.DISCORD_REDIRECT_URI,
        'response_type': 'code',
        'scope': 'identify guilds'
    }
    
    oauth_url = DISCORD_OAUTH_URL + '?' + urlencode(params)
    return redirect(oauth_url)

@app.route('/callback')
def oauth_callback():
    """Handle Discord OAuth callback"""
    code = request.args.get('code')
    if not code:
        return render_template('error.html', 
            error='OAuth Error',
            message='No authorization code received from Discord.'
        )
    
    try:
        # Exchange code for access token
        token_data = {
            'client_id': Config.DISCORD_CLIENT_ID,
            'client_secret': Config.DISCORD_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': Config.DISCORD_REDIRECT_URI
        }
        
        token_response = requests.post(
            DISCORD_TOKEN_URL,
            data=token_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if token_response.status_code != 200:
            return render_template('error.html',
                error='Token Exchange Failed',
                message='Failed to exchange authorization code for access token.'
            )
        
        token_json = token_response.json()
        access_token = token_json['access_token']
        
        # Get user info
        user_response = requests.get(
            f'{DISCORD_API_BASE}/users/@me',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if user_response.status_code != 200:
            return render_template('error.html',
                error='User Info Failed',
                message='Failed to fetch user information from Discord.'
            )
        
        user_data = user_response.json()
        
        # Get user guilds
        guilds_response = requests.get(
            f'{DISCORD_API_BASE}/users/@me/guilds',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        guilds_data = []
        if guilds_response.status_code == 200:
            guilds_data = guilds_response.json()
        
        # Store in session
        session['user'] = user_data
        session['guilds'] = guilds_data
        session['access_token'] = access_token
        
        # Store OAuth session in database
        expires_at = datetime.now() + timedelta(seconds=token_json.get('expires_in', 3600))
        db.store_oauth_session(
            user_id=int(user_data['id']),
            access_token=access_token,
            refresh_token=token_json.get('refresh_token'),
            expires_at=expires_at
        )
        
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        print(f'OAuth callback error: {e}')
        return render_template('error.html',
            error='Authentication Error',
            message='An error occurred during authentication. Please try again.'
        )

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard"""
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    
    guilds = session.get('guilds', [])
    return render_template('dashboard.html', user=user, guilds=guilds)

@app.route('/analytics/<int:guild_id>')
def analytics(guild_id):
    """Analytics page for specific guild"""
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    
    # Check if user has access to this guild
    guilds = session.get('guilds', [])
    guild = next((g for g in guilds if g['id'] == str(guild_id)), None)
    
    if not guild:
        return render_template('error.html',
            error='Access Denied',
            message='You do not have access to this server.'
        )
    
    # Get analytics data
    try:
        server_analytics = db.get_server_analytics(guild_id, days=30)
        message_analytics = db.get_message_analytics(guild_id, days=30)
        user_activity = db.get_user_activity_stats(guild_id, days=30)
        
        return render_template('analytics.html', 
            guild=guild,
            server_analytics=server_analytics,
            message_analytics=message_analytics,
            user_activity=user_activity
        )
    except Exception as e:
        print(f'Analytics error: {e}')
        return render_template('error.html',
            error='Analytics Error',
            message='Failed to load analytics data.'
        )

@app.route('/api/analytics/<int:guild_id>')
def api_analytics(guild_id):
    """API endpoint for analytics data"""
    user = session.get('user')
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Check guild access
    guilds = session.get('guilds', [])
    guild = next((g for g in guilds if g['id'] == str(guild_id)), None)
    
    if not guild:
        return jsonify({'error': 'Access denied'}), 403
    
    days = request.args.get('days', 7, type=int)
    
    try:
        data = {
            'server_analytics': db.get_server_analytics(guild_id, days),
            'message_analytics': db.get_message_analytics(guild_id, days),
            'user_activity': db.get_user_activity_stats(guild_id, days)
        }
        return jsonify(data)
    except Exception as e:
        print(f'API analytics error: {e}')
        return jsonify({'error': 'Failed to fetch analytics data'}), 500

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    print("Starting Rations Web Dashboard...")
    app.run(debug=Config.FLASK_ENV == 'development', host='0.0.0.0', port=5000)