import os
import discord
import download_manager

from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
download_timeout = int(os.getenv('DOWNLOAD_TIMEOUT'))

download_manager.max_download_duration = download_timeout

bot = commands.Bot(command_prefix="!")
slash = SlashCommand(bot, sync_commands=True)

@slash.slash(
	name="linkMedia",
	description="Takes a URL",
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
	await ctx.defer()

	try:
		path = download_manager.downloadMedia(address)
		await ctx.send(file=discord.File(path))

	except discord.errors.HTTPException as e:
		filesize = format_byte_to_megabyte(get_filesize(path))
		await ctx.send(f'The absolute unit of a file was way too large ({filesize} MB) for Discord to handle. We may or may not handle this with file hosting services in the near or far future.')

	except HTTPError as e:
		await ctx.send("Could not establish a connection.")

	except RuntimeError as e:
		await ctx.send("The file took too long to download.")

	except BaseException as e:
		await ctx.send("Something unexpected went wrong. Trying again will likely not help, but feel free to do so.")
		raise e

@bot.event
async def on_ready():
	print("Ready!")

def get_filesize(path):
	return os.path.getsize(path)

def format_byte_to_megabyte(byte):
	return "{:.2f}".format(byte/1000/1000)
	
bot.run(TOKEN)

