"""
Comandos relacionados con la integración de FACEIT.
"""
import discord
from discord import app_commands
import requests
from datetime import datetime
from config import FACEIT_API_KEY, FACEIT_API_URL
from utils.helpers import format_timestamp

def setup(bot, tree):
    """Configura los comandos de FACEIT."""
    
    @tree.command(name='elo', description='Buscar el ELO de FACEIT de un jugador')
    @app_commands.describe(nickname='Nickname de FACEIT del jugador')
    async def faceit_elo(interaction: discord.Interaction, nickname: str):
        """Busca y muestra únicamente el ELO de FACEIT para un jugador."""
        if not FACEIT_API_KEY:
            await interaction.response.send_message(
                "⚠️ No se ha configurado la API key de FACEIT. El administrador debe configurarla en las variables de entorno.",
                ephemeral=True
            )
            return
        
        # Primero, indicar que estamos procesando
        await interaction.response.defer(thinking=True)
        
        try:
            # Buscar al jugador por nickname (case insensitive)
            headers = {
                "Authorization": f"Bearer {FACEIT_API_KEY}",
                "Accept": "application/json"
            }
            
            # Utilizamos la búsqueda por nickname, que es insensible a mayúsculas/minúsculas
            # La API de FACEIT por defecto trata las búsquedas como case insensitive
            player_url = f"{FACEIT_API_URL}/players?nickname={nickname}&game=cs2"
            player_response = requests.get(player_url, headers=headers)
            
            if player_response.status_code != 200:
                await interaction.followup.send(f"❌ No se encontró el jugador '{nickname}' en FACEIT o hubo un error en la API. Código: {player_response.status_code}")
                return
            
            player_data = player_response.json()
            
            # Extraer la información básica del jugador
            player_nickname = player_data.get('nickname', nickname)
            faceit_elo = player_data.get('games', {}).get('cs2', {}).get('faceit_elo', 'Desconocido')
            level = player_data.get('games', {}).get('cs2', {}).get('skill_level', 0)
            
            # Crear un embed de Discord para mostrar solo el ELO
            embed = discord.Embed(
                title=f"ELO de {player_nickname} en FACEIT",
                url=f"https://www.faceit.com/es/players/{player_nickname}",
                color=0xFF5500  # Color naranja de FACEIT
            )
            
            # Añadir avatar del jugador si está disponible
            avatar_url = player_data.get('avatar')
            if avatar_url:
                embed.set_thumbnail(url=avatar_url)
            
            # Añadir la información del ELO y nivel
            embed.add_field(name="Nivel", value=f"{level} ⭐", inline=True)
            embed.add_field(name="ELO", value=faceit_elo, inline=True)
            
            # Añadir pie de página
            embed.set_footer(text=f"Información actualizada el {format_timestamp()}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            print(f"ERROR consultando FACEIT API: {e}")
            await interaction.followup.send(f"❌ Ocurrió un error al procesar la solicitud: {str(e)}")

    @faceit_elo.error
    async def faceit_elo_error(interaction: discord.Interaction, error):
        """Maneja errores para el comando faceit_elo."""
        await interaction.response.send_message(
            f"❌ Error al buscar el ELO de FACEIT: {str(error)}",
            ephemeral=True
        )
    
    @tree.command(name='stats', description='Buscar estadísticas generales de un jugador en FACEIT')
    @app_commands.describe(nickname='Nickname de FACEIT del jugador')
    async def faceit_stats(interaction: discord.Interaction, nickname: str):
        """Busca y muestra estadísticas globales de un jugador en FACEIT."""
        if not FACEIT_API_KEY:
            await interaction.response.send_message(
                "⚠️ No se ha configurado la API key de FACEIT. El administrador debe configurarla en las variables de entorno.",
                ephemeral=True
            )
            return
        
        # Primero, indicar que estamos procesando
        await interaction.response.defer(thinking=True)
        
        try:
            # Buscar al jugador por nickname
            headers = {
                "Authorization": f"Bearer {FACEIT_API_KEY}",
                "Accept": "application/json"
            }
            
            player_url = f"{FACEIT_API_URL}/players?nickname={nickname}&game=cs2"
            player_response = requests.get(player_url, headers=headers)
            
            if player_response.status_code != 200:
                await interaction.followup.send(f"❌ No se encontró el jugador '{nickname}' en FACEIT o hubo un error en la API. Código: {player_response.status_code}")
                return
            
            player_data = player_response.json()
            player_id = player_data.get('player_id')
            
            if not player_id:
                await interaction.followup.send(f"❌ No se encontró el jugador '{nickname}' en FACEIT.")
                return
            
            # Obtener estadísticas del jugador
            stats_url = f"{FACEIT_API_URL}/players/{player_id}/stats/cs2"
            stats_response = requests.get(stats_url, headers=headers)
            
            if stats_response.status_code != 200:
                await interaction.followup.send(f"⚠️ Jugador encontrado, pero no se pudieron obtener estadísticas. Código: {stats_response.status_code}")
                return
            
            stats_data = stats_response.json()
            
            # Extraer y formatear la información
            player_nickname = player_data.get('nickname', nickname)
            faceit_elo = player_data.get('games', {}).get('cs2', {}).get('faceit_elo', 'Desconocido')
            level = player_data.get('games', {}).get('cs2', {}).get('skill_level', 0)
            
            # Estadísticas generales
            lifetime_stats = stats_data.get('lifetime', {})
            matches = lifetime_stats.get('Matches', '0')
            win_rate = lifetime_stats.get('Win Rate %', '0')
            avg_kd = lifetime_stats.get('Average K/D Ratio', '0')
            hs_rate = lifetime_stats.get('Average Headshots %', '0')
            wins = lifetime_stats.get('Wins', '0')
            avg_kills = lifetime_stats.get('Average Kills', '0')
            
            # Crear un embed de Discord para mostrar las estadísticas
            embed = discord.Embed(
                title=f"Estadísticas de {player_nickname} en FACEIT",
                url=f"https://www.faceit.com/es/players/{player_nickname}",
                color=0xFF5500  # Color naranja de FACEIT
            )
            
            # Añadir avatar del jugador si está disponible
            avatar_url = player_data.get('avatar')
            if avatar_url:
                embed.set_thumbnail(url=avatar_url)
            
            # Información principal
            embed.add_field(name="Nivel", value=f"{level} ⭐", inline=True)
            embed.add_field(name="ELO", value=faceit_elo, inline=True)
            embed.add_field(name="Partidas Totales", value=matches, inline=True)
            embed.add_field(name="Victorias", value=wins, inline=True)
            embed.add_field(name="% Victoria", value=f"{win_rate}%", inline=True)
            embed.add_field(name="K/D Medio", value=avg_kd, inline=True)
            embed.add_field(name="Kills Promedio", value=avg_kills, inline=True)
            embed.add_field(name="% Headshots", value=f"{hs_rate}%", inline=True)
            
            # Añadir pie de página
            embed.set_footer(text=f"Información actualizada el {format_timestamp()}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            print(f"ERROR consultando FACEIT API: {e}")
            await interaction.followup.send(f"❌ Ocurrió un error al procesar la solicitud: {str(e)}")

    @faceit_stats.error
    async def faceit_stats_error(interaction: discord.Interaction, error):
        """Maneja errores para el comando faceit_stats."""
        await interaction.response.send_message(
            f"❌ Error al buscar estadísticas de FACEIT: {str(error)}",
            ephemeral=True
        )
    
    @tree.command(name='recientes', description='Ver estadísticas de las últimas 20 partidas en FACEIT')
    @app_commands.describe(nickname='Nickname de FACEIT del jugador')
    async def faceit_recent(interaction: discord.Interaction, nickname: str):
        """Busca y muestra estadísticas de las últimas 20 partidas de un jugador en FACEIT."""
        if not FACEIT_API_KEY:
            await interaction.response.send_message(
                "⚠️ No se ha configurado la API key de FACEIT. El administrador debe configurarla en las variables de entorno.",
                ephemeral=True
            )
            return
        
        # Primero, indicar que estamos procesando
        await interaction.response.defer(thinking=True)
        
        try:
            # Buscar al jugador por nickname
            headers = {
                "Authorization": f"Bearer {FACEIT_API_KEY}",
                "Accept": "application/json"
            }
            
            player_url = f"{FACEIT_API_URL}/players?nickname={nickname}&game=cs2"
            player_response = requests.get(player_url, headers=headers)
            
            if player_response.status_code != 200:
                await interaction.followup.send(f"❌ No se encontró el jugador '{nickname}' en FACEIT o hubo un error en la API. Código: {player_response.status_code}")
                return
            
            player_data = player_response.json()
            player_id = player_data.get('player_id')
            player_nickname = player_data.get('nickname', nickname)
            
            if not player_id:
                await interaction.followup.send(f"❌ No se encontró el jugador '{nickname}' en FACEIT.")
                return
            
            # Obtener historial de las últimas 20 partidas
            history_url = f"{FACEIT_API_URL}/players/{player_id}/history?game=cs2&offset=0&limit=20"
            history_response = requests.get(history_url, headers=headers)
            
            if history_response.status_code != 200:
                await interaction.followup.send(f"⚠️ Jugador encontrado, pero no se pudo obtener historial de partidas. Código: {history_response.status_code}")
                return
            
            history_data = history_response.json()
            
            # Crear un embed de Discord para las estadísticas recientes
            embed = discord.Embed(
                title=f"Últimas partidas de {player_nickname} en FACEIT",
                url=f"https://www.faceit.com/es/players/{player_nickname}",
                color=0xFF5500  # Color naranja de FACEIT
            )
            
            # Añadir avatar del jugador si está disponible
            avatar_url = player_data.get('avatar')
            if avatar_url:
                embed.set_thumbnail(url=avatar_url)
            
            # Analizar partidas recientes
            recent_matches = history_data.get('items', [])
            wins = 0
            losses = 0
            total_kills = 0
            total_deaths = 0
            total_hs = 0
            total_maps = 0
            
            if not recent_matches:
                embed.add_field(
                    name="Sin partidas recientes",
                    value="No se encontraron partidas recientes para este jugador.",
                    inline=False
                )
            else:
                # Obtener detalles de cada partida para contar victorias/derrotas
                for match in recent_matches:
                    match_id = match.get('match_id')
                    total_maps += 1
                    
                    # Obtener detalles de la partida
                    match_stats_url = f"{FACEIT_API_URL}/matches/{match_id}/stats"
                    match_stats_response = requests.get(match_stats_url, headers=headers)
                    
                    if match_stats_response.status_code == 200:
                        match_stats = match_stats_response.json()
                        rounds = match_stats.get('rounds', [])
                        
                        if rounds:
                            for round_info in rounds:
                                teams = round_info.get('teams', [])
                                
                                for team in teams:
                                    players = team.get('players', [])
                                    
                                    for player in players:
                                        if player.get('player_id') == player_id:
                                            # Encontramos al jugador, extraemos sus estadísticas
                                            player_stats = player.get('player_stats', {})
                                            total_kills += int(player_stats.get('Kills', '0'))
                                            total_deaths += int(player_stats.get('Deaths', '0'))
                                            total_hs += int(player_stats.get('Headshots', '0'))
                                            
                                            # También determinamos si ganó
                                            team_won = team.get('team_win', '0') == '1'
                                            if team_won:
                                                wins += 1
                                            else:
                                                losses += 1
                
                # Calcular estadísticas
                matches_with_stats = wins + losses
                win_rate = (wins / matches_with_stats) * 100 if matches_with_stats > 0 else 0
                avg_kd = total_kills / total_deaths if total_deaths > 0 else 0
                hs_percentage = (total_hs / total_kills) * 100 if total_kills > 0 else 0
                
                # Añadir estadísticas al embed
                embed.add_field(name="Partidas analizadas", value=f"{matches_with_stats}/{len(recent_matches)}", inline=True)
                embed.add_field(name="Victorias", value=f"{wins}", inline=True)
                embed.add_field(name="Derrotas", value=f"{losses}", inline=True)
                embed.add_field(name="% Victoria", value=f"{win_rate:.1f}%", inline=True)
                embed.add_field(name="K/D", value=f"{avg_kd:.2f}", inline=True)
                embed.add_field(name="% Headshots", value=f"{hs_percentage:.1f}%", inline=True)
                
                # Información sobre la tendencia
                if matches_with_stats > 0:
                    trend = "🟩 POSITIVA" if win_rate >= 50 else "🟥 NEGATIVA"
                    embed.add_field(
                        name="Tendencia",
                        value=f"{trend} ({'+' if win_rate >= 50 else '-'}{abs(wins - losses)} partidas)",
                        inline=False
                    )
            
            # Añadir pie de página
            embed.set_footer(text=f"Información actualizada el {format_timestamp()}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            print(f"ERROR consultando FACEIT API: {e}")
            await interaction.followup.send(f"❌ Ocurrió un error al procesar la solicitud: {str(e)}")

    @faceit_recent.error
    async def faceit_recent_error(interaction: discord.Interaction, error):
        """Maneja errores para el comando faceit_recent."""
        await interaction.response.send_message(
            f"❌ Error al buscar partidas recientes de FACEIT: {str(error)}",
            ephemeral=True
        )
