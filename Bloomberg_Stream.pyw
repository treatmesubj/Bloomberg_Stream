import requests
import m3u8
import time
import subprocess
import os
import sys
import multiprocessing
import platform
import webbrowser


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
		self.bless_dl = False
		self.keep_dl = False

		if os.path.exists(self.vid_path):
			os.remove(self.vid_path)
			while os.path.exists(self.vid_path):
				pass

	def download_stream(self):
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
		self.vid_path = f"{os.getcwd()}\\bb_stream.mp4"
		self.ps_html_path = f"{os.getcwd()}\\Bloomberg_Stream.html"
		super(Windows_Stream, self).__init__(**kwargs)

	def display_local_video(self):
		subprocess.call([r"C:\\Program Files (x86)\\Windows Media Player\\wmplayer.exe", self.vid_path])

	def is_watching(self):
		if "wmplayer.exe" in (p.name() for p in psutil.process_iter()):
			return True
		else:
			return False

	def wrap_up(self, stream_dl_process):
		stream_dl_process.terminate()
		while True:
			try:
				os.remove(self.vid_path)
				break
			except Exception:
				pass

	def pure_stream(self):
		while True:
			if os.path.exists(self.ps_html_path):
				webbrowser.open(self.ps_html_path)
				break
			else:  # write html file to be opened
				with open(self.ps_html_path, "w") as f:
					f.write(
"""<script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
<body style="background-color:black;">
  <video id="video" class="videoCentered" controls="" autoplay="" style="position: fixed; height: 100%; width: 100%"></video>
</body>
<script>
  var video = document.getElementById('video');
  var videoSrc = 'https://liveprodusphoenixeast.global.ssl.fastly.net/USPhx-HD/Channel-TX-USPhx-AWS-virginia-1/Source-USPhx-16k-1-s6lk2-BP-07-02-81ykIWnsMsg_live.m3u8';
  if (Hls.isSupported()) {
    var hls = new Hls();
    hls.loadSource(videoSrc);
    hls.attachMedia(video);
    hls.on(Hls.Events.MANIFEST_PARSED, function() {
      video.play();
    });
  }
  else if (video.canPlayType('application/vnd.apple.mpegurl')) {
    video.src = videoSrc;
    video.addEventListener('loadedmetadata', function() {
      video.play();
    });
  }
</script>""")



class Termux_Stream(Stream):
	"""
	Termux-specific stream object; inherits from the Stream base-class

	"""

	def __init__(self, **kwargs):
		self.vid_path = 'bb_stream.mp4'
		super(Termux_Stream, self).__init__(**kwargs)

	def display_local_video(self):
		# subprocess.call(['termux-open', '--chooser', self.vid_path])  # VLC Media Player seems to work
		subprocess.call(['am', 'start', '--user', '0', '-n', 'org.videolan.vlc/org.videolan.vlc.gui.video.VideoPlayerActivity', '-d', f"{os.getcwd()}/{self.vid_path}"])  # to run local file

	def is_watching(self):
		input("Hit Enter to terminate stream download session: ")
		return False

	def wrap_up(self, stream_dl_process):
		stream_dl_process.terminate()
		if not self.keep_dl:
			while True:
				try:
					os.remove(self.vid_path)
					break
				except Exception:
					pass


	def pure_stream(self):
		subprocess.call(['am', 'start', '--user', '0', '-n', 'org.videolan.vlc/org.videolan.vlc.gui.video.VideoPlayerActivity', '-a', 'android.intent.action.VIEW', '-d', self.m3u8_url])  # to stream directly!


def Stream_Session(Stream_Obj):
	"""
	Handles the facets of a stream session using a stream object:
		spins up the processes, kills them when stream is apparently 
		done being watched, and disposes of the left over resources
	"""

	if Stream_Obj.bless_dl:
		stream_dl_proc = multiprocessing.Process(target=Stream_Obj.download_stream)
		stream_dl_proc.start()  # concurrent download process while everything else happens
		while not os.path.exists(Stream_Obj.vid_path):
			print("waiting for file build...", end="\r")
		while os.stat(Stream_Obj.vid_path).st_size < 4500000:
			print(f"building file buffer: {os.stat(Stream_Obj.vid_path).st_size} bytes...", end="\r")
		else:
			print("\nfile's ready")
		Stream_Obj.display_local_video()
		while Stream_Obj.is_watching() is not False:
			time.sleep(1)
			pass
		else:
			Stream_Obj.wrap_up(stream_dl_proc)

	else:
		Stream_Obj.pure_stream()


if __name__ == '__main__':

	root_url = "https://liveprodusphoenixeast.global.ssl.fastly.net/USPhx-HD/Channel-TX-USPhx-AWS-virginia-1"
	ext_url = "Source-USPhx-16k-1-s6lk2-BP-07-02-81ykIWnsMsg"
	m3u8_url = f"{root_url}/{ext_url}_live.m3u8"

	if platform.system() == 'Windows':
		import psutil  # termux can't handle this import
		BB_Stream = Windows_Stream(root_url=root_url, ext_url=ext_url, m3u8_url=m3u8_url)
		if any(arg in sys.argv for arg in ("-dl", "--download")):
			BB_Stream.bless_dl = True
			if any(arg in sys.argv for arg in ("-k", "--keep")):
				BB_Stream.keep_dl = True

	elif platform.system() == 'Linux' and 'termux' in os.environ['SHELL']:
		BB_Stream = Termux_Stream(root_url=root_url, ext_url=ext_url, m3u8_url=m3u8_url)
		if any(arg in sys.argv for arg in ("-dl", "--download")):
			BB_Stream.bless_dl = True
			if any(arg in sys.argv for arg in ("-k", "--keep")):
				BB_Stream.keep_dl = True
	
	else:
		print(f"{os.environ=}\nNo support for this environment yet...")

	Stream_Session(BB_Stream)
