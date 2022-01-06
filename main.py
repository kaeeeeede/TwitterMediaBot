import os
import discord
import download_manager

from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from dotenv import load_dotenv

#To get the bot online
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#Test command
bot = commands.Bot(command_prefix="!")
slash = SlashCommand(bot, sync_commands=True)

@slash.slash(
	name="linkMedia",
	description="Takes a URL",
	guild_ids=[928649725396267049],
	options=[
		create_option(
			name="address",
			description="Enter a URL",
			required=True,
			option_type=3,
		)
	],
)

async def linkMedia(ctx:SlashContext, address):
	try:
		path = download_manager.downloadMedia(address)
		await ctx.send(file=discord.File(path))

	except discord.errors.HTTPException as e:
		await ctx.send("The absolute unit of a file was way too large for Discord to handle. We may or may not handle this with file hosting services in the near or far future.")

bot.run(TOKEN)

