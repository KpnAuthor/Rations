"""
Rations Discord Bot - Main Bot Implementation
"""
import asyncio
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from src.database import db

# Bot intents - Start with minimal intents
intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True
# Note: message_content and members require privileged intents to be enabled in Discord Developer Portal

class RationsBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=None,  # No text commands, only slash commands
            intents=intents,
            help_command=None
        )
        self.voice_tracking = {}  # Track voice channel activity
        
    async def on_ready(self):
        """Called when bot is ready"""
        print(f'🤖 Bot logged in as {self.user} (ID: {self.user.id if self.user else "Unknown"})')
        print(f'📊 Connected to {len(self.guilds)} guilds')
        
        # Start background tasks
        self.analytics_update_task.start()
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            print(f'📋 Synced {len(synced)} slash commands')
        except Exception as e:
            print(f'Failed to sync commands: {e}')
        
        # Set bot activity
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.guilds)} servers | /analytics"
        ))
    
    async def on_guild_join(self, guild):
        """Called when bot joins a new guild"""
        print(f'📈 Joined new guild: {guild.name} (ID: {guild.id})')
        await self.update_presence()
    
    async def on_guild_remove(self, guild):
        """Called when bot leaves a guild"""
        print(f'📉 Left guild: {guild.name} (ID: {guild.id})')
        await self.update_presence()
    
    async def update_presence(self):
        """Update bot presence with current guild count"""
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.guilds)} servers | /analytics"
        ))
    
    async def on_message(self, message):
        """Called for every message"""
        if message.author.bot:
            return
        
        # Log message activity
        if message.guild:
            db.log_message_activity(
                guild_id=message.guild.id,
                channel_id=message.channel.id,
                user_id=message.author.id,
                message_length=len(message.content)
            )
        
        await self.process_commands(message)
    
    async def on_voice_state_update(self, member, before, after):
        """Track voice channel activity"""
        if member.bot:
            return
        
        guild_id = member.guild.id
        user_id = member.id
        
        # User joined a voice channel
        if before.channel is None and after.channel is not None:
            self.voice_tracking[user_id] = datetime.now()
            db.log_user_activity(
                guild_id=guild_id,
                user_id=user_id,
                activity_type='voice_join',
                channel_id=after.channel.id
            )
        
        # User left a voice channel
        elif before.channel is not None and after.channel is None:
            if user_id in self.voice_tracking:
                duration = (datetime.now() - self.voice_tracking[user_id]).total_seconds()
                db.log_user_activity(
                    guild_id=guild_id,
                    user_id=user_id,
                    activity_type='voice_leave',
                    channel_id=before.channel.id,
                    duration=int(duration)
                )
                del self.voice_tracking[user_id]
    
    @tasks.loop(seconds=Config.ANALYTICS_UPDATE_INTERVAL)
    async def analytics_update_task(self):
        """Update analytics data periodically"""
        for guild in self.guilds:
            try:
                # Count text channels
                text_channels = len([c for c in guild.channels if isinstance(c, discord.TextChannel)])
                
                # Estimate recent message count (this is simplified)
                message_count = 0
                for channel in guild.text_channels:
                    try:
                        # Count messages from last hour as an estimate
                        async for message in channel.history(limit=100, after=datetime.now() - timedelta(hours=1)):
                            if not message.author.bot:
                                message_count += 1
                    except discord.Forbidden:
                        continue
                
                # Calculate voice minutes
                voice_minutes = sum([
                    (datetime.now() - start_time).total_seconds() / 60
                    for start_time in self.voice_tracking.values()
                ])
                
                # Store analytics
                db.log_server_analytics(
                    guild_id=guild.id,
                    member_count=guild.member_count or 0,
                    channel_count=text_channels,
                    message_count=message_count,
                    voice_minutes=int(voice_minutes)
                )
                
            except Exception as e:
                print(f'Error updating analytics for guild {guild.id}: {e}')
    
    @analytics_update_task.before_loop
    async def before_analytics_update_task(self):
        """Wait for bot to be ready"""
        await self.wait_until_ready()

# Bot instance
bot = RationsBot()

