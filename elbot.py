#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import socket
import string
import threading
import time
import json
import random
import time

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

#Config
config = {}
configfile = 'config.json'
#Messages :
msgs = {}
msgfile = 'msgs.json'
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
	f = open(fname, 'r')
	fcontent = f.readlines()
	content = json.loads(''.join(fcontent))
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

def MakeAction(msg):
	message = Message(msg)
	message.printMsg()
	if(message.contains('PRIVMSG')):
		if(message.contains('hello') or message.contains('Hello')):
			s.send("PRIVMSG %s :Hello %s :) How are you ? How can I help you ?\r\n" % (message.GetChannel(),message.GetUname()))
			return
		if(message.contains(config['nick'])):
			s.send("PRIVMSG %s :%s, %s\r\n" % (message.GetChannel(),message.GetUname(),RandMentionResponse())) 
			s.send("PRIVMSG %s :%s, %s\r\n" % (message.GetChannel(),message.GetUname(),"Type \x02!help\x02 to learn more.")) 
		if(message.contains('!help')):
			s.send("PRIVMSG %s :%s, Sorry, my master is too lasy to implement this :( you can maybe help on https://github.com/rednaks/EspritLibreBot ?\r\n" % (message.GetChannel(),message.GetUname()))
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
#  print temp
  if(temp[0].find(linkname) is -1):
    try:
      MakeAction(temp[0].decode('utf-8'))
    except:
      MakeAction(temp[0].decode('iso8859-1'))
  #print GetMsg(temp[0])
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
