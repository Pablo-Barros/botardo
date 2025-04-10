import os
import re
import discord
from discord import app_commands
from discord.ext import commands
from keep_alive import keep_alive  # To keep the bot active

# Configure intents for the bot
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content

# Initialize the bot with a command tree for slash commands
bot = commands.Bot(command_prefix='!', intents=intents)  # Prefix is still needed for error handling but won't be used for commands
tree = bot.tree  # Command tree for slash commands

# Regular expression to detect "connect" followed by an IP address
IP_PATTERN = re.compile(r'connect\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', re.IGNORECASE)

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
        bot_member = guild.get_member(bot.user.id)
        permissions = bot_member.guild_permissions
        print(f'Bot has "Manage Messages" permission: {permissions.manage_messages}')

@bot.event
async def on_message(message):
    """Event that executes when a message is received."""
    # Ignore messages from the bot itself to avoid loops
    if message.author == bot.user:
        return
    
    # Check if the message contains "connect" followed by an IP
    match = IP_PATTERN.search(message.content)
    if match:
        # Log the action (for audit purposes)
        found_ip = match.group(1)
        print(f'Detected sensitive message - User: {message.author}, Content: {message.content}')
        
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
    
    # We no longer need to process commands here, as slash commands are handled differently

@tree.command(name='ping', description='Check if the bot is working')
async def ping(interaction: discord.Interaction):
    """Simple command to verify that the bot is working."""
    await interaction.response.send_message('Pong! Bot working correctly.')

@tree.command(name='info', description='Learn about the purpose of this bot')
async def info(interaction: discord.Interaction):
    """Command to show information about the purpose of the bot."""
    await interaction.response.send_message("I'm a bot designed to delete messages containing connection instructions with IP addresses, to maintain server security.")

@tree.command(name='checkperms', description='Check if the bot has necessary permissions')
async def check_permissions(interaction: discord.Interaction):
    """Check if the bot has the necessary permissions."""
    bot_member = interaction.guild.get_member(bot.user.id)
    permissions = bot_member.guild_permissions
    
    if permissions.manage_messages:
        response = "I have the 'Manage Messages' permission required to delete messages."
    else:
        response = "I don't have the 'Manage Messages' permission! Please update my role permissions."
    
    # List channels where bot can't delete messages
    problem_channels = []
    for channel in interaction.guild.text_channels:
        perms = channel.permissions_for(bot_member)
        if not perms.manage_messages:
            problem_channels.append(channel.name)
    
    if problem_channels:
        response += f"\nI can't delete messages in these channels: {', '.join(problem_channels)}"
    
    await interaction.response.send_message(response)

# Keep the bot active (specific for Replit)
keep_alive()

# Run the bot
bot.run(os.environ['DISCORD_TOKEN'])