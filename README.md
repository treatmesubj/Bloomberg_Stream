# Bloomberg Stream

Enjoy live Bloomberg TV in a sleek window without any of the annoyances that come with using a web browser such as JavaScript nonsense like viewing-time limits, paywalls, ad-blocker blocking, commercials, ect...

## Bloomberg_Stream.html
Uses the HTTP Live Streaming protocol via hls.js and some HTML; it can be opened with a web browser without any setup or dependencies. Video Controls allow for picture-in-a-picture, full screen, resizing, ect. Seems like it's always forced on the foreground of your screen, though. 

![alt text](https://github.com/treatmesubj/Bloomberg_Stream/blob/master/Screenshot%20(33).png)

## Bloomberg_Stream.pyw
Uses HTTP requests, subprocesses, and multiprocessing to continually request m3u8 files, download their pointed-at transport-stream files, and write them to a video file on the disk, which is concurrently played in Windows Media Player, all via Python. It's got a lot more overhead and complication than the HTML-stream, but it's cooler. 

Usage: `python Bloomberg_Stream.pyw [-dl|--download] [-k|--keep]`
```
Default Behavior: web browser, HTML, and hls.js handle stream directly; no local file is created
    [-dl|--download]: concurrently downloads the stream content to a local file, which is played in Windows Media Player
            [-k|--keep]: the local file is not deleted at the end of the streaming session
```

![alt text](https://github.com/treatmesubj/Bloomberg_Stream/blob/master/Screenshot%20(31).png)

### Android Termux
You can watch it on your phone! On Android, Bloomberg_Stream.pyw can run via Python in the Termux Linux environment and VLC Media Player! It even has closed captions and a pop-up player!

Usage: `python Bloomberg_Stream.pyw [-dl|--download] [-k|--keep]`
```
Default Behavior: VLC handles the livestream directly; no local file is created
    [-dl|--download]: concurrently downloads the stream content to a local file, which is played in VLC
            [-k|--keep]: the local file is not deleted at the end of the streaming session
```

<img src="https://github.com/treatmesubj/Bloomberg_Stream/blob/master/droid_bb.jpg" width="50%" height="50%">
