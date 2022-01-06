import os

import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from dotenv import load_dotenv

#To get the bot online
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#Test command
bot = commands.Bot(command_prefix="!")
slash = SlashCommand(bot)

@slash.slash(
	name="test",
	description="Sends a test image"
)

async def test(ctx:SlashContext):
	await ctx.send(file=discord.File('testPic.png'))

bot.run(TOKEN)