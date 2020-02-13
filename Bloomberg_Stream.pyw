import requests
import m3u8
import time
import threading
import subprocess
import os
import sys
import psutil


class Stream:

	def __init__(self, root_url, ext_url, m3u8_url):
		self.used_uris = []
		self.root_url = root_url
		self.ext_url = ext_url
		self.m3u8_url = m3u8_url

	def download_stream(self):
		with open("video.ts", "wb") as f:
			while True:
				r = requests.get(self.m3u8_url)

				m3u8_file = m3u8.loads(r.text.replace("Source", f"{self.root_url}/Source"))

				ts_uris = [seg['uri'] for seg in m3u8_file.data['segments']]
				for ts_uri in ts_uris:
					if ts_uri not in self.used_uris:
						# print(ts_uri)
						self.used_uris.append(ts_uri)
						f.write(requests.get(ts_uri).content)

				time.sleep(1)


	def display_video(self):
		subprocess.call([r"C:\\Program Files (x86)\\Windows Media Player\\wmplayer.exe", f"{os.path.dirname(sys.argv[0])}\\video.ts"])


root_url = "https://liveprodusphoenixeast.global.ssl.fastly.net/USPhx-HD/Channel-TX-USPhx-AWS-virginia-1"
ext_url = "Source-USPhx-16k-1-s6lk2-BP-07-02-81ykIWnsMsg"
m3u8_url = f"{root_url}/{ext_url}_live.m3u8"

BB_Stream = Stream(root_url=root_url, ext_url=ext_url, m3u8_url=m3u8_url)

threading.Thread(target=BB_Stream.download_stream).start()
time.sleep(1)
threading.Thread(target=BB_Stream.display_video, daemon=True).start()

while "wmplayer.exe" in (p.name() for p in psutil.process_iter()):
	pass
print("it's over")

