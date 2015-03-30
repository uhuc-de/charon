#!/usr/bin/python2
# -*- coding: utf-8 -*-

import os
import sys
import time
import traceback
import thread
import urllib2 # python2 only
import urllib

import irc.client
import feedparser


### CONFIG ###

# Name of the IRC server
HOST = 'irc.jdqirc.net'

# Port of the IRC server
PORT = 6667

# Channel, to post the new feed entries
CHANNEL = '#test'

# Nick of the Bot
NICK = 'charon'

# Name of the Bot
NAME = 'FeedBot'

# List of feeds to observe
FEED_LIST = [ "https://www.python.org/dev/peps/peps.rss/","http://www.linux.org/originalcontent" ]

# File which saves the last posted entries
ENTRY_FILE = "~/bin/charon/old_feed_entries"

 

### CODE ###


class IRCCat(irc.client.SimpleIRCClient):

	def __init__(self, target, msgs):
		irc.client.SimpleIRCClient.__init__(self)
		self.target = target
		self.msgs = msgs

	def on_welcome(self, connection, event):
		if irc.client.is_channel(self.target):
			connection.join(self.target)
		else:
			self.send_it()

	def on_join(self, connection, event):
		self.send_it()

	def on_disconnect(self, connection, event):
		sys.exit(0)

	def send_it(self):
		time.sleep(2)
		for i in self.msgs:
			self.connection.privmsg(self.target, i)
			time.sleep(1)

		time.sleep(2)
		self.connection.quit("Goodbye and thanks for all the fish!")




def main():
	msgq = load_feeds()

	if msgq:
		c = IRCCat(CHANNEL, msgq)
		try:
			c.connect(HOST, PORT, NICK)
		except irc.client.ServerConnectionError as x:
			print (x)
			sys.exit(2)
		c.start()

def load_feeds():
	FILE = open( ENTRY_FILE, "r" )
	filetext = FILE.read()
	FILE.close()    

	msgqueue = []

	for f in FEED_LIST:
		d = feedparser.parse(f)
		for entry in d.entries:
			ident = entry.link.encode('utf-8')+entry.title.encode('utf-8')
			if ident in filetext:
				pass
			else:
				FILE = open ( ENTRY_FILE, "a")
				FILE.write(ident+"\n")
				FILE.close()

				surl = entry.link.encode('utf-8') 
				msgqueue.append( "%s ( %s )" % (entry.title.encode('utf-8'), surl ) )
				time.sleep(1)
	return msgqueue




if __name__ == "__main__":
	main()

