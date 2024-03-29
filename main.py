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

import ffmpeg
import cv2	

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
download_timeout = int(os.getenv('DOWNLOAD_TIMEOUT'))

download_manager.max_download_duration = download_timeout

bot = lightbulb.BotApp(token = TOKEN)

report_guild_ids = [int(server_id) for server_id in os.getenv('REPORT_SERVER_IDS').split(",")]

@bot.command
@lightbulb.option("address", "Enter a URL")
@lightbulb.option("video_index", "Which video to download if there is more than 1. If not provided, will download all videos.", required=False, type = int)
@lightbulb.option("start_trim", "Start trim point (in seconds). Defaults to 0.", required=False, type = float)
@lightbulb.option("trim_duration", "Duration to trim. Defaults to infinity.", required=False, type = float)
@lightbulb.command("linkmedia", "Downloads (video) media from the specified URL", ephemeral = False, auto_defer = False)
@lightbulb.implements(lightbulb.SlashCommand)
async def linkMedia(ctx):
	try:
		await ctx.respond("Downloading...", flags = MessageFlag.EPHEMERAL)
		await bot.update_presence(status = Status.DO_NOT_DISTURB, activity = Activity(name = "dead or is busy", type = 0))
	
		paths = download_manager.downloadMedia(ctx.options.address, os.getenv('COOKIES_FILE'))

		if ctx.options.video_index != None:
			if video_index <= path.length:
				paths = [paths[ctx.options.video_index - 1]]

		for i,path in enumerate(paths):
			if ctx.options.trim_duration or ctx.options.start_trim:
				start_trim = ctx.options.start_trim if ctx.options.start_trim else 0

				end_trim = (start_trim + ctx.options.trim_duration) if ctx.options.trim_duration else get_video_duration(path)

				target_path = removeExtension(path) + " trimmed.mp4"

				input_file = ffmpeg.input(path)
				output_file = ffmpeg.output(input_file.trim(start=start_trim, end=end_trim), target_path)
				ffmpeg.run(output_file, overwrite_output=True)

				path = target_path

			filesize_bytes = get_filesize(path)
			filesize_mb = format_byte_to_megabyte(filesize_bytes)
			
			message = ""

			if i == 0:
				message = f"Requested by {ctx.author.mention} from <{ctx.options.address}>"

			await bot.rest.create_message(channel = ctx.channel_id, content = message, attachment = path)

			db.execute("INSERT INTO interactions (datetime, url, size) VALUES (?, ?, ?)", (datetime.datetime.now(), filepathToUrl(path), filesize_bytes))		
			db.commit()

		await ctx.respond("Done!", flags = MessageFlag.EPHEMERAL)		

	except hikari.errors.ClientHTTPResponseError as e:
		await ctx.edit_last_response(f'The absolute unit of a file was way too large ({filesize_mb} MB) for Discord to handle.')

	except RuntimeError as e:
		await ctx.edit_last_response("The file took too long to download.")

	except BaseException as e:
		await ctx.edit_last_response("Something unexpected went wrong. Trying again will likely not help, but feel free to do so.")
		raise e

	finally:
		await bot.update_presence(status = Status.ONLINE, activity = Activity(type = 3, name='the chat'))

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

def get_video_duration(path):
	video = cv2.VideoCapture(path)

	fps = video.get(cv2.CAP_PROP_FPS)
	frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)

	return frame_count / fps

bot.run()
