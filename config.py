"""
Configuraciones globales para el bot.
Centraliza todas las variables de configuración, patrones y constantes.
"""
import os
import re

# Canal predeterminado para monitorear mensajes
DEFAULT_CHANNEL_NAME = "〖🔫〗cs2"

# Detectar cualquier IPv4 en el mensaje
IP_PATTERN = re.compile(r'((?:\d{1,3}\.){3}\d{1,3})')

# Tokens y claves de API
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
FACEIT_API_KEY = os.environ.get('FACEIT_API_KEY')
FACEIT_API_URL = "https://open.faceit.com/data/v4"

# Diccionario para almacenar canales objetivo por servidor
target_channels = {}
