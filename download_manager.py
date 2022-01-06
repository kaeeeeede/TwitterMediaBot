import youtube_dl
import shutil

def downloadMedia(url, filename = "Downloads/temp", sizeLimit = "8M", cleanupBeforeDownloading = True):

	if cleanupBeforeDownloading:
		cleanup()

	ydl_opts = {
		'outtmpl' : f'{filename}.%(ext)s',
		'format' : f'best'
	}

	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
	    ydl.download([url])	

def cleanup(folder = "Downloads"):
	shutil.rmtree(folder, ignore_errors = True)		