# Slash commands
@bot.tree.command(name='analytics', description='Display server analytics and statistics')
async def analytics_slash(interaction: discord.Interaction):
    """Display server analytics"""
    if not interaction.guild:
        await interaction.response.send_message("❌ This command can only be used in servers!", ephemeral=True)
        return
    
    try:
        # Defer response for longer processing
        await interaction.response.defer()
        # Get analytics data
        analytics = db.get_server_analytics(interaction.guild.id, days=7)
        message_analytics = db.get_message_analytics(interaction.guild.id, days=7)
        
        if not analytics:
            await interaction.followup.send("📊 No analytics data available yet. Please wait for data to be collected.")
            return
        
        # Get latest data
        latest = analytics[0]
        
        # Create embed
        embed = discord.Embed(
            title=f"📊 Server Analytics - {interaction.guild.name}",
            description="Analytics for the last 7 days",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📈 Members",
            value=f"{latest['member_count']:,}",
            inline=True
        )
        
        embed.add_field(
            name="📝 Channels",
            value=f"{latest['channel_count']:,}",
            inline=True
        )
        
        embed.add_field(
            name="💬 Messages",
            value=f"{sum([a['message_count'] for a in analytics]):,}",
            inline=True
        )
        
        embed.add_field(
            name="🎙️ Voice Minutes",
            value=f"{sum([a['voice_minutes'] for a in analytics]):,}",
            inline=True
        )
        
        embed.add_field(
            name="📅 Data Points",
            value=f"{len(analytics)}",
            inline=True
        )
        
        # Most active channel
        if message_analytics:
            top_channel = message_analytics[0]
            channel = interaction.guild.get_channel(top_channel['channel_id'])
            channel_name = channel.name if channel else "Unknown"
            embed.add_field(
                name="🔥 Most Active Channel",
                value=f"#{channel_name} ({top_channel['message_count']} messages)",
                inline=False
            )
        
        embed.set_footer(text="Use /help for more commands")
        embed.timestamp = datetime.now()
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        print(f'Analytics command error: {e}')
        await interaction.followup.send("❌ An error occurred while fetching analytics data.")

@bot.tree.command(name='help', description='Show help information about the bot')
async def help_slash(interaction: discord.Interaction):
    """Display help information"""
    embed = discord.Embed(
        title="🤖 Rations Bot - Help",
        description="Discord Server Analytics Bot",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="/analytics",
        value="View server analytics and statistics",
        inline=False
    )
    
    embed.add_field(
        name="/help",
        value="Show this help message",
        inline=False
    )
    
    embed.add_field(
        name="/invite",
        value="Get the bot invite link",
        inline=False
    )
    
    embed.add_field(
        name="🌐 Web Dashboard",
        value="Visit the web dashboard for detailed analytics and charts",
        inline=False
    )
    
    embed.set_footer(text="Made with ❤️ for the Discord community")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='invite', description='Get the bot invite link')
async def invite_slash(interaction: discord.Interaction):
    """Generate bot invite link"""
    if not Config.DISCORD_CLIENT_ID:
        await interaction.response.send_message("❌ Bot client ID not configured.", ephemeral=True)
        return
    
    permissions = discord.Permissions(
        read_messages=True,
        send_messages=True,
        read_message_history=True,
        view_channel=True,
        connect=True,
        speak=True
    )
    
    invite_url = discord.utils.oauth_url(
        client_id=Config.DISCORD_CLIENT_ID,
        permissions=permissions,
        scopes=['bot', 'applications.commands']
    )
    
    embed = discord.Embed(
        title="🔗 Invite Rations Bot",
        description=f"[Click here to add the bot to your server]({invite_url})",
        color=discord.Color.blurple()
    )
    
    await interaction.response.send_message(embed=embed)

async def main():
    """Main bot function"""
    if not Config.DISCORD_TOKEN:
        print("❌ Error: DISCORD_TOKEN not found!")
        return
    
    try:
        async with bot:
            await bot.start(Config.DISCORD_TOKEN)
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot error: {e}")

if __name__ == "__main__":
    asyncio.run(main())