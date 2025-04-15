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
    
    # Comprobar si el mensaje contiene una IP
    match = IP_PATTERN.search(message.content)
    if match:
        found_ip = match.group(1)
        print(f'Mensaje sensible detectado en canal #{message.channel.name} - Usuario: {message.author}, Contenido: {message.content}')
        try:
            await message.delete()
            print(f'Mensaje con IP eliminado correctamente: {found_ip}')
            await message.channel.send(
                f"{message.author.mention} tu mensaje ha sido eliminado porque contenía una dirección IP.",
                delete_after=10
            )
        except Exception as e:
            print(f"ERROR al eliminar mensaje: {e}")
            try:
                await message.channel.send(
                    f"Necesito el permiso 'Gestionar Mensajes' para eliminar mensajes que contengan direcciones IP."
                )
            except:
                pass

async def on_message_edit(bot, before, after):
    """Maneja el evento que se ejecuta cuando se edita un mensaje."""
    if after.author == bot.user:
        return
    guild_id = after.guild.id
    if guild_id not in target_channels or after.channel.id != target_channels[guild_id]:
        return
    if before.content == after.content:
        return
    match = IP_PATTERN.search(after.content)
    if match:
        found_ip = match.group(1)
        print(f'MENSAJE EDITADO con IP detectado en canal #{after.channel.name} - Usuario: {after.author}, Contenido: {after.content}')
        try:
            await after.delete()
            print(f'Mensaje editado con IP eliminado correctamente: {found_ip}')
            await after.channel.send(
                f"{after.author.mention} tu mensaje editado ha sido eliminado porque contenía una dirección IP.",
                delete_after=10
            )
        except Exception as e:
            print(f"ERROR al eliminar mensaje editado: {e}")
            try:
                await after.channel.send(
                    f"Necesito el permiso 'Gestionar Mensajes' para eliminar mensajes editados que contengan direcciones IP."
                )
            except:
                pass
