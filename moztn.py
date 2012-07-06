#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import socket
import string
import threading
import time


#HOST=sys.argv[1]
PORT=6667
#NICK=sys.argv[2]
HOST='irc.mozilla.org'
NICK='moztn'
IDENT="Mozilla Tunisia Bot"
REALNAME="moztnBot"
#readbuffer=""
#CHANNEL = '#esprit-libre'

cmd_list=['quit','names','join']

s=socket.socket( )
s.connect((HOST, PORT))
s.send("NICK %s\r\n" % NICK)
s.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))
#s.send("JOIN %s\r\n" % CHANNEL)



def joinChannel(msg):
  channel = GetChannel(msg)
  s.send("JOIN %s\r\n" % channel)

def MakeAction(msg):
  if(msg.find('PRIVMSG') is not -1):
     return 1
  elif(msg.find('INVITE') is not -1):
     return 2
  else:
     return 0

def GetMsg(msg):
  msg = msg[msg.find('PRIVMSG'):]
  msg = msg[msg.find(':')+1:]
  msg = msg[:msg.find('\r')]
  return msg

def GetUname(msg):
  return msg[msg.find(':')+1:msg.find('!')]

def GetChannel(msg):
  if(msg.find('INVITE')>-1):
    return msg[msg.find('#'):msg.find('\r')]
  elif(msg.find('PRIVMSG')>-1):
    msg = msg[msg.find('#'):]
    return msg[:msg.find(':')-1]
  
def printMsg(msg):
  if(msg.find(' hi') >-1 or msg.find('hello') >-1 or msg.find('Hello') > -1):
    s.send("PRIVMSG %s :Hello %s :) How are you ? How can I help you ?\r\n" % (GetChannel(msg),GetUname(msg)))
  print '@'+GetUname(msg)+': '+GetMsg(msg)

    
def run():
 readbuffer = ""
 while 1:
  readbuffer=readbuffer+s.recv(1024)
  temp=string.split(readbuffer, "\n")
  readbuffer=temp.pop( )
  print temp
  if(MakeAction(temp[0]) is 1):
      printMsg(temp[0])
  elif(MakeAction(temp[0]) is 2):
      joinChannel(temp[0])

    #print GetMsg(temp[0])
  for line in temp:
      line=string.rstrip(line)
      line=string.split(line)
      if(line[0]=="PING"):
          s.send("PONG %s\r\n" % line[1])
            

run()
