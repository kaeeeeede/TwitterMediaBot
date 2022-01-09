import youtube_dl
import shutil

latest_download_destination = ""
max_download_duration = 60*60


def progress_hook(s):
	if (s['status'] == 'downloading') and (s['elapsed'] >= max_download_duration):
		raise RuntimeError("Took too long to download!")


	elif s['status'] == 'finished':
		global latest_download_destination
		latest_download_destination = s['filename']
	

def downloadMedia(url, filename = "Downloads/temp", cleanupBeforeDownloading = True):

	if cleanupBeforeDownloading:
		cleanup()

	ydl_opts = {
		'outtmpl' : f'{filename}.%(ext)s',
		'format' : f'best',
		'progress_hooks' : [progress_hook]
	}

	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
	    print(ydl.download([url]))	 

	return latest_download_destination   

def cleanup(folder = "Downloads"):
	shutil.rmtree(folder, ignore_errors = True)
