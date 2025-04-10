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
    
    @tree.command(name='elo', description='Buscar estadísticas de FACEIT de un jugador')
    @app_commands.describe(nickname='Nickname de FACEIT del jugador')
    async def faceit_stats(interaction: discord.Interaction, nickname: str):
        """Busca las estadísticas de FACEIT para un jugador, incluyendo su ELO y últimas 20 partidas."""
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
            
            # Obtener historial de las últimas 20 partidas
            history_url = f"{FACEIT_API_URL}/players/{player_id}/history?game=cs2&offset=0&limit=20"
            history_response = requests.get(history_url, headers=headers)
            
            if history_response.status_code != 200:
                await interaction.followup.send(f"⚠️ Jugador encontrado, pero no se pudo obtener historial de partidas. Código: {history_response.status_code}")
                return
            
            history_data = history_response.json()
            
            # Extraer y formatear la información
            player_info = player_data
            faceit_elo = player_info.get('games', {}).get('cs2', {}).get('faceit_elo', 'Desconocido')
            level = player_info.get('games', {}).get('cs2', {}).get('skill_level', 0)
            
            # Estadísticas generales
            lifetime_stats = stats_data.get('lifetime', {})
            matches = lifetime_stats.get('Matches', '0')
            win_rate = lifetime_stats.get('Win Rate %', '0')
            avg_kd = lifetime_stats.get('Average K/D Ratio', '0')
            hs_rate = lifetime_stats.get('Average Headshots %', '0')
            
            # Crear un embed de Discord para mostrar las estadísticas
            embed = discord.Embed(
                title=f"Perfil FACEIT de {player_info.get('nickname')}",
                url=f"https://www.faceit.com/es/players/{player_info.get('nickname')}",
                color=0xFF5500  # Color naranja de FACEIT
            )
            
            # Añadir avatar del jugador si está disponible
            avatar_url = player_info.get('avatar')
            if avatar_url:
                embed.set_thumbnail(url=avatar_url)
            
            # Información principal
            embed.add_field(name="Nivel", value=f"{level} ⭐", inline=True)
            embed.add_field(name="ELO", value=faceit_elo, inline=True)
            embed.add_field(name="Partidas", value=matches, inline=True)
            embed.add_field(name="% Victoria", value=f"{win_rate}%", inline=True)
            embed.add_field(name="K/D Medio", value=avg_kd, inline=True)
            embed.add_field(name="% HS", value=f"{hs_rate}%", inline=True)
            
            # Información sobre las últimas partidas
            recent_matches = history_data.get('items', [])
            wins = 0
            losses = 0
            
            if recent_matches:
                # Imprimir información de depuración de la primera partida para análisis
                print(f"DEBUG - Estructura de datos de la primera partida:")
                if recent_matches and len(recent_matches) > 0:
                    first_match = recent_matches[0]
                    print(f"Llaves principales: {list(first_match.keys())}")
                    
                for match in recent_matches:
                    # Determinar el resultado de la partida para el jugador
                    match_id = match.get('match_id')
                    
                    # Obtener los detalles de la partida individual
                    match_details_url = f"{FACEIT_API_URL}/matches/{match_id}"
                    match_details_response = requests.get(match_details_url, headers=headers)
                    
                    if match_details_response.status_code == 200:
                        match_details = match_details_response.json()
                        
                        # Determinar a qué equipo pertenece el jugador y si ganó
                        faction1_roster = match_details.get('teams', {}).get('faction1', {}).get('roster', [])
                        faction2_roster = match_details.get('teams', {}).get('faction2', {}).get('roster', [])
                        
                        player_team = None
                        for player_info in faction1_roster:
                            if player_info.get('player_id') == player_id:
                                player_team = 'faction1'
                                break
                        
                        if player_team is None:
                            for player_info in faction2_roster:
                                if player_info.get('player_id') == player_id:
                                    player_team = 'faction2'
                                    break
                        
                        if player_team:
                            winner = match_details.get('results', {}).get('winner')
                            if winner == player_team:
                                wins += 1
                            elif winner:  # Si hay un ganador pero no es el equipo del jugador
                                losses += 1
                
                # Calcular porcentaje de victoria
                recent_win_rate = 0
                if wins + losses > 0:
                    recent_win_rate = (wins / (wins + losses)) * 100
                
                embed.add_field(
                    name="Últimas 20 partidas",
                    value=f"🏆 {wins} victorias | 💀 {losses} derrotas | 📊 {recent_win_rate:.1f}% victoria",
                    inline=False
                )
            
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
