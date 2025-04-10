# Discord Connect-IP Bot

Un bot de Discord diseñado para detectar y eliminar automáticamente mensajes que contengan la palabra "connect" seguida de una dirección IP, ayudando a mantener la seguridad en servidores de Discord.

## Características

- Detecta mensajes que contienen la palabra "connect" seguida de una dirección IP
- Elimina automáticamente estos mensajes
- Envía una notificación temporal al usuario informándole que su mensaje ha sido eliminado
- Incluye comandos básicos para verificar el funcionamiento del bot

## Despliegue en Replit

Este proyecto está configurado para ser desplegado fácilmente en Replit, que ofrece alojamiento gratuito para bots de Discord.

### Configuración en Replit

1. Crea una cuenta en [Replit](https://replit.com) si no tienes una
2. Haz clic en el botón "+" para crear un nuevo Repl
3. Selecciona "Importar desde GitHub" y utiliza la URL de este repositorio
4. Una vez importado, agrega tu token de bot de Discord como secreto:
   - Haz clic en "Secretos" en el panel de herramientas
   - Agrega un nuevo secreto con la clave `DISCORD_TOKEN` y tu token de Discord como valor
5. Haz clic en el botón "Run" para iniciar tu bot

El bot incluye un mecanismo de keep-alive para permanecer en línea en la versión gratuita de Replit.

## Requisitos

- Python 3.8 o superior
- Token de bot de Discord
- Permisos de gestión de mensajes en el servidor

## Instalación local (alternativa)

1. Clona este repositorio o descarga los archivos

2. Instala las dependencias necesarias:
   ```
   pip install -r requirements.txt
   ```

3. Establece tu token de Discord como variable de entorno:
   ```
   export DISCORD_TOKEN=tu-token-aquí
   ```

## Cómo obtener un token de Discord

1. Ve al [Portal de desarrolladores de Discord](https://discord.com/developers/applications)
2. Crea una nueva aplicación
3. Ve a la sección "Bot" y crea un nuevo bot
4. Copia el token y establécelo como variable de entorno o en secretos de Replit
5. En la sección "OAuth2" > "Generador de URL", selecciona el alcance "bot" y los permisos "Gestionar mensajes" y "Leer historial de mensajes"
6. Utiliza la URL generada para invitar al bot a tu servidor

## Permisos necesarios

Para que el bot funcione correctamente, necesita los siguientes permisos:
- Leer mensajes
- Leer historial de mensajes
- Gestionar mensajes (para eliminar mensajes)
- Enviar mensajes (para notificaciones)

## Comandos disponibles

- `!ping`: Verifica si el bot está activo
- `!info`: Muestra información sobre el propósito del bot
