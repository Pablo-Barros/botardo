"""
Maneja el evento on_ready del bot cuando se conecta.
"""
import discord
from config import DEFAULT_CHANNEL_NAME, target_channels

async def on_ready(bot, tree):
    """Maneja el evento que se ejecuta cuando el bot está listo y conectado."""
    print(f'Bot conectado como {bot.user.name}')
    print(f'ID del Bot: {bot.user.id}')
    print('------')
    
    # DIAGNÓSTICO: Listar comandos actuales antes de la sincronización
    print("\n🔍 DIAGNÓSTICO DE COMANDOS:")
    print("Comandos registrados ANTES de sincronizar:")
    global_commands = await bot.application.commands.fetch()
    for cmd in global_commands:
        print(f"  - /{cmd.name} (global)")
    
    for guild in bot.guilds:
        try:
            guild_commands = await guild.fetch_application_commands()
            for cmd in guild_commands:
                print(f"  - /{cmd.name} (en {guild.name})")
        except Exception as e:
            print(f"  Error al obtener comandos en {guild.name}: {e}")
    
    # ESTRATEGIA DE SINCRONIZACIÓN MEJORADA
    # 1. Primero sincronizamos por servidores (más rápido y con menos límites de tasa)
    print("\nSincronizando comandos por servidor (para actualizaciones rápidas)...")
    for guild in bot.guilds:
        try:
            # Borrar comandos existentes en el servidor antes de sincronizar
            # Esto asegura que se eliminan comandos obsoletos
            tree.clear_commands(guild=guild)
            await tree.sync(guild=guild)
            
            # Volver a sincronizar con los comandos actualizados
            guild_commands = await tree.sync(guild=guild)
            print(f"✓ Comandos sincronizados para {guild.name} (ID: {guild.id}). Cantidad: {len(guild_commands)}")
            if guild_commands:
                print(f"  Comandos: {', '.join([cmd.name for cmd in guild_commands])}")
        except Exception as e:
            print(f"✗ Error sincronizando comandos para {guild.name}: {e}")
    
    # 2. Luego sincronizamos globalmente para servidores futuros
    try:
        print("\nRealizando sincronización global de comandos...")
        # Limpiar comandos globales existentes
        tree.clear_commands(guild=None)
        await tree.sync()
        
        # Sincronizar con comandos actualizados
        synced = await tree.sync()
        print(f"¡Comandos slash sincronizados globalmente! Cantidad: {len(synced)}")
        if synced:
            print(f"Comandos registrados: {', '.join([cmd.name for cmd in synced])}")
    except Exception as e:
        print(f"Error en sincronización global: {e}")
    
    # DIAGNÓSTICO: Verificar comandos después de la sincronización
    print("\n🔍 Comandos registrados DESPUÉS de sincronizar:")
    global_commands = await bot.application.commands.fetch()
    for cmd in global_commands:
        print(f"  - /{cmd.name} (global)")
    
    for guild in bot.guilds:
        try:
            guild_commands = await guild.fetch_application_commands()
            for cmd in guild_commands:
                print(f"  - /{cmd.name} (en {guild.name})")
        except Exception as e:
            print(f"  Error al obtener comandos en {guild.name}: {e}")
    
    # Información sobre permisos del bot
    for guild in bot.guilds:
        print(f'Conectado al servidor: {guild.name} (id: {guild.id})')
        
        # Intentar encontrar el canal predeterminado si no hay ninguno configurado para este servidor
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
                # Eliminar canal inválido
                target_channels.pop(guild.id, None)
        
        bot_member = guild.get_member(bot.user.id)
        permissions = bot_member.guild_permissions
        print(f'El bot tiene permiso "Gestionar Mensajes": {permissions.manage_messages}')
        
        # Verificar scope applications.commands
        try:
            bot_user = await guild.fetch_member(bot.user.id)
            if bot_user:
                print(f'Permisos integración de aplicaciones en {guild.name}: {bot_user.guild_permissions.use_application_commands}')
        except Exception as e:
            print(f'Error al verificar permisos en {guild.name}: {str(e)}')
