import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

initial_extensions = [
    "cogs.demissao",
    "cogs.ausencia",
    "cogs.exoneracao",
    "cogs.comandos",
]


async def load_extensions():
    for ext in initial_extensions:
        await bot.load_extension(ext)


@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔵 {len(synced)} comandos de barra sincronizados.")
    except Exception as e:
        print(f"Erro ao sincronizar comandos: {e}")


async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
