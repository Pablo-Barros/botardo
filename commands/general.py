"""
Comandos generales y básicos del bot.
"""
import discord
from discord import app_commands
from config import target_channels
from utils.helpers import get_target_channel_info

# Variable global para almacenar las referencias
_bot = None
_tree = None

def setup(bot, tree):
    """Configura los comandos generales."""
    global _bot, _tree
    _bot = bot
    _tree = tree
    
    register_commands(tree)

def register_commands(tree):
    """Registra todos los comandos generales en el árbol."""
    
    @tree.command(name='test', description='Comprobar si los comandos slash funcionan')
    async def test_command(interaction: discord.Interaction):
        """Comando simple para verificar que los comandos slash funcionan."""
        await interaction.response.send_message("✅ Los comandos slash están funcionando correctamente.")
    
    @tree.command(name='ping', description='Comprobar si el bot está funcionando')
    async def ping(interaction: discord.Interaction):
        """Comando simple para verificar que el bot está funcionando."""
        await interaction.response.send_message('¡Pong! Bot funcionando correctamente.')
    
    @tree.command(name='info', description='Conoce el propósito de este bot')
    async def info(interaction: discord.Interaction):
        """Comando para mostrar información sobre el propósito del bot."""
        guild_id = interaction.guild.id
        channel_info, _ = get_target_channel_info(guild_id, interaction.guild)
        
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
