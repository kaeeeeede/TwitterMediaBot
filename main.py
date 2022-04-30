import os
import download_manager
from db import db
import datetime

import lightbulb
from hikari.presences import Status, Activity
import hikari.errors
from hikari.messages import MessageFlag
from hikari.interactions import ResponseType

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
download_timeout = int(os.getenv('DOWNLOAD_TIMEOUT'))

download_manager.max_download_duration = download_timeout

bot = lightbulb.BotApp(token = TOKEN)

report_guild_ids = [int(server_id) for server_id in os.getenv('REPORT_SERVER_IDS').split(",")]


@bot.command
@lightbulb.option("address", "Enter a URL")
@lightbulb.command("linkmedia", "Downloads (video) media from the specified URL", ephemeral = False, auto_defer = False)
@lightbulb.implements(lightbulb.SlashCommand)

async def linkMedia(ctx):
	try:
		await ctx.respond("hold up", flags = MessageFlag.EPHEMERAL)
		await bot.update_presence(status = Status.DO_NOT_DISTURB, activity = Activity(name = "dead or is busy", type = 0))
	
		path = download_manager.downloadMedia(ctx.options.address)
		filesize_bytes = get_filesize(path)
		filesize_mb = format_byte_to_megabyte(filesize_bytes)
		
		await ctx.respond(attachment = path)

		db.execute("INSERT INTO interactions (datetime, url, size) VALUES (?, ?, ?)", (datetime.datetime.now(), filepathToUrl(path), filesize_bytes))		
		db.commit()		

	except hikari.errors.ClientHTTPResponseError as e:
		await ctx.respond(f'The absolute unit of a file was way too large ({filesize_mb} MB) for Discord to handle.', flags = MessageFlag.EPHEMERAL)

	except RuntimeError as e:
		await ctx.respond("The file took too long to download.", flags = MessageFlag.EPHEMERAL)

	except BaseException as e:
		await ctx.respond("Something unexpected went wrong. Trying again will likely not help, but feel free to do so.", flags = MessageFlag.EPHEMERAL)
		raise e

	finally:
		await bot.update_presence(status = Status.DO_NOT_DISTURB, activity = Activity(type = 3, name='the chat'))


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
