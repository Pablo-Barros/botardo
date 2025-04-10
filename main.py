import os
import re
import discord
from discord.ext import commands
from keep_alive import keep_alive  # To keep the bot active

# Configure intents for the bot
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content

# Initialize the bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Regular expression to detect "connect" followed by an IP address
IP_PATTERN = re.compile(r'connect\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', re.IGNORECASE)

@bot.event
async def on_ready():
    """Event that executes when the bot is ready and connected."""
    print(f'Bot connected as {bot.user.name}')
    print(f'Bot ID: {bot.user.id}')
    print('------')

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
        print(f'Message deleted - User: {message.author}, Content: {message.content}')
        
        try:
            # Delete the message
            await message.delete()
            
            # Optional: Send a warning message to the user
            await message.channel.send(
                f"{message.author.mention} your message has been deleted because it contained sensitive information.",
                delete_after=10  # The message will be deleted after 10 seconds
            )
        except discord.errors.Forbidden:
            print(f"I don't have permissions to delete messages in {message.channel}")
        except Exception as e:
            print(f"Error deleting message: {e}")
    
    # Process commands in the message (if any)
    await bot.process_commands(message)

@bot.command(name='ping')
async def ping(ctx):
    """Simple command to verify that the bot is working."""
    await ctx.send('Pong! Bot working correctly.')

@bot.command(name='info')
async def info(ctx):
    """Command to show information about the purpose of the bot."""
    await ctx.send("I'm a bot designed to delete messages containing connection instructions with IP addresses, to maintain server security.")

# Keep the bot active (specific for Replit)
keep_alive()

# Run the bot
bot.run(os.environ['DISCORD_TOKEN'])
