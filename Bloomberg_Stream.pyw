import requests
import m3u8
import time
import subprocess
import os
import sys
import multiprocessing
import platform


class Stream:
	"""
	Stream Object: organizes resources necessary for streaming;
		continually requests the updating m3u8 file, and writes
		its pointed-to transport stream files to a local file

	"""

	def __init__(self, root_url, ext_url, m3u8_url):
		self.used_uris = []  #  not shared if in other process
		self.root_url = root_url
		self.ext_url = ext_url
		self.m3u8_url = m3u8_url

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
						# avoid writing the same segments
						self.used_uris.append(ts_uri)
						f.write(requests.get(ts_uri).content)
				time.sleep(1)


class Windows_Stream(Stream):
	"""
	Windows-specific stream object; inherits from the Stream base-class

	"""

	def __init__(self, **kwargs):
		self.vid_path = f"{os.path.dirname(sys.argv[0])}\\bb_stream.ts"
		super(Windows_Stream, self).__init__(**kwargs)

	def display_video(self):
		subprocess.call([r"C:\\Program Files (x86)\\Windows Media Player\\wmplayer.exe", self.vid_path])

	def is_watching(self):
		if "wmplayer.exe" in (p.name() for p in psutil.process_iter()):
			return True
		else:
			return False

	def wrap_up(self, stream_process):
		stream_process.terminate()
		while True:
			try:
				os.remove(self.vid_path)
				break
			except Exception:
				pass


class Termux_Stream(Stream):
	"""
	Termux-specific stream object; inherits from the Stream base-class

	"""

	def __init__(self, **kwargs):
		self.vid_path = 'bb_stream.ts'
		super(Termux_Stream, self).__init__(**kwargs)

	def display_video(self):
		subprocess.call(['termux-open', '--chooser', self.vid_path])

	def is_watching(self):
		return "IDK"

	def wrap_up(self, stream_process):
		print("You'll have to wrap up things yourself")


def Stream_Session(Stream_Obj):
	"""
	Handles the facets of a stream session using a stream object:
		spins up the processes, kills them when stream is apparently 
		done being watched, and disposes of the left over resources
	"""

	stream_dl_proc = multiprocessing.Process(target=Stream_Obj.download_stream)
	stream_dl_proc.start()  # concurrent download process while everything else happens
	while not os.path.exists(Stream_Obj.vid_path) or os.stat(Stream_Obj.vid_path).st_size < 100:
		pass  # build up at least some buffer for streaming continuity and ability to open file
	Stream_Obj.display_video()
	while Stream_Obj.is_watching() is not False:
		time.sleep(1)
		pass
	else:
		Stream_Obj.wrap_up(stream_dl_proc)


if __name__ == '__main__':

	root_url = "https://liveprodusphoenixeast.global.ssl.fastly.net/USPhx-HD/Channel-TX-USPhx-AWS-virginia-1"
	ext_url = "Source-USPhx-16k-1-s6lk2-BP-07-02-81ykIWnsMsg"
	m3u8_url = f"{root_url}/{ext_url}_live.m3u8"

	if platform.system() == 'Windows':
		import psutil  # termux can't handle this, I guess
		BB_Stream = Windows_Stream(root_url=root_url, ext_url=ext_url, m3u8_url=m3u8_url)
	if platform.system() == 'Linux' and 'termux' in os.environ['SHELL']:
		BB_Stream = Termux_Stream(root_url=root_url, ext_url=ext_url, m3u8_url=m3u8_url)

	Stream_Session(BB_Stream)
