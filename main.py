import os
import re
import discord
from discord import app_commands
from discord.ext import commands
import requests
from datetime import datetime

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

# FACEIT API Constants
FACEIT_API_KEY = os.environ.get('FACEIT_API_KEY')
FACEIT_API_URL = "https://open.faceit.com/data/v4"

# Define all slash commands outside of on_ready
@tree.command(name='test', description='Comprobar si los comandos slash funcionan')
async def test_command(interaction: discord.Interaction):
    """Comando simple para verificar que los comandos slash funcionan."""
    await interaction.response.send_message("✅ Los comandos slash están funcionando correctamente.")

@tree.command(name='ping', description='Comprobar si el bot está funcionando')
async def ping(interaction: discord.Interaction):
    """Simple command to verify that the bot is working."""
    await interaction.response.send_message('¡Pong! Bot funcionando correctamente.')

@tree.command(name='info', description='Conoce el propósito de este bot')
async def info(interaction: discord.Interaction):
    """Command to show information about the purpose of the bot."""
    guild_id = interaction.guild.id
    if guild_id in target_channels:
        channel = interaction.guild.get_channel(target_channels[guild_id])
        channel_info = f"el canal #{channel.name}" if channel else "un canal configurado (que puede que ya no exista)"
    else:
        channel_info = "ningún canal configurado aún (usa /canal para configurar uno)"
    
    await interaction.response.send_message(
        f"Soy un bot diseñado para eliminar mensajes que contienen instrucciones de conexión con direcciones IP en {channel_info}, para mantener la seguridad del servidor."
    )

@tree.command(name='comandos', description='Mostrar todos los comandos disponibles')
async def list_commands(interaction: discord.Interaction):
    """Lista todos los comandos slash disponibles."""
    cmd_list = []
    for cmd in tree.get_commands():
        cmd_list.append(f"/{cmd.name} - {cmd.description}")
    
    if cmd_list:
        await interaction.response.send_message("**Comandos disponibles:**\n" + "\n".join(cmd_list))
    else:
        await interaction.response.send_message("❌ No hay comandos registrados actualmente.")

@tree.command(name='sincronizar', description='Forzar la sincronización de comandos (solo administradores)')
@app_commands.checks.has_permissions(administrator=True)
async def force_sync(interaction: discord.Interaction):
    """Fuerza la sincronización de los comandos slash con Discord."""
    await interaction.response.defer(thinking=True)
    
    try:
        # Sync to this guild
        synced = await tree.sync(guild=interaction.guild)
        cmd_names = [cmd.name for cmd in synced]
        
        await interaction.followup.send(
            f"✅ Sincronización completada. {len(synced)} comandos sincronizados:\n" + 
            ", ".join(cmd_names) if cmd_names else "No se encontraron comandos para sincronizar."
        )
    except Exception as e:
        await interaction.followup.send(f"❌ Error durante la sincronización: {e}")

@tree.command(name='canal', description='Establece qué canal monitorizar para mensajes con IP')
@app_commands.describe(channel='El canal para monitorizar mensajes connect+IP')
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
        permission_status = "Tengo permiso para eliminar mensajes en este canal."
    else:
        permission_status = "¡ADVERTENCIA: No tengo permiso para eliminar mensajes en este canal! Por favor, actualiza mis permisos."
    
    await interaction.response.send_message(
        f"✅ Ahora monitorizando el canal #{channel.name} para mensajes connect+IP.\n{permission_status}"
    )

@set_channel.error
async def set_channel_error(interaction: discord.Interaction, error):
    """Handle errors for the set_channel command."""
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            "Necesitas el permiso 'Gestionar Canales' para usar este comando.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"Ocurrió un error: {str(error)}",
            ephemeral=True
        )

# Los comandos de FACEIT ahora se manejan en commands/faceit.py
# Se han eliminado las definiciones antiguas para evitar duplicación

