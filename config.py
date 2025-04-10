"""
Configuraciones globales para el bot.
Centraliza todas las variables de configuración, patrones y constantes.
"""
import os
import re

# Canal predeterminado para monitorear mensajes
DEFAULT_CHANNEL_NAME = "〖🔫〗cs2"

# Expresión regular para detectar "connect" seguido de una dirección IP
IP_PATTERN = re.compile(r'connect\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', re.IGNORECASE)

# Tokens y claves de API
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
FACEIT_API_KEY = os.environ.get('FACEIT_API_KEY')
FACEIT_API_URL = "https://open.faceit.com/data/v4"

# Diccionario para almacenar canales objetivo por servidor
target_channels = {}
