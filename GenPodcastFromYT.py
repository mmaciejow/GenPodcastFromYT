#!/usr/bin/env python
# encoding: utf-8
# @author: Maciej Maciejowski
# @www: myenv.net


#from __future__ import unicode_literals

from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from requests.exceptions import ConnectionError
from mutagen.mp3 import MP3

import os
import threading 
import youtube_dl
import time

import urllib
import time
import datetime
import requests 

REFRESH_RSS = 60*30 # in sec

PLAYLIST = "xxx...."

PATH_MP3="/mnt/DYSK_USB/Downloads/YouTube-dl/"
PATH_DL_FILE=PATH_MP3+"downloaded.txt"
FILE_NAME="feed.rss"
IMAGE="https://www.youtube.com/yts/img/favicon_144-vfliLAfaB.png"
TITLE="Podcast YouTube"
DESC="Downloaded items from YouTube"

HOST="example.local"
PORT=8888
URL="http://"+HOST+":"+ str(PORT) +"/"

def start_server():

	os.chdir(PATH_MP3)

	server = HTTPServer(('', PORT), SimpleHTTPRequestHandler)
	thread = threading.Thread(target = server.serve_forever)
	thread.daemon = True
	try:
		thread.start()
	except KeyboardInterrupt:
		server.shutdown()
		sys.exit(0)

	print("Server running at port %d" % (PORT))

def dlAudio():

	print("DL Audio:")
	ydl_opts = {
		'download_archive': PATH_DL_FILE,
		'outtmpl': PATH_MP3+'%(title)s.%(ext)s',    
		#'noplaylist':True,
		'extractaudio':True,
		'nooverwrites':True,
		'audioformat':'mp3',
		'format': 'bestaudio/best',
		'cachedir': False,
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '192',
			}],
		}

	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		vidinfo = ydl.extract_info(PLAYLIST, download = True)

	  
	if not ydl.in_download_archive(vidinfo):
		ydl.download([PLAYLIST])
		ydl.record_download_archive(vidinfo)
	
def gen_rss():

	out=""
	out+="<?xml version=\"1.0\" encoding=\"UTF-8\"?> \n"
	out+="<rss xmlns:itunes=\"http://www.itunes.com/dtds/podcast-1.0.dtd\" version=\"2.0\"> \n"
	out+="\t <channel> \n"
	out+="\t <title>"+ TITLE +" </title> \n"
	out+="\t <description>"+ DESC +"</description> \n"
	out+="\t <itunes:image href=\""+IMAGE+"\" /> \n"
	out+="\t <link>"+ URL +"feed.rss</link> \n"


	for root, dirs, files in os.walk(PATH_MP3):  
		for filename in files:
			if filename.endswith(".mp3"):

				name = os.path.splitext(filename)[0]
				pathFile = os.path.join(root, filename)		
				encodeFile = urllib.quote(filename)
				
				t = os.path.getmtime(pathFile)
				time = datetime.datetime.fromtimestamp(t)
				time2 = time.strftime("%a, %d %b %Y %H:%M:%S +0000")
				
				size = os.path.getsize(pathFile)
				
				audio = MP3(pathFile)
				length = audio.info.length	
				duration = str(datetime.timedelta(seconds=int(length) ))
				
				out+="\n"
				out+="\t <item>  \n"
				out+="\t\t <guid>"+name+"</guid> \n"
				out+="\t\t <link>"+name+"</link> \n"
				out+="\t\t <title>"+name+"</title> \n"
				out+="\t\t <description>"+name+"</description> \n"
				out+="\t\t <pubDate>"+time2+"</pubDate> \n"
				out+="\t\t <enclosure url=\""+URL+encodeFile+"\" \n"
				out+="\t\t type=\"audio/mpeg\" length=\""+str(size)+"\"/> \n" 
				out+="\t\t <itunes:duration>"+str(duration)+"</itunes:duration> \n" 
				out+="\t\t </item> \n"
				
	out+="\t </channel> \n"
	out+="</rss> \n"

	file = open(PATH_MP3+FILE_NAME,"w") 
	file.write(out) 
	file.close() 

def check_net():
	while(True):
		try:
		   requests.get("http://example.com")
		   return
		except ConnectionError as e:
			time.sleep(60)

				
start_server()
	
while True:

	check_net()
	dlAudio()
	time.sleep(2)
	gen_rss()
	time.sleep(REFRESH_RSS)
	
	
