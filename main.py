import os
import re
import discord
from discord import app_commands
from discord.ext import commands

# Configure intents for the bot
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content

# Initialize the bot with a command tree for slash commands
bot = commands.Bot(command_prefix='!', intents=intents)  # Prefix is still needed for error handling but won't be used for commands
tree = bot.tree  # Command tree for slash commands

# Regular expression to detect "connect" followed by an IP address
IP_PATTERN = re.compile(r'connect\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', re.IGNORECASE)

# Dictionary to store target channels for each guild (server)
target_channels = {}

# Default channel name (will be used if no channel is set)
DEFAULT_CHANNEL_NAME = "〖🔫〗cs2"

@bot.event
async def on_ready():
    """Event that executes when the bot is ready and connected."""
    print(f'Bot connected as {bot.user.name}')
    print(f'Bot ID: {bot.user.id}')
    print('------')
    
    # Sync slash commands with Discord
    await tree.sync()
    print("Slash commands synced!")
    
    # Print bot permissions information
    for guild in bot.guilds:
        print(f'Connected to server: {guild.name} (id: {guild.id})')
        
        # Try to find the default channel if none is set for this guild
        if guild.id not in target_channels:
            default_channel = discord.utils.get(guild.channels, name=DEFAULT_CHANNEL_NAME)
            if default_channel:
                target_channels[guild.id] = default_channel.id
                print(f'Set default target channel "{DEFAULT_CHANNEL_NAME}" in {guild.name}')
            else:
                print(f'WARNING: Default channel "{DEFAULT_CHANNEL_NAME}" not found in {guild.name}')
        else:
            channel = guild.get_channel(target_channels[guild.id])
            if channel:
                print(f'Using previously set target channel "{channel.name}" in {guild.name}')
            else:
                print(f'WARNING: Previously set target channel no longer exists in {guild.name}')
                # Remove invalid channel
                target_channels.pop(guild.id, None)
        
        bot_member = guild.get_member(bot.user.id)
        permissions = bot_member.guild_permissions
        print(f'Bot has "Manage Messages" permission: {permissions.manage_messages}')

@bot.event
async def on_message(message):
    """Event that executes when a message is received."""
    # Ignore messages from the bot itself to avoid loops
    if message.author == bot.user:
        return
    
    # Only check messages in the target channel for this guild
    guild_id = message.guild.id
    if guild_id not in target_channels or message.channel.id != target_channels[guild_id]:
        return
    
    # Check if the message contains "connect" followed by an IP
    match = IP_PATTERN.search(message.content)
    if match:
        # Log the action (for audit purposes)
        found_ip = match.group(1)
        print(f'Detected sensitive message in channel #{message.channel.name} - User: {message.author}, Content: {message.content}')
        
        try:
            # Delete the message
            await message.delete()
            print(f'Successfully deleted message with IP: {found_ip}')
            
            # Optional: Send a warning message to the user
            await message.channel.send(
                f"{message.author.mention} your message has been deleted because it contained sensitive information.",
                delete_after=10  # The message will be deleted after 10 seconds
            )
        except discord.errors.Forbidden as e:
            print(f"ERROR: No permission to delete message in {message.channel} - {e}")
            await message.channel.send(
                f"I need 'Manage Messages' permission to delete messages containing connect+IP."
            )
        except Exception as e:
            print(f"ERROR deleting message: {e}")

@tree.command(name='ping', description='Check if the bot is working')
async def ping(interaction: discord.Interaction):
    """Simple command to verify that the bot is working."""
    await interaction.response.send_message('Pong! Bot working correctly.')

@tree.command(name='info', description='Learn about the purpose of this bot')
async def info(interaction: discord.Interaction):
    """Command to show information about the purpose of the bot."""
    guild_id = interaction.guild.id
    if guild_id in target_channels:
        channel = interaction.guild.get_channel(target_channels[guild_id])
        channel_info = f"the #{channel.name} channel" if channel else "a configured channel (which may no longer exist)"
    else:
        channel_info = "no configured channel yet (use /canal to set one)"
    
    await interaction.response.send_message(
        f"I'm a bot designed to delete messages containing connection instructions with IP addresses in {channel_info}, to maintain server security."
    )

@tree.command(name='canal', description='Set which channel to monitor for IP messages')
@app_commands.describe(channel='The channel to monitor for connect+IP messages')
@app_commands.checks.has_permissions(manage_channels=True)
async def set_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    """Set which channel should be monitored for connect+IP messages.
    Only users with 'Manage Channels' permission can use this command."""
    
    guild_id = interaction.guild.id
    target_channels[guild_id] = channel.id
    
    # Check if the bot has permissions to delete messages in this channel
    bot_member = interaction.guild.get_member(bot.user.id)
    channel_perms = channel.permissions_for(bot_member)
    
    if channel_perms.manage_messages:
        permission_status = "I have permission to delete messages in this channel."
    else:
        permission_status = "WARNING: I don't have permission to delete messages in this channel! Please update my permissions."
    
    await interaction.response.send_message(
        f"✅ Now monitoring channel #{channel.name} for connect+IP messages.\n{permission_status}"
    )

@set_channel.error
async def set_channel_error(interaction: discord.Interaction, error):
    """Handle errors for the set_channel command."""
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            "You need the 'Manage Channels' permission to use this command.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"An error occurred: {str(error)}",
            ephemeral=True
        )

@tree.command(name='checkperms', description='Check if the bot has necessary permissions')
async def check_permissions(interaction: discord.Interaction):
    """Check if the bot has the necessary permissions."""
    guild_id = interaction.guild.id
    bot_member = interaction.guild.get_member(bot.user.id)
    permissions = bot_member.guild_permissions
    
    # Check if the target channel exists
    if guild_id in target_channels:
        target_channel = interaction.guild.get_channel(target_channels[guild_id])
        if target_channel:
            channel_status = f"✅ Currently monitoring channel: #{target_channel.name}"
            
            # Check permissions in the target channel
            channel_perms = target_channel.permissions_for(bot_member)
            if channel_perms.manage_messages:
                channel_status += "\n✅ I can delete messages in this channel."
            else:
                channel_status += "\n❌ I DON'T have permission to delete messages in this channel!"
        else:
            channel_status = "❌ The previously set target channel no longer exists! Please use /canal to set a new channel."
    else:
        channel_status = "❓ No channel is currently set for monitoring. Use /canal to set a channel."
    
    if permissions.manage_messages:
        response = f"I have the 'Manage Messages' permission at the server level.\n{channel_status}"
    else:
        response = f"I don't have the 'Manage Messages' permission at the server level! Please update my role permissions.\n{channel_status}"
    
    # List channels where bot can't delete messages
    problem_channels = []
    for channel in interaction.guild.text_channels:
        perms = channel.permissions_for(bot_member)
        if not perms.manage_messages:
            problem_channels.append(channel.name)
    
    if problem_channels:
        response += f"\nI can't delete messages in these channels: {', '.join(problem_channels)}"
    
    await interaction.response.send_message(response)

# Run the bot
if __name__ == "__main__":
    bot.run(os.environ['DISCORD_TOKEN'])