import discord
import subprocess
import os
from discord.ext import commands
from dotenv import load_dotenv

# Cargar el token desde el archivo .env
load_dotenv()
TOKEN = os.getenv("TOKEN")  # Usa el archivo .env para evitar exponer el token

# Lista de IDs de usuarios autorizados
USUARIOS_AUTORIZADOS = {757468382835638272, 1119394834822733925, 1279119172164649021, 1031359846823501904, 1249589124034461758}  # Sustituye con tus IDs

# Configurar los intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Definir el bot y el prefijo del comando
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    # Cambiar el estado del bot a DND y jugando Minecraft
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game("Minecraft"))

@bot.command()
async def install(ctx, *, package: str = None):
    """Instala paquetes usando pkg, apt o pip."""
    if ctx.author.id not in USUARIOS_AUTORIZADOS:
        await ctx.send("❌ No tienes permiso para usar este comando.")
        return

    if not package:
        await ctx.send("❌ Uso incorrecto. Usa: `!install <paquete>`")
        return

    # Separar el comando y el paquete
    if " " in package:
        tool, package_name = package.split(" ", 1)
    else:
        tool, package_name = "pip", package

    # Comando para instalar usando pkg, apt o pip
    try:
        if tool == "pkg":
            result = subprocess.run(f"pkg install {package_name}", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        elif tool == "apt":
            result = subprocess.run(f"apt install {package_name}", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        elif tool == "pip":
            result = subprocess.run(f"pip install {package_name}", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            await ctx.send("❌ Herramienta no reconocida. Usa `pkg`, `apt` o `pip`.")
            return

        await ctx.send(f"✅ Paquete `{package_name}` instalado correctamente usando `{tool}`.")
    
    except subprocess.CalledProcessError as e:
        await ctx.send(f"❌ Error al intentar instalar `{package_name}`: {e.stderr.decode()}")

@bot.command()
async def srv(ctx, server: str = None, *, command: str = None):
    """Envía comandos a los servidores alojados en screen."""
    if ctx.author.id not in USUARIOS_AUTORIZADOS:
        await ctx.send("❌ No tienes permiso para usar este comando.")
        return

    if not server or not command:
        await ctx.send("❌ Uso incorrecto. Usa: `!srv <servidor> <comando>`")
        return

    # Definir los nombres de sesión de screen sin el sufijo -sv
    server_sessions = {
        "terraria": "terraria",
        "bedrock": "bedrock",
        "java": "java"
    }

    if server not in server_sessions:
        await ctx.send("❌ Servidor no reconocido. Usa: `terraria`, `bedrock` o `java`.")
        return

    screen_name = server_sessions[server]

    # Enviar el comando sin comillas ni escapes innecesarios
    screen_command = f"screen -S {screen_name} -p 0 -X stuff {shlex.quote(command + '\\n')}"

    try:
        subprocess.run(screen_command, shell=True, check=True)
        await ctx.send(f"✅ Comando enviado a `{server}`: `{command}`")
    except subprocess.CalledProcessError:
        await ctx.send(f"❌ No se pudo enviar el comando. ¿El servidor `{server}` está corriendo?")

@bot.command()
async def exs(ctx, server: str = None):
    """Envía Ctrl + C para guardar y cerrar el servidor especificado en screen."""
    if ctx.author.id not in USUARIOS_AUTORIZADOS:
        await ctx.send("❌ No tienes permiso para usar este comando.")
        return

    if not server:
        await ctx.send("❌ Uso incorrecto. Usa: `!exs <servidor>`")
        return

    # Definir los nombres de sesión de screen según el servidor
    server_sessions = {
        "terraria": "terraria",
        "bedrock": "bedrock",
        "java": "java"
    }

    if server not in server_sessions:
        await ctx.send("❌ Servidor no reconocido. Usa: `terraria`, `bedrock` o `java`.")
        return

    screen_name = server_sessions[server]

    try:
        # Enviar Ctrl + C para simular la interrupción y cerrar el servidor
        screen_command = f"screen -S {screen_name} -p 0 -X stuff $'\x03'"
        subprocess.run(screen_command, shell=True, check=True)

        await ctx.send(f"✅ El servidor `{server}` ha sido guardado y cerrado correctamente con Ctrl + C.")
    except subprocess.CalledProcessError:
        await ctx.send(f"❌ No se pudo guardar y cerrar el servidor `{server}`. ¿Está corriendo?")

@bot.command()
async def clear(ctx):
    """Borra todos los mensajes del canal de mensajes directos."""
    if ctx.author.id not in USUARIOS_AUTORIZADOS:
        await ctx.send("❌ No tienes permiso para usar este comando.")
        return

    if isinstance(ctx.channel, discord.DMChannel):
        # Limpiar todos los mensajes del canal de mensajes directos
        try:
            async for message in ctx.channel.history(limit=100):  # Limitar a los últimos 100 mensajes, ajustable
                await message.delete()
            await ctx.send("✅ Todos los mensajes han sido eliminados.")
        except discord.errors.Forbidden:
            await ctx.send("❌ No tengo permisos para borrar mensajes en este canal.")
        except Exception as e:
            await ctx.send(f"❌ Ocurrió un error: {e}")
    else:
        await ctx.send("❌ Este comando solo puede ejecutarse en un canal de mensajes directos.")

@bot.command()
async def tsh(ctx, *, command: str = None):
    """Ejecuta comandos en la terminal usando el prefijo 'tsh'."""
    if ctx.author.id not in USUARIOS_AUTORIZADOS:
        await ctx.send("❌ No tienes permiso para usar este comando.")
        return

    if not command:
        await ctx.send("❌ Faltó un comando. Usa el formato `tsh <comando>`.")
        return

    try:
        # Ejecutar el comando en la terminal
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout.strip() or result.stderr.strip() or "No hubo salida."

        if len(output) > 2000:
            await ctx.send("⚠️ La salida es demasiado larga. Solo mostraré los primeros 2000 caracteres.")
            output = output[:2000]

        await ctx.send(f"```\n{output}\n```")

    except subprocess.TimeoutExpired:
        await ctx.send("⏳ El comando tardó demasiado en ejecutarse y fue cancelado.")
    except Exception as e:
        await ctx.send(f"❌ Error al ejecutar el comando: {e}")

@bot.command()
async def start(ctx, server: str = None):
    """Inicia diferentes servidores según el argumento."""
    if ctx.author.id not in USUARIOS_AUTORIZADOS:
        await ctx.send("❌ No tienes permiso para usar este comando.")
        return

    if not server:
        await ctx.send("❌ Faltó un servidor. Usa: `!start terraria-sv`, `!start bedrock-sv` o `!start java-sv`.")
        return

    if server == "terraria-sv":
        command = "bash /data/data/com.termux/files/home/servers/terraria/terraria.sh"
    elif server == "bedrock-sv":
        command = "bash /data/data/com.termux/files/home/servers/bedrock/bedrock.sh"
    elif server == "java-sv":
        command = "bash /data/data/com.termux/files/home/servers/java/java.sh"
    else:
        await ctx.send("❌ Servidor no reconocido. Usa: `terraria-sv`, `bedrock-sv` o `java-sv`.")
        return

    # Enviar mensaje diciendo que se está iniciando el servidor
    await ctx.send("Iniciando servidor, ve por un café esto puede llevar unos minutos  ☕")

    try:
        # Ejecutar el comando del servidor
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)  # Tiempo extendido a 60 segundos
        output = result.stdout.strip() or result.stderr.strip() or "No hubo salida."

        if len(output) > 2000:
            await ctx.send("⚠️ La salida es demasiado larga. Solo mostraré los primeros 2000 caracteres.")
            output = output[:2000]

        await ctx.send(f"```\n{output}\n```")

    except subprocess.TimeoutExpired:
        await ctx.send("⏳ El comando tardó demasiado en ejecutarse y fue cancelado.")
    except Exception as e:
        await ctx.send(f"❌ Error al ejecutar el comando: {e}")

@bot.command(name="ip")
async def IP(ctx):
    servidores = {
        "Terraria": {
            "IP": "play.coderx-servers.dansted.org",
            "Puerto": "56220"
        },
        "Java": "play.coderx-servers.dansted.org:10466",  # Este lo dejamos junto

        "Bedrock": {
            "IP": "play.coderx-servers.dansted.org",
            "Puerto": "3511"
        },
    }
    
    mensaje = "IPs y Puertos de los servidores:\n"
    
    for nombre, datos in servidores.items():
        if isinstance(datos, dict):
            mensaje += f"{nombre}:\nIP: {datos['IP']}\nPuerto: {datos['Puerto']}\n"
        else:
            mensaje += f"{nombre}: {datos}\n"
    
    await ctx.send(mensaje)

@bot.command()
async def info(ctx):
    """Muestra la información actual del bot."""
    embed = discord.Embed(title="Información del Bot", color=discord.Color.blue())
    embed.add_field(name="📛 Nombre", value=bot.user.name, inline=False)
    embed.add_field(name="📡 Estado", value=str(bot.status), inline=False)
    actividad = bot.activity.name if bot.activity else "Ninguna"
    embed.add_field(name="🎮 Actividad", value=actividad, inline=False)
    embed.set_thumbnail(url=bot.user.avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def botname(ctx, *, nuevo_nombre: str):
    """Cambia el nombre del bot."""
    if ctx.author.id not in USUARIOS_AUTORIZADOS:
        await ctx.send("❌ No tienes permiso para cambiar el nombre.")
        return

    await bot.user.edit(username=nuevo_nombre)
    await ctx.send(f"✅ Nombre cambiado a **{nuevo_nombre}**.")

@bot.command()
async def status(ctx, estado: str = None):
    """Cambia el estado del bot (online, idle, dnd, offline)."""
    if ctx.author.id not in USUARIOS_AUTORIZADOS:
        await ctx.send("❌ No tienes permiso para cambiar el estado.")
        return

    if not estado:
        await ctx.send("❌ Faltó el argumento. Usa el formato: `!status <estado>`.")
        return

    estados = {
        "online": discord.Status.online,
        "idle": discord.Status.idle,
        "dnd": discord.Status.dnd,
        "offline": discord.Status.offline
    }

    if estado.lower() not in estados:
        await ctx.send("❌ Estado no válido. Usa: online, idle, dnd, offline.")
        return

    await bot.change_presence(status=estados[estado.lower()])
    await ctx.send(f"✅ Estado cambiado a **{estado}**.")

@bot.command()
async def activity(ctx, tipo: str = None, *, actividad: str = None):
    """Cambia la actividad del bot (jugando, viendo, escuchando)."""
    if ctx.author.id not in USUARIOS_AUTORIZADOS:
        await ctx.send("❌ No tienes permiso para cambiar la actividad.")
        return

    if not tipo or not actividad:
        await ctx.send("❌ Faltan argumentos. Usa el formato: `!activity <tipo> <actividad>`.")
        return

    tipos = {
        "jugando": discord.Game(name=actividad),
        "viendo": discord.Activity(type=discord.ActivityType.watching, name=actividad),
        "escuchando": discord.Activity(type=discord.ActivityType.listening, name=actividad)
    }

    if tipo.lower() not in tipos:
        await ctx.send("❌ Tipo de actividad no válido. Usa: jugando, viendo, escuchando.")
        return

    await bot.change_presence(activity=tipos[tipo.lower()])
    await ctx.send(f"✅ Ahora el bot está **{tipo} {actividad}**.")

@bot.command()
async def botpic(ctx):
    """Cambia la foto de perfil del bot usando una imagen local."""
    if ctx.author.id not in USUARIOS_AUTORIZADOS:
        await ctx.send("❌ No tienes permiso para cambiar el avatar.")
        return

    try:
        with open("avatar.png", "rb") as img:
            avatar = img.read()
            await bot.user.edit(avatar=avatar)
            await ctx.send("✅ Foto de perfil actualizada con éxito.")
    except Exception as e:
        await ctx.send(f"❌ Error al cambiar la foto de perfil: {e}")

# Iniciar el bot
bot.run(TOKEN)
