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

@bot.event
async def on_ready():
    """Event that executes when the bot is ready and connected."""
    print(f'Bot conectado como {bot.user.name}')
    print(f'ID del Bot: {bot.user.id}')
    print('------')
    
    # Sync slash commands with Discord
    await tree.sync()
    print("¡Comandos slash sincronizados!")
    
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

@tree.command(name='elo', description='Buscar estadísticas de FACEIT de un jugador')
@app_commands.describe(nickname='Nickname de FACEIT del jugador')
async def faceit_stats(interaction: discord.Interaction, nickname: str):
    """Busca las estadísticas de FACEIT para un jugador, incluyendo su ELO y últimas 20 partidas."""
    if not FACEIT_API_KEY:
        await interaction.response.send_message(
            "⚠️ No se ha configurado la API key de FACEIT. El administrador debe configurarla en las variables de entorno.",
            ephemeral=True
        )
        return
    
    # Primero, indicar que estamos procesando
    await interaction.response.defer(thinking=True)
    
    try:
        # Buscar al jugador por nickname
        headers = {
            "Authorization": f"Bearer {FACEIT_API_KEY}",
            "Accept": "application/json"
        }
        
        player_url = f"{FACEIT_API_URL}/players?nickname={nickname}&game=cs2"
        player_response = requests.get(player_url, headers=headers)
        
        if player_response.status_code != 200:
            await interaction.followup.send(f"❌ No se encontró el jugador '{nickname}' en FACEIT o hubo un error en la API. Código: {player_response.status_code}")
            return
        
        player_data = player_response.json()
        player_id = player_data.get('player_id')
        
        if not player_id:
            await interaction.followup.send(f"❌ No se encontró el jugador '{nickname}' en FACEIT.")
            return
        
        # Obtener estadísticas del jugador
        stats_url = f"{FACEIT_API_URL}/players/{player_id}/stats/cs2"
        stats_response = requests.get(stats_url, headers=headers)
        
        if stats_response.status_code != 200:
            await interaction.followup.send(f"⚠️ Jugador encontrado, pero no se pudieron obtener estadísticas. Código: {stats_response.status_code}")
            return
        
        stats_data = stats_response.json()
        
        # Obtener historial de las últimas 20 partidas
        history_url = f"{FACEIT_API_URL}/players/{player_id}/history?game=cs2&offset=0&limit=20"
        history_response = requests.get(history_url, headers=headers)
        
        if history_response.status_code != 200:
            await interaction.followup.send(f"⚠️ Jugador encontrado, pero no se pudo obtener historial de partidas. Código: {history_response.status_code}")
            return
        
        history_data = history_response.json()
        
        # Extraer y formatear la información
        player_info = player_data
        faceit_elo = player_info.get('games', {}).get('cs2', {}).get('faceit_elo', 'Desconocido')
        level = player_info.get('games', {}).get('cs2', {}).get('skill_level', 0)
        
        # Estadísticas generales
        lifetime_stats = stats_data.get('lifetime', {})
        matches = lifetime_stats.get('Matches', '0')
        win_rate = lifetime_stats.get('Win Rate %', '0')
        avg_kd = lifetime_stats.get('Average K/D Ratio', '0')
        hs_rate = lifetime_stats.get('Average Headshots %', '0')
        
        # Crear un embed de Discord para mostrar las estadísticas
        embed = discord.Embed(
            title=f"Perfil FACEIT de {player_info.get('nickname')}",
            url=f"https://www.faceit.com/es/players/{player_info.get('nickname')}",
            color=0xFF5500  # Color naranja de FACEIT
        )
        
        # Añadir avatar del jugador si está disponible
        avatar_url = player_info.get('avatar')
        if avatar_url:
            embed.set_thumbnail(url=avatar_url)
        
        # Información principal
        embed.add_field(name="Nivel", value=f"{level} ⭐", inline=True)
        embed.add_field(name="ELO", value=faceit_elo, inline=True)
        embed.add_field(name="Partidas", value=matches, inline=True)
        embed.add_field(name="% Victoria", value=f"{win_rate}%", inline=True)
        embed.add_field(name="K/D Medio", value=avg_kd, inline=True)
        embed.add_field(name="% HS", value=f"{hs_rate}%", inline=True)
        
        # Información sobre las últimas partidas
        recent_matches = history_data.get('items', [])
        wins = 0
        losses = 0
        
        if recent_matches:
            for match in recent_matches:
                match_teams = match.get('teams', {})
                match_result = "No disponible"
                
                # Encontrar el resultado de la partida para el jugador
                for team_key, team_data in match_teams.items():
                    for player in team_data.get('players', []):
                        if player.get('player_id') == player_id:
                            match_result = team_data.get('outcome', 'No disponible')
                
                if match_result == 'win':
                    wins += 1
                elif match_result == 'loss':
                    losses += 1
            
            # Añadir estadísticas de partidas recientes
            recent_win_rate = 0
            if wins + losses > 0:
                recent_win_rate = (wins / (wins + losses)) * 100
            
            embed.add_field(
                name="Últimas 20 partidas",
                value=f"🏆 {wins} victorias | 💀 {losses} derrotas | 📊 {recent_win_rate:.1f}% victoria",
                inline=False
            )
        
        # Añadir pie de página
        embed.set_footer(text=f"Información actualizada el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        print(f"ERROR consultando FACEIT API: {e}")
        await interaction.followup.send(f"❌ Ocurrió un error al procesar la solicitud: {str(e)}")

@faceit_stats.error
async def faceit_stats_error(interaction: discord.Interaction, error):
    """Handle errors for the faceit_stats command."""
    await interaction.response.send_message(
        f"❌ Error al buscar estadísticas de FACEIT: {str(error)}",
        ephemeral=True
    )

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

# Run the bot
if __name__ == "__main__":
    bot.run(os.environ['DISCORD_TOKEN'])