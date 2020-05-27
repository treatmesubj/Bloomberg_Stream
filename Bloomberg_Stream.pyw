import requests
import m3u8
import time
import subprocess
import os
import sys
import multiprocessing
import platform
if platform.system() == 'Windows':
	import psutil


class Stream:

	def __init__(self, root_url, ext_url, m3u8_url):
		self.used_uris = []  #  not shared if in other process
		self.root_url = root_url
		self.ext_url = ext_url
		self.m3u8_url = m3u8_url
		if platform.system() == 'Windows':
			self.vid_path = f"{os.path.dirname(sys.argv[0])}\\bb_stream.ts"
		if platform.system() == 'Linux':
			self.vid_path = 'bb_stream.ts'

	def download_stream(self):
		if os.path.exists(self.vid_path):
			os.remove(self.vid_path)
		with open(self.vid_path, "wb") as f:
			while True:
				r = requests.get(self.m3u8_url)
				m3u8_file = m3u8.loads(r.text.replace("Source", f"{self.root_url}/Source"))
				ts_uris = [seg['uri'] for seg in m3u8_file.data['segments']]
				for ts_uri in ts_uris:
					if ts_uri not in self.used_uris:
						self.used_uris.append(ts_uri)
						f.write(requests.get(ts_uri).content)
				time.sleep(1)

	def display_video(self):
		if platform.system() == 'Windows':
			subprocess.call([r"C:\\Program Files (x86)\\Windows Media Player\\wmplayer.exe", self.vid_path])
		if platform.system() == 'Linux':  # intended for Termux-Android
			subprocess.call(['termux-open', '--chooser', self.vid_path])

	def watching(self):
		if platform.system() == 'Windows' and "wmplayer.exe" in (p.name() for p in psutil.process_iter()):
			return True
		else:
			return False


if __name__ == '__main__':

	root_url = "https://liveprodusphoenixeast.global.ssl.fastly.net/USPhx-HD/Channel-TX-USPhx-AWS-virginia-1"
	ext_url = "Source-USPhx-16k-1-s6lk2-BP-07-02-81ykIWnsMsg"
	m3u8_url = f"{root_url}/{ext_url}_live.m3u8"
	print(f"{m3u8_url}")

	BB_Stream = Stream(root_url=root_url, ext_url=ext_url, m3u8_url=m3u8_url)
	stream_dl_proc = multiprocessing.Process(target=BB_Stream.download_stream)
	stream_dl_proc.start()

	while not os.path.exists(BB_Stream.vid_path) or os.stat(BB_Stream.vid_path).st_size < 100:
		pass

	BB_Stream.display_video()

	if platform.system() == 'Windows':
		while BB_Stream.watching():
			time.sleep(1)
			pass
		else:
			stream_dl_proc.terminate()
			while True:
				try:
					os.remove(BB_Stream.vid_path)
					break
				except Exception:
					pass
			print("done streaming")
