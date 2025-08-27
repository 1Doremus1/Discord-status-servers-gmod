import discord
from discord.ext import commands, tasks
import asyncio

from steam.game_servers import a2s_info, a2s_players

TOKEN = "BOT TOKEN"
SERVER_ADDRESS = ("IP SERVER", 27015)
CHANNEL_ID = CHANEL ID

status_message = None

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

async def get_server_info():
    try:
        info = await asyncio.to_thread(a2s_info, SERVER_ADDRESS)
        players = await asyncio.to_thread(a2s_players, SERVER_ADDRESS)

        return {
            "name": info.get('name', "Неизвестно"),
            "map": info.get('map', 'Неизвестно'),
            "players": f"{info.get('players', 0)}/{info.get('max_players', 0)}",
        }
    except Exception as e:
        return {"error": str(e)}


def create_embed(data):
    if "error" in data:
        embed = discord.Embed(
            title="⚠️ Ошибка подключения",
            description=f"Error {data['error']}",
            color=discord.Color.red()
        )

        return embed, None

    embed = discord.Embed(
        title=f"**{data['name']}**",
        description="━━━━━━━━━━━━━━━━━━━━━━━━\n\u200B",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url="")
    embed.add_field(name=f"🌍  `Карта` {data['map']}\u200B", value="", inline=False)
    embed.add_field(name=f"👥  `Игроки` {data['players']}\u200B", value="", inline=False)
    embed.add_field(name=f"🚀  `Прямое подключение`\u200B", value="**steam://connect/46.174.53.166:27015**", inline=False)
    embed.add_field(name=f"\u200B", value="━━━━━━━━━━━━━━━━━━━━━━━━")
    embed.set_image(url="")
    embed.set_footer(text="Информация обновляеться каждые 5 минут.")

    return embed


@tasks.loop(minutes=5)
async def update_status():
    global status_message
    channel = bot.get_channel(CHANNEL_ID)

    data = await get_server_info()
    embed = create_embed(data)

    if status_message is None:
        status_message = await channel.send(embed=embed)
    else:
        try:
            await  status_message.edit(embed=embed)
        except discord.NotFound:
            status_message = await channel.send(embed=embed)

@bot.event
async def on_ready():
    print(f"Bot {bot.user} loaded!")
    update_status.start()

bot.run(TOKEN)