@tree.command(name='checkperms', description='Comprobar si el bot tiene los permisos necesarios')
async def check_permissions(interaction: discord.Interaction):
    """Check if the bot has the necessary permissions."""
    guild_id = interaction.guild.id
    bot_member = interaction.guild.get_member(bot.user.id)
    permissions = bot_member.guild_permissions
    
    # Check if the target channel exists
    if guild_id in target_channels:
        target_channel = interaction.guild.get_channel(target_channels[guild_id])
        if target_channel:
            channel_status = f"✅ Actualmente monitorizando canal: #{target_channel.name}"
            
            # Check permissions in the target channel
            channel_perms = target_channel.permissions_for(bot_member)
            if channel_perms.manage_messages:
                channel_status += "\n✅ Puedo eliminar mensajes en este canal."
            else:
                channel_status += "\n❌ ¡NO tengo permiso para eliminar mensajes en este canal!"
        else:
            channel_status = "❌ ¡El canal objetivo configurado previamente ya no existe! Por favor, usa /canal para configurar un nuevo canal."
    else:
        channel_status = "❓ No hay ningún canal configurado actualmente para monitorizar. Usa /canal para configurar uno."
    
    if permissions.manage_messages:
        response = f"Tengo el permiso 'Gestionar Mensajes' a nivel de servidor.\n{channel_status}"
    else:
        response = f"¡No tengo el permiso 'Gestionar Mensajes' a nivel de servidor! Por favor, actualiza mis permisos de rol.\n{channel_status}"
    
    # List channels where bot can't delete messages
    problem_channels = []
    for channel in interaction.guild.text_channels:
        perms = channel.permissions_for(bot_member)
        if not perms.manage_messages:
            problem_channels.append(channel.name)
    
    if problem_channels:
        response += f"\nNo puedo eliminar mensajes en estos canales: {', '.join(problem_channels)}"
    
    await interaction.response.send_message(response)

@bot.event
async def on_ready():
    """Event that executes when the bot is ready and connected."""
    print(f'Bot conectado como {bot.user.name}')
    print(f'ID del Bot: {bot.user.id}')
    print('------')
    
    # Sync slash commands with Discord - Global sync first
    try:
        print("Intentando sincronización global de comandos...")
        synced = await tree.sync()
        print(f"¡Comandos slash sincronizados globalmente! Cantidad: {len(synced)}")
        print(f"Comandos registrados: {', '.join([cmd.name for cmd in synced])}")
    except Exception as e:
        print(f"Error en sincronización global: {e}")
    
    # Then sync per guild for faster updates
    print("Sincronizando comandos por servidor...")
    for guild in bot.guilds:
        try:
            guild_commands = await tree.sync(guild=guild)
            print(f"✓ Comandos sincronizados para {guild.name} (ID: {guild.id}). Cantidad: {len(guild_commands)}")
            if guild_commands:
                print(f"  Comandos: {', '.join([cmd.name for cmd in guild_commands])}")
        except Exception as e:
            print(f"✗ Error sincronizando comandos para {guild.name}: {e}")
    
    # Print bot permissions information
    for guild in bot.guilds:
        print(f'Conectado al servidor: {guild.name} (id: {guild.id})')
        
        # Try to find the default channel if none is set for this guild
        if guild.id not in target_channels:
            default_channel = discord.utils.get(guild.channels, name=DEFAULT_CHANNEL_NAME)
            if default_channel:
                target_channels[guild.id] = default_channel.id
                print(f'Canal objetivo predeterminado configurado "{DEFAULT_CHANNEL_NAME}" en {guild.name}')
            else:
                print(f'ADVERTENCIA: Canal predeterminado "{DEFAULT_CHANNEL_NAME}" no encontrado en {guild.name}')
        else:
            channel = guild.get_channel(target_channels[guild.id])
            if channel:
                print(f'Usando canal objetivo previamente configurado "{channel.name}" en {guild.name}')
            else:
                print(f'ADVERTENCIA: El canal objetivo configurado previamente ya no existe en {guild.name}')
                # Remove invalid channel
                target_channels.pop(guild.id, None)
        
        bot_member = guild.get_member(bot.user.id)
        permissions = bot_member.guild_permissions
        print(f'El bot tiene permiso "Gestionar Mensajes": {permissions.manage_messages}')
        
        # Check applications.commands scope
        bot_user = await guild.fetch_member(bot.user.id)
        if bot_user:
            print(f'Permisos integración de aplicaciones en {guild.name}: {bot_user.guild_permissions.use_application_commands}')

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
        print(f'Mensaje sensible detectado en canal #{message.channel.name} - Usuario: {message.author}, Contenido: {message.content}')
        
        try:
            # Delete the message
            await message.delete()
            print(f'Mensaje con IP eliminado correctamente: {found_ip}')
            
            # Optional: Send a warning message to the user
            await message.channel.send(
                f"{message.author.mention} tu mensaje ha sido eliminado porque contenía información sensible.",
                delete_after=10  # The message will be deleted after 10 seconds
            )
        except discord.errors.Forbidden as e:
            print(f"ERROR: Sin permiso para eliminar mensajes en {message.channel} - {e}")
            await message.channel.send(
                f"Necesito el permiso 'Gestionar Mensajes' para eliminar mensajes que contengan connect+IP."
            )
        except Exception as e:
            print(f"ERROR al eliminar mensaje: {e}")

# Run the bot
if __name__ == "__main__":
    bot.run(os.environ['DISCORD_TOKEN'])