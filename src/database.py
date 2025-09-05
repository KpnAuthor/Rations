"""
Database operations for Rations Discord Analytics Bot
"""
import sqlite3
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import threading

class Database:
    def __init__(self, db_path: str = 'rations.db'):
        self.db_path = db_path
        self.local = threading.local()
        self.init_database()
    
    def get_connection(self):
        """Get thread-local database connection"""
        if not hasattr(self.local, 'connection'):
            self.local.connection = sqlite3.connect(self.db_path)
            self.local.connection.row_factory = sqlite3.Row
        return self.local.connection
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Server analytics table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS server_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            member_count INTEGER DEFAULT 0,
            channel_count INTEGER DEFAULT 0,
            message_count INTEGER DEFAULT 0,
            voice_minutes INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Message analytics table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS message_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            message_length INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # User activity table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            activity_type TEXT NOT NULL,
            channel_id INTEGER,
            duration INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Discord OAuth sessions
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS oauth_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            access_token TEXT NOT NULL,
            refresh_token TEXT,
            expires_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
    
    def log_server_analytics(self, guild_id: int, member_count: int, channel_count: int, message_count: int, voice_minutes: int = 0):
        """Log server analytics data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO server_analytics (guild_id, member_count, channel_count, message_count, voice_minutes)
        VALUES (?, ?, ?, ?, ?)
        ''', (guild_id, member_count, channel_count, message_count, voice_minutes))
        
        conn.commit()
    
    def log_message_activity(self, guild_id: int, channel_id: int, user_id: int, message_length: int):
        """Log message activity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO message_analytics (guild_id, channel_id, user_id, message_length)
        VALUES (?, ?, ?, ?)
        ''', (guild_id, channel_id, user_id, message_length))
        
        conn.commit()
    
    def log_user_activity(self, guild_id: int, user_id: int, activity_type: str, channel_id: Optional[int] = None, duration: int = 0):
        """Log user activity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO user_activity (guild_id, user_id, activity_type, channel_id, duration)
        VALUES (?, ?, ?, ?, ?)
        ''', (guild_id, user_id, activity_type, channel_id, duration))
        
        conn.commit()
    
    def get_server_analytics(self, guild_id: int, days: int = 7) -> List[Dict]:
        """Get server analytics for the last N days"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        since_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
        SELECT * FROM server_analytics 
        WHERE guild_id = ? AND timestamp >= ?
        ORDER BY timestamp DESC
        ''', (guild_id, since_date))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_message_analytics(self, guild_id: int, days: int = 7) -> List[Dict]:
        """Get message analytics for the last N days"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        since_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
        SELECT channel_id, COUNT(*) as message_count, AVG(message_length) as avg_length
        FROM message_analytics 
        WHERE guild_id = ? AND timestamp >= ?
        GROUP BY channel_id
        ORDER BY message_count DESC
        ''', (guild_id, since_date))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_user_activity_stats(self, guild_id: int, days: int = 7) -> List[Dict]:
        """Get user activity statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        since_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
        SELECT user_id, activity_type, COUNT(*) as activity_count, SUM(duration) as total_duration
        FROM user_activity 
        WHERE guild_id = ? AND timestamp >= ?
        GROUP BY user_id, activity_type
        ORDER BY activity_count DESC
        ''', (guild_id, since_date))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def store_oauth_session(self, user_id: int, access_token: str, refresh_token: Optional[str] = None, expires_at: Optional[datetime] = None):
        """Store OAuth session data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO oauth_sessions (user_id, access_token, refresh_token, expires_at)
        VALUES (?, ?, ?, ?)
        ''', (user_id, access_token, refresh_token, expires_at))
        
        conn.commit()
    
    def get_oauth_session(self, user_id: int) -> Optional[Dict]:
        """Get OAuth session data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM oauth_sessions WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old analytics data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        tables = ['server_analytics', 'message_analytics', 'user_activity']
        for table in tables:
            cursor.execute(f'DELETE FROM {table} WHERE timestamp < ?', (cutoff_date,))
        
        conn.commit()

# Global database instance
db = Database()