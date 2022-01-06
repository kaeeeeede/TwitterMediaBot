import youtube_dl
import shutil

latest_download_destination = ""

def finish_hook(s):
	if s['status'] == 'finished':
		global latest_download_destination
		latest_download_destination = s['filename']

def downloadMedia(url, filename = "Downloads/temp", sizeLimit = "8M", cleanupBeforeDownloading = True):

	if cleanupBeforeDownloading:
		cleanup()

	ydl_opts = {
		'outtmpl' : f'{filename}.%(ext)s',
		'format' : f'best',
		'progress_hooks' : [finish_hook]
	}

	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
	    print(ydl.download([url]))	 

	return latest_download_destination   

def cleanup(folder = "Downloads"):
	shutil.rmtree(folder, ignore_errors = True)
