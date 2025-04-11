"""
Botardo - Bot de Discord para monitorear y eliminar mensajes connect+IP.
Punto de entrada principal que inicializa el bot y carga todos los módulos.
"""
import discord
import traceback
from discord.ext import commands

# Imports de módulos locales
from config import DISCORD_TOKEN
from commands import general, admin, faceit
from events import ready, messages

# Configurar intents para el bot
intents = discord.Intents.default()
intents.message_content = True  # Requerido para leer el contenido de los mensajes

# Inicializar el bot con un árbol de comandos para comandos slash
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree  # Árbol de comandos para slash commands

# Verificar los módulos de comandos
print("Módulos de comandos disponibles:")
print(f"- general: {general}")
print(f"- admin: {admin}")
print(f"- faceit: {faceit}")

# Configurar el evento on_ready
@bot.event
async def on_ready():
    """Evento que se ejecuta cuando el bot está listo y conectado."""
    await ready.on_ready(bot, tree)

# Configurar el evento on_message
@bot.event
async def on_message(message):
    """Evento que se ejecuta cuando se recibe un mensaje."""
    await messages.on_message(bot, message)

# Cargar todos los módulos de comandos
def setup_command_modules():
    """Inicializa y configura todos los módulos de comandos."""
    try:
        print("Cargando módulo general...")
        general.setup(bot, tree)
        print("✓ Módulo general cargado")
    except Exception as e:
        print(f"✗ Error al cargar módulo general: {e}")
        traceback.print_exc()
    
    try:
        print("Cargando módulo admin...")
        admin.setup(bot, tree)
        print("✓ Módulo admin cargado")
    except Exception as e:
        print(f"✗ Error al cargar módulo admin: {e}")
        traceback.print_exc()
    
    try:
        print("Cargando módulo faceit...")
        faceit.setup(bot, tree)
        print("✓ Módulo faceit cargado")
    except Exception as e:
        print(f"✗ Error al cargar módulo faceit: {e}")
        traceback.print_exc()
    
    # Listar comandos registrados en el árbol de comandos después de la carga
    print("\nComandos registrados actualmente en el árbol:")
    for cmd in tree.get_commands():
        print(f"- /{cmd.name}")

if __name__ == "__main__":
    print("Iniciando bot...")
    print("Cargando módulos de comandos...")
    setup_command_modules()
    print("Módulos de comandos procesados.")
    print("Conectando con Discord...")
    
    # Ejecutar el bot
    bot.run(DISCORD_TOKEN)
