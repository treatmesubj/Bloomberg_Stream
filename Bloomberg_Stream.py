import requests
import m3u8
from pprint import pprint
import time
import threading
import subprocess
import os
import sys

rooturl = "https://liveprodusphoenixeast.global.ssl.fastly.net/USPhx-HD/Channel-TX-USPhx-AWS-virginia-1"
exturl = "Source-USPhx-16k-1-s6lk2-BP-07-02-81ykIWnsMsg"
m3u8_url = f"{rooturl}/{exturl}_live.m3u8"

used_uris = []


def download_stream():
	with open("video.ts", "wb") as f:
		while True:
			try:
				r = requests.get(m3u8_url)

				m3u8_file = m3u8.loads(r.text.replace("Source", f"{rooturl}/Source"))

				ts_uris = [seg['uri'] for seg in m3u8_file.data['segments']]
				for ts_uri in ts_uris:
					if ts_uri not in used_uris:
						print(ts_uri)
						used_uris.append(ts_uri)
						f.write(requests.get(ts_uri).content)

				time.sleep(1)

			except Exception:
				raise


def display_video():
	try:
		subprocess.call([r"C:\\Program Files (x86)\\Windows Media Player\\wmplayer.exe", f"{os.path.dirname(sys.argv[0])}\\video.ts"])
	except Exception:
		raise


threading.Thread(target=download_stream).start()
time.sleep(1)
threading.Thread(target=display_video).start()
