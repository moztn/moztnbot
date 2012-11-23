#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys, os.path
import socket
import string
import threading
import time
import json
import random
import time

html_begin = '''<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8"/>
		<title>MozTn IRC log file</title>
		<style type="text/css">
			h3 { text-align: center }
			body { background: #f0f0f0; }
			body .time { color: #007020; display: inline-block; width: 75px; vertical-align: top; }
			body .nick { color: #062873; font-weight: bold;display: inline-block; vertical-align: middle; width: 130px;vertical-align: top; }
			body .msg { display: inline-block; width: 80%; }
		</style>
	</head>
	<body>
'''

class Message:
	message = ''
	def __init__(self, message):
		self.message = message

	def GetCmd():
		return

	def contains(self,word):
		return self.message.find(word) != -1

	def GetMsg(self):
		msg = self.message[self.message.find('PRIVMSG'):]
		msg = msg[msg.find(':')+1:]
		msg = msg[:msg.find('\r')]
		return msg
	
	def GetUname(self):
  		return self.message[self.message.find(':')+1:self.message.find('!')]

	def GetChannel(self):
  		if(self.contains('INVITE')):
			return self.message[self.message.find('#'):self.message.find('\r')]
		elif(self.contains('PRIVMSG')):
			msg = self.message[self.message.find('#'):]
			return msg[:msg.find(':')-1]
	
	def printMsg(self):
		time = getTime()
		uname = self.GetUname()
		msg = self.GetMsg()
		if(len(msg) is not 0):
  			print time+' @'+uname+': '+msg

	def log(self):
		date = getDate()
		channel = self.GetChannel().replace('#','')
		fname = '/var/www/irc/log/'+channel+'-'+date+'.log.html'
		time = getTime()
		uname = self.GetUname()
		msg = self.GetMsg()
		if(not os.path.exists(fname)):
			f = open(fname,'a')
			f.write(html_begin)
			f.write('		<h3>========================%s========================</h3>\n'%date)
			f.close()

		if(len(msg) is not 0):
			f = open(fname,'a')
			content = '		<p>'+'<span class="time">'+time+'</span> <span class="nick"><'+uname+'> : </span> <span class="msg">'+msg+'</span></p>\n'
			f.write(content.encode('utf-8'))
			f.close()
	def pushLog(self):
		try:
			date = getDate()
			channel = self.GetChannel().replace('#','')
			fname = channel+'-'+date+'.log.html'
			return 'http://irc.mozilla-tunisia.org/log/'+fname
		except:	
			return None


#Config
config = {}
configfile = '/opt/moztnbot/config.json'
#Messages :
msgs = {}
msgfile = '/opt/moztnbot/msgs.json'
#Server info :
linkname = ''
# Main Socket 
s=socket.socket()

def init():
	loadConfig()
	loadMsgs()

def Connect():
	s.connect((config['host'], config['port']))
	s.send("NICK %s\r\n" % config['nick'])
	s.send("USER %s %s bla :%s\r\n" % (config['ident'], config['host'], config['realname']))

def loadJson(fname):
	try:
		f = open(fname, 'r')
		fcontent = f.readlines()
		content = json.loads(''.join(fcontent))
		f.close()
	except:
		f = open("/var/log/moztnbot.log", "w")
		f.write('failed to open '+fname)
		f.close()

	return content

def loadConfig():
	global config 
	config = loadJson(configfile)

def loadMsgs():
	global msgs
	msgs = loadJson(msgfile)

def joinChannel(msg):
	channel = Message(msg).GetChannel()
	s.send("JOIN %s\r\n" % channel)

def RandMentionResponse():
	n = random.randrange(1,len(msgs)+1)
	return msgs[str(n)]

def getTime():
	lt = time.localtime()
	localtime = '%s:%s:%s' %(lt.tm_hour, lt.tm_min, lt.tm_sec)
	return localtime

def getDate():
	lt = time.localtime()
	date = '%s-%s-%s' %(lt.tm_year, lt.tm_mon, lt.tm_mday)
	return date

def MakeAction(msg):
	message = Message(msg)
	message.printMsg()
	if(message.contains('PRIVMSG')):
		message.log()
		if(message.contains('hello') or message.contains('Hello')):
			s.send("PRIVMSG %s :Hello %s :) How are you ? How can I help you ?\r\n" % (message.GetChannel(),message.GetUname()))
			return
		if(message.contains(config['nick'])):
			s.send("PRIVMSG %s :%s, %s\r\n" % (message.GetChannel(),message.GetUname(),RandMentionResponse())) 
			s.send("PRIVMSG %s :%s, %s\r\n" % (message.GetChannel(),message.GetUname(),"Type \x02!help\x02 to learn more.")) 
		if(message.contains('!help')):
			s.send("PRIVMSG %s :%s, Sorry, my master is too lasy to implement this :( you can maybe help on https://github.com/rednaks/EspritLibreBot ?\r\n" % (message.GetChannel(),message.GetUname()))
		if(message.contains('!log')):
			url = message.pushLog()
			if(url is not None):
				s.send("PRIVMSG %s :%s you can find the log here : %s\r\n" % (message.GetChannel(),message.GetUname(),url))
			else:
				s.send("PRIVMSG %s :%s Sorry unable to get log please contact my master\r\n" % (message.GetChannel(), message.GetUname()))
	if(message.contains('INVITE')):
		joinChannel(msg)

def getLinkname():
	buff = s.recv(1024)
	global linkname
	linkname = buff[buff.find(':')+1:buff.find(' ')]
    
def main_loop():
 readbuffer = ""
 while 1:
  readbuffer=readbuffer+s.recv(1024)
  temp=string.split(readbuffer, "\n")
  readbuffer=temp.pop()
  print temp
  if(temp[0].find(linkname) is -1):
    try:
      MakeAction(temp[0].decode('utf-8'))
    except:
	try:
      		MakeAction(temp[0].decode('iso8859-15'))
	except:
		try:
			MakeAction(temp[0].decode('iso8859-8-I'))
		except:
			continue
  for line in temp:
      line=string.rstrip(line)
      line=string.split(line)
      if(line[0]=="PING"):
          s.send("PONG %s\r\n" % line[1])
            
if __name__ == '__main__':
	init()
	Connect()
	getLinkname()
	main_loop()
