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
slash = SlashCommand(bot, sync_commands=True)

@slash.slash(
	name="Input",
	description="Takes a URL",
	guild_ids=[928649725396267049],
	options=[
		create_option(
			name="URL",
			description="Enter a URL",
			required=True,
			option_type=3,
		)
	],
)

async def Input(ctx:SlashContext, URL):
	await ctx.send(URL)

bot.run(TOKEN)



