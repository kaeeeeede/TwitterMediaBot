import os
import discord
import download_manager
from db import db
import datetime

from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
download_timeout = int(os.getenv('DOWNLOAD_TIMEOUT'))

download_manager.max_download_duration = download_timeout

bot = commands.Bot(command_prefix="!", activity=discord.Activity(type=discord.ActivityType.watching, name='the chat'))
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
	try:
		await ctx.defer()
		await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.playing, name='dead or is busy'))
		path = download_manager.downloadMedia(address)
		filesize_bytes = get_filesize(path)
		filesize_mb = format_byte_to_megabyte(filesize_bytes)

		await ctx.send(file=discord.File(path))

		db.execute("INSERT INTO interactions (datetime, url, size) VALUES (?, ?, ?)", (datetime.datetime.now(), filepathToUrl(path), filesize_bytes))		
		db.commit()		

	except discord.errors.HTTPException as e:
		await ctx.send(f'The absolute unit of a file was way too large ({filesize_mb} MB) for Discord to handle. We may or may not handle this with file hosting services in the near or far future.')

	except HTTPError as e:
		await ctx.send("Could not establish a connection.")

	except RuntimeError as e:
		await ctx.send("The file took too long to download.")

	except BaseException as e:
		await ctx.send("Something unexpected went wrong. Trying again will likely not help, but feel free to do so.")
		raise e

	finally:
		await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name='the chat'))

@bot.event
async def on_ready():
	print("Ready!")	

def get_filesize(path):
	return os.path.getsize(path)

def format_byte_to_megabyte(byte):
	return "{:.2f}".format(byte/1000/1000)

def removeExtension(filename):
	return filename.rsplit(".", 1)[0]

def filepathToUrl(path):
	return removeExtension(path.split("\\", 1)[1])

def firstSecondOfDate(date):
	return datetime.datetime.combine(date, datetime.time.min)

def finalSecondOfDate(date):
	return datetime.datetime.combine(date, datetime.time.max)

def aggregateCountAndSize(interactions):
	countSum = 0
	sizeSum = 0

	for interaction in interactions:
		countSum += 1
		sizeSum += interaction[0]

	return (countSum, sizeSum)

def getTotalCountAndSizeBetween(startDate, endDate):
	interactions = db.getInteractionsBetween(firstSecondOfDate(startDate), finalSecondOfDate(endDate))
	return aggregateCountAndSize(interactions)

def createReportEmbed(sizeSum, fileCount, serverCount, startDate, endDate):
	embed = discord.Embed(title="Media link report", description=f'Served a total of **{format_byte_to_megabyte(sizeSum)} MB** over **{fileCount} files** in **{serverCount} servers!**', color=0x00ff1e)

	if startDate == endDate:
		footer = f'{startDate}'
	else:
		footer = f'{startDate} - {endDate}'

	embed.set_footer(text=footer)

	return embed
	
bot.run(TOKEN)