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
