"""
Maneja los eventos relacionados con mensajes del bot.
"""
from config import IP_PATTERN, target_channels

async def on_message(bot, message):
    """Maneja el evento que se ejecuta cuando se recibe un mensaje."""
    # Ignorar mensajes del propio bot para evitar bucles
    if message.author == bot.user:
        return
    
    # Solo revisar mensajes en el canal objetivo para este servidor
    guild_id = message.guild.id
    if guild_id not in target_channels or message.channel.id != target_channels[guild_id]:
        return
    
    # Comprobar si el mensaje contiene "connect" seguido de una IP
    match = IP_PATTERN.search(message.content)
    if match:
        # Registrar la acción (para auditoría)
        found_ip = match.group(1)
        print(f'Mensaje sensible detectado en canal #{message.channel.name} - Usuario: {message.author}, Contenido: {message.content}')
        
        try:
            # Eliminar el mensaje
            await message.delete()
            print(f'Mensaje con IP eliminado correctamente: {found_ip}')
            
            # Opcional: Enviar un mensaje de advertencia al usuario
            await message.channel.send(
                f"{message.author.mention} tu mensaje ha sido eliminado porque contenía información sensible.",
                delete_after=10  # El mensaje se eliminará después de 10 segundos
            )
        except Exception as e:
            print(f"ERROR al eliminar mensaje: {e}")
            # Intentar enviar un mensaje de error si es posible
            try:
                await message.channel.send(
                    f"Necesito el permiso 'Gestionar Mensajes' para eliminar mensajes que contengan connect+IP."
                )
            except:
                # Si no podemos enviar el mensaje, simplemente continuamos
                pass

async def on_message_edit(bot, before, after):
    """Maneja el evento que se ejecuta cuando se edita un mensaje.
    
    Este evento permite detectar cuando un usuario edita un mensaje
    para añadir una IP que debería ser eliminada.
    """
    # Ignorar ediciones de mensajes del propio bot
    if after.author == bot.user:
        return
    
    # Solo revisar mensajes en el canal objetivo para este servidor
    guild_id = after.guild.id
    if guild_id not in target_channels or after.channel.id != target_channels[guild_id]:
        return
    
    # Ignorar si el contenido no cambió
    if before.content == after.content:
        return
    
    # Comprobar si el mensaje editado contiene "connect" seguido de una IP
    match = IP_PATTERN.search(after.content)
    if match:
        # Registrar la acción (para auditoría)
        found_ip = match.group(1)
        print(f'MENSAJE EDITADO con IP detectado en canal #{after.channel.name} - Usuario: {after.author}, Contenido: {after.content}')
        
        try:
            # Eliminar el mensaje
            await after.delete()
            print(f'Mensaje editado con IP eliminado correctamente: {found_ip}')
            
            # Opcional: Enviar un mensaje de advertencia al usuario
            await after.channel.send(
                f"{after.author.mention} tu mensaje editado ha sido eliminado porque contenía información sensible.",
                delete_after=10  # El mensaje se eliminará después de 10 segundos
            )
        except Exception as e:
            print(f"ERROR al eliminar mensaje editado: {e}")
            try:
                await after.channel.send(
                    f"Necesito el permiso 'Gestionar Mensajes' para eliminar mensajes editados que contengan connect+IP."
                )
            except:
                # Si no podemos enviar el mensaje, simplemente continuamos
                pass
