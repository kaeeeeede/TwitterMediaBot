import yt_dlp
import shutil

latest_download_destination = ""
max_download_duration = 60*60


def progress_hook(s):
	if (s['status'] == 'downloading') and (s['elapsed'] >= max_download_duration):
		raise RuntimeError("Took too long to download!")


	elif s['status'] == 'finished':
		global latest_download_destination
		latest_download_destination = s['filename']
	

def downloadMedia(url, path = "Downloads", cleanupBeforeDownloading = True):

	if cleanupBeforeDownloading:
		cleanup()

	ydl_opts = {
		'outtmpl' : f'{path}/%(webpage_url)s.%(ext)s',
		'format' : f'best',
		'progress_hooks' : [progress_hook]
	}

	with yt_dlp.YoutubeDL(ydl_opts) as ydl:
	    print(ydl.download([url]))	 

	return latest_download_destination   

def cleanup(folder = "Downloads"):
	shutil.rmtree(folder, ignore_errors = True)
