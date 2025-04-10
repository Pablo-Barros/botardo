"""
Comandos administrativos y de gestión del bot.
"""
import discord
from discord import app_commands
from config import target_channels

def setup(bot, tree):
    """Configura los comandos administrativos."""
    
    @tree.command(name='sincronizar', description='Forzar la sincronización de comandos (solo administradores)')
    @app_commands.checks.has_permissions(administrator=True)
    async def force_sync(interaction: discord.Interaction):
        """Fuerza la sincronización de los comandos slash con Discord."""
        await interaction.response.defer(thinking=True)
        
        try:
            # Sync to this guild
            synced = await tree.sync(guild=interaction.guild)
            cmd_names = [cmd.name for cmd in synced]
            
            await interaction.followup.send(
                f"✅ Sincronización completada. {len(synced)} comandos sincronizados:\n" + 
                ", ".join(cmd_names) if cmd_names else "No se encontraron comandos para sincronizar."
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Error durante la sincronización: {e}")
    
    @tree.command(name='canal', description='Establece qué canal monitorizar para mensajes con IP')
    @app_commands.describe(channel='El canal para monitorizar mensajes connect+IP')
    @app_commands.checks.has_permissions(manage_channels=True)
    async def set_channel(interaction: discord.Interaction, channel: discord.TextChannel):
        """Establece qué canal debe ser monitoreado para mensajes connect+IP.
        Solo usuarios con permiso 'Gestionar Canales' pueden usar este comando."""
        
        guild_id = interaction.guild.id
        target_channels[guild_id] = channel.id
        
        # Verificar si el bot tiene permisos para eliminar mensajes en este canal
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
        """Maneja errores para el comando set_channel."""
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
    
    @tree.command(name='checkperms', description='Comprobar si el bot tiene los permisos necesarios')
    async def check_permissions(interaction: discord.Interaction):
        """Verifica si el bot tiene los permisos necesarios."""
        guild_id = interaction.guild.id
        bot_member = interaction.guild.get_member(bot.user.id)
        permissions = bot_member.guild_permissions
        
        # Verificar si existe el canal objetivo
        if guild_id in target_channels:
            target_channel = interaction.guild.get_channel(target_channels[guild_id])
            if target_channel:
                channel_status = f"✅ Actualmente monitorizando canal: #{target_channel.name}"
                
                # Verificar permisos en el canal objetivo
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
        
        # Listar canales donde el bot no puede eliminar mensajes
        problem_channels = []
        for channel in interaction.guild.text_channels:
            perms = channel.permissions_for(bot_member)
            if not perms.manage_messages:
                problem_channels.append(channel.name)
        
        if problem_channels:
            response += f"\nNo puedo eliminar mensajes en estos canales: {', '.join(problem_channels)}"
        
        await interaction.response.send_message(response)
