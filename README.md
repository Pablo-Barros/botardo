# Botardo - Bot de Discord Multipropósito

Un bot de Discord modular diseñado para múltiples funcionalidades:
1. Monitorizar y eliminar mensajes con direcciones IP
2. Consultar estadísticas de jugadores en FACEIT

## Características

### Seguridad
- Detecta y elimina mensajes que contienen "connect" seguido de una dirección IP
- Monitorea tanto mensajes nuevos como mensajes editados
- Configurable para vigilar canales específicos en cada servidor
- Notifica al usuario cuando sus mensajes son eliminados

### Integración con FACEIT
- Comando `/elo`: Muestra el ELO y nivel de un jugador en FACEIT
- Comando `/stats`: Muestra estadísticas completas de un jugador
- Comando `/recientes`: Muestra el rendimiento en las últimas 20 partidas

### Administración
- Comando `/canal`: Permite configurar qué canal monitorizar para IPs
- Comando `/checkperms`: Verifica si el bot tiene los permisos necesarios
- Comando `/sincronizar`: Sincroniza manualmente los comandos con Discord
- Comando `/comandos`: Muestra todos los comandos disponibles

## Arquitectura

El código está organizado en una estructura modular para facilitar el mantenimiento:

```
/botardo/
├── main.py              # Punto de entrada principal
├── config.py            # Configuraciones y variables globales
├── commands/            # Comandos del bot
│   ├── general.py       # Comandos básicos (ping, info, etc.)
│   ├── admin.py         # Comandos administrativos
│   └── faceit.py        # Comandos para integración con FACEIT
├── events/              # Manejadores de eventos
│   ├── ready.py         # Evento on_ready
│   └── messages.py      # Eventos relacionados con mensajes
└── utils/               # Utilidades
    └── helpers.py       # Funciones auxiliares
```

## Requisitos

- Python 3.8 o superior
- Token de bot de Discord
- API Key de FACEIT (opcional, solo para comandos de FACEIT)
- Permisos de Discord adecuados

## Variables de Entorno

Crear un archivo `.env` basado en `.env.example` con:

```
DISCORD_TOKEN=tu-token-aquí
FACEIT_API_KEY=tu-api-key-aquí (opcional)
```

## Instalación Local

1. Clona este repositorio
2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```
3. Configura las variables de entorno
4. Ejecuta el bot:
   ```
   python main.py
   ```

## Despliegue en Railway

Este proyecto está configurado para ser desplegado en Railway:

1. Crea una cuenta en [Railway](https://railway.app)
2. Crea un nuevo proyecto y conecta tu repositorio de GitHub
3. Configura las variables de entorno (`DISCORD_TOKEN` y opcionalmente `FACEIT_API_KEY`)
4. Railway detectará automáticamente el archivo `requirements.txt` e instalará las dependencias
5. Despliega el proyecto, Railway ejecutará automáticamente `python main.py`

## Invitación del Bot

Para que el bot funcione correctamente con comandos slash, asegúrate de invitarlo con los scopes correctos:

```
https://discord.com/oauth2/authorize?client_id=TU_CLIENT_ID&permissions=275414829120&scope=bot%20applications.commands
```

Es **CRÍTICO** incluir el scope `applications.commands` para que los comandos slash funcionen.

## Permisos Necesarios

Para funcionar correctamente, el bot necesita estos permisos:
- Ver canales
- Enviar mensajes
- Gestionar mensajes (para eliminar mensajes con IPs)
- Usar comandos de aplicación (para comandos slash)

## Comandos Disponibles

### Generales
- `/ping`: Verifica si el bot está funcionando
- `/info`: Muestra información sobre el propósito del bot
- `/comandos`: Lista todos los comandos disponibles

### Administración
- `/canal [#channel]`: Configura qué canal monitorizar para mensajes con IPs
- `/checkperms`: Verifica si el bot tiene los permisos necesarios
- `/sincronizar`: Sincroniza los comandos slash (solo administradores)

### FACEIT
- `/elo [nickname]`: Muestra el ELO y nivel de un jugador
- `/stats [nickname]`: Muestra estadísticas completas del jugador
- `/recientes [nickname]`: Muestra las estadísticas de las últimas 20 partidas

## Contribuir

Las contribuciones son bienvenidas. Por favor, mantén la estructura modular del código al añadir nuevas características.
