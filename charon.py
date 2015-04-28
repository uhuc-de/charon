#!/usr/bin/python2
# -*- coding: utf-8 -*-
#
# Charon (version 3)
# This script observes a list of feeds (RSS 2.0 only!) and sends new entries to an IRC channel. 
#
# Dependencies: Python 2 should be installed.
#
# Installation:
# - Copy the charon.py into the directory *~/bin/charon* for example. 
# - Change the configuration inside the charon.py to your needs. 
# - Add a cronjob for charon.py to run every x minutes (e.g. 15 minutes).
#
# Licensed under the GPLv3: http://www.gnu.org/licenses/gpl-3.0.html


import os
import sys
import urllib2
import socket
import string
import select
import traceback
import time


### CONFIG ###

# Name of the IRC server
HOST = 'irc.example.net'

# Port of the IRC server
PORT = 6667

# Channel, to post the new feed entries
CHANNEL = '#example'

# Nick of the Bot
NICK = 'charon'

# Name of the Bot
REALNAME = 'FeedBot'

# Identification
IDENT="CharonRSS"


# List of feeds to observe (RSS2.0 only)
FEED_LIST = [ "https://www.python.org/dev/peps/peps.rss/","http://www.linux.org/originalcontent" ]

# File which saves the last posted entries
HISTORY_FILE = "~/bin/charon/history"



### CODE ###

def getNewPosts():

	msgqueue = []

	for feed in FEED_LIST:
		try:
			# download the feed an filter titles and links
			response = urllib2.urlopen(feed)
			html = response.read().split("\n")
			unfilteredFeeds = []
			for line in html:
				if ("<link>" in line):
					unfilteredFeeds.append(line.strip()[6:-7])
				if ("<title>" in line):
					unfilteredFeeds.append(line.strip()[16:-11])

			# merge the lines together
			filteredFeeds = []
			unfilteredFeeds = unfilteredFeeds[2:]
			r = range(len(unfilteredFeeds)/2 )
			for i in r :
				filteredFeeds.append("%s ( %s )" % ( unfilteredFeeds[i*2], unfilteredFeeds[i*2+1] ))

			# check if posts are already in the history file
			FILE = open( HISTORY_FILE, "r" )
			history = FILE.read()
			FILE.close()
			for f in filteredFeeds:
				if f in history: 
					# post is in historyfile
					pass
				else:
					# post is new: write to history and append to msgqueue
					FILE = open ( HISTORY_FILE, "a")
					FILE.write(f+"\n")
					FILE.close()
					msgqueue.append(f)
		except:
			raise

	return msgqueue


def sendToIrc(msgq):

	try:
		s=socket.socket()
		s.connect((HOST, PORT))
		s.send("NICK %s\r\n" % NICK)
		s.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))

		readbuffer = ""

		while 1:
			# Get the list sockets which are ready to be read through select
			try:
				read_sockets,write_sockets,error_sockets = select.select([s],[],[],1)
			except select.error as e:
				break
			except socket.error as e:
				break

			for sock in read_sockets:
				if sock == s:

					readbuffer=readbuffer+s.recv(1024).decode("UTF-8", errors='replace')
					temp=string.split(readbuffer, "\n")
					readbuffer=temp.pop( )

					for line in temp:
						line=string.rstrip(line)
						line=string.split(line)

						if(line[0]=="PING"):
							s.send("PONG %s\r\n" % line[1])
						elif (line[1]=="001"):
							s.send("JOIN %s\r\n" % CHANNEL)
							for i in msgq:
								s.send("PRIVMSG %s :%s\r\n" % (CHANNEL, i) )
								time.sleep(5)

							s.send("QUIT\r\n")
							s.close()
						else:
							pass

				else:
					print("unknown Socket")

	except:
		traceback.print_exc(file=sys.stdout)


def main():
	# check if HISTORY_FILE exists
	if not os.path.isfile(HISTORY_FILE):
		os.system("cat blubb > %s" HISTORY_FILE)

	msgq = getNewPosts()

	if msgq:
		sendToIrc(msgq)


if __name__ == "__main__":
	main()

