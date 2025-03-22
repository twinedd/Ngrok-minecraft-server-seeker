import discord, threading
from discord.ext import commands
from  mcstatus import JavaServer
from mcstatus.motd import Motd
import asyncio
import requests
from lib_mc2 import to_ansi_123

token = ''
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
servers = False

@bot.event
async def on_ready():
    activity = discord.Activity(name=" ngrok servers", type=3)
    await bot.change_presence(status=discord.Status.online, activity=activity)

def create_embed_forscan():
    embed = discord.Embed(title = "Scanning is started!",description = "It may take some time...",color = discord.Colour.default())
    embed.set_author(name="NgrokSeeker", icon_url="https://github.com/twinedd/pngs/raw/main/icons8--128.png")
    return embed

def create_embed_forfound(list_players, motd, players_online, version, ip):
    ServerInfo = requests.get(f'https://api.mcsrvstat.us/3/{ip}')
    embed = discord.Embed(title="Succesfully founded server",description=f"**Player's** {list_players}\n**Server's description:** {motd}",color=discord.Colour.green(),)
    embed.set_author(name = 'NgrokSeeker', icon_url ='https://github.com/twinedd/pngs/raw/main/green-wifi-15069.png')
    embed.add_field(name = "Server's ip:", value = f'```{ip}```')
    
    embed.set_thumbnail(url=f'https://api.mcsrvstat.us/icon/{ip}')
    embed.set_footer(text='NgrokSeeker')

    if ServerInfo.status_code == 200:
        ServerJson = ServerInfo.json()
        mods = False
        core='Vanilla'
        try:
            ServerJson['mods']
            mods = True
        except:
            pass

        try:
            core = ServerJson['software']
        except:
            pass

        embed.add_field(name = "Server's stats:", value = f"**Version:** {version}\n**Player's count:** {players_online}\n**License:** {ServerJson['eula_blocked']}\n**Core**: {core}\n**Modded**: {mods}")
    else:
        embed.add_field(name = "Server's stats:", value = f"**Version:** {version}\n**Player's count:** {players_online}")

    return embed

def create_embed_forstop():
    embed = discord.Embed(title = 'Succesfully stoped the scanning', description = 'You can start scanning again by slash command', color = discord.Colour.red())
    embed.set_author(name = '❌ NgrokSeeker')
    return embed

@bot.slash_command(description="Starts scanning")
async def start_scanning(ctx, port_range1 = 10000, port_range2 = 30000, version_check = 'any'):
    global servers
    if not servers:
        list_servers = []
        await ctx.respond(embed = create_embed_forscan())
        for port in range(int(port_range1), int(port_range2)):
            for host in range(1,8):
                list_servers.append(f'{host}.tcp.eu.ngrok.io:{port}')
        for i in range(1,15):
            thread = threading.Thread(target = randomizer, args = (ctx, list_servers, version_check))
            thread.start()
    else:
        await ctx.respond('you cant start one more')
        

def randomizer(ctx, list_servers, version_check):
    global servers
    servers = True
    while servers:
        for i in range(1,8):
            if len(list_servers) % 50 == 0:
                bot.loop.create_task(bot.change_presence(status=discord.Status.online, activity=discord.Activity(name=f" ngrok servers | current port: {list_servers[0].split(':')[1]}", type=3)))
            if not servers:
                break
            try:
                ip = list_servers.pop(0)
                server = JavaServer.lookup(f"{ip}", .3).status()
                if not server.players.sample:
                    list_players = 'no players online'
                else:
                    list_players = ", ".join([player.name for player in server.players.sample])
                version = str(server.version).split("'")[1]
                if version_check != 'any' and int(''.join(version.split('.')[-2:])) > int(''.join(version_check.split('.')[-2:])):
                    print('return')
                    return
                bot.loop.create_task(ctx.send(embed = create_embed_forfound(list_players = list_players, motd = f'```ansi\n{to_ansi_123(Motd.parse(server.motd.raw).to_minecraft())}```', version = version, players_online = server.players.online, ip = ip)))
            except:
                pass

@bot.slash_command()
async def stop_scanning(msg):
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(name=" ngrok servers", type=3))
    global servers
    servers = False
    await msg.respond(embed = create_embed_forstop())

@bot.slash_command()
async def ping(msg, ip):
    try:
        server = JavaServer.lookup(f"{ip}", .3).status()
        if not server.players.sample:
            list_players = 'no players online'
        else:
            list_players = ", ".join([player.name for player in server.players.sample])
        version = str(server.version).split("'")[1]
        await msg.respond(embed = create_embed_forfound(list_players = list_players, motd = f'```ansi\n{to_ansi_123(Motd.parse(server.motd.raw).to_minecraft())}```', version = version, players_online = server.players.online, ip = ip))
    except Exception as s:
        await msg.respond('the server is not responding')
        pass

bot.run(token)
