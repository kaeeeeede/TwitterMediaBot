import os
import download_manager
from db import db
import datetime

import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option

import lightbulb
from hikari.presences import Status, Activity

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
download_timeout = int(os.getenv('DOWNLOAD_TIMEOUT'))

download_manager.max_download_duration = download_timeout

#bot = commands.Bot(command_prefix="!", activity=discord.Activity(type=discord.ActivityType.watching, name='the chat'))
bot = lightbulb.BotApp(token = TOKEN)
#slash = SlashCommand(bot, sync_commands=True)

report_guild_ids = [int(server_id) for server_id in os.getenv('REPORT_SERVER_IDS').split(",")]

# @slash.slash(
# 	name="linkMedia",
# 	description="Takes a URL",
# 	options=[
# 		create_option(
# 			name="address",
# 			description="Enter a URL",
# 			required=True,
# 			option_type=3,
# 		)
# 	],
# )

@bot.command
@lightbulb.option("address", "Enter a URL")
@lightbulb.command("linkmedia", "Downloads (video) media from the specified URL", ephemeral = True, auto_defer = True)
@lightbulb.implements(lightbulb.SlashCommand)

async def linkMedia(ctx):
	try:
		await bot.update_presence(status = Status.DO_NOT_DISTURB, activity = Activity(name = "dead or is busy", type = 0))
	
		path = download_manager.downloadMedia(ctx.options.address)
		filesize_bytes = get_filesize(path)
		filesize_mb = format_byte_to_megabyte(filesize_bytes)

		print(dir(ctx))

	# 	if not (target := ctx.channel):
	# 		target = ctx.author

	# 	await target.send(file=discord.File(path))
	# 	await ctx.send("Done!", hidden = True)

	# 	db.execute("INSERT INTO interactions (datetime, url, size) VALUES (?, ?, ?)", (datetime.datetime.now(), filepathToUrl(path), filesize_bytes))		
	# 	db.commit()		

	# except discord.errors.HTTPException as e:
	# 	await ctx.send(f'The absolute unit of a file was way too large ({filesize_mb} MB) for Discord to handle.', hidden = True)

	# except HTTPError as e:
	# 	await ctx.send("Could not establish a connection.", hidden = True)

	# except RuntimeError as e:
	# 	await ctx.send("The file took too long to download.", hidden = True)

	# except BaseException as e:
	# 	await ctx.send("Something unexpected went wrong. Trying again will likely not help, but feel free to do so.", hidden = True)
	# 	raise e

	# finally:
	# 	await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name='the chat'))
	finally:
		pass

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
	
bot.run()
