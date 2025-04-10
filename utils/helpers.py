"""
Funciones auxiliares y utilidades para el bot.
"""
import discord
from datetime import datetime
from config import target_channels

def format_timestamp():
    """Devuelve la fecha y hora actual formateada."""
    return datetime.now().strftime('%d/%m/%Y %H:%M:%S')

def get_target_channel_info(guild_id, guild):
    """Obtiene información sobre el canal objetivo configurado para un servidor."""
    if guild_id in target_channels:
        channel = guild.get_channel(target_channels[guild_id])
        if channel:
            return f"el canal #{channel.name}", channel
        else:
            return "un canal configurado (que puede que ya no exista)", None
    else:
        return "ningún canal configurado aún (usa /canal para configurar uno)", None
