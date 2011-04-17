# -*- coding: utf-8 -*-

from threading import Thread, Lock
import SimpleHTTPServer, SocketServer, os, sys, urllib2, socket, mimetypes, time
from commons import log

try: import json
except ImportError: import simplejson as json
try:
  import wx
  #import wx.lib.newevent
except ImportError:
  log('! Install wxPython library version 2.6 with \'sudo apt-get install python-wxgtk2.6\'')
  sys.exit(1)


#WebStateUpdateEvent, WEB_STATE_EVENT = wx.lib.newevent.NewEvent()

data = None


class ExitableSocketServer(SocketServer.TCPServer):
  allow_reuse_address = True

class httpRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

  def log_request(self, code='-', size='-'):
    pass

  def log_error(self, *args):
    pass

  def do_GET(self):


    global http_running
    global data


    try:
      if self.path.endswith(".json"):

	self.send_response(200)
	self.send_header('Content-type','application/x-javascript')
	self.end_headers()

	self.wfile.write(data.getJson())

      elif self.path.endswith("control?quit"):
	self.changeState(False, 'Web interface stopped', True)

      else:
	if self.path=='/':
	  path='wilocate.html'
	else:
	  path = self.path
	  
	self.path = os.curdir + os.sep + 'html' + os.sep + path

	return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)


    except IOError:
      log('Error ' + 404 + ' File not found: %s' % self.path)


class httpHandler ( Thread ):

   port = -1
   
   running = False
   forced_quit = False
   
   httpd = None

   def __init__(self, parentApp, jsondata, port=8000):

     global data
     data=jsondata
     self.port=port
     self.parent=parentApp
     Thread.__init__ ( self )

   def stop(self):
     self.__changeState(False, 'Web interface stopped')
     self.forced_quit=True
     if self.httpd:
	self.httpd.shutdown()

     #for n in range(3):
	#try:
	    #urllib2.urlopen('http://localhost:' + str(self.port) + '/', timeout=1)
	#except Exception, e:
	  #pass
	#else:
	  #break

   def __changeState(self, state, msg, displayerror = False):
      self.running = state
      #wx.PostEvent(self.parent, WebStateUpdateEvent())
      #wx.PostEvent(target, SomeNewEvent(attr1=foo, attr2=bar))
      self.parent.WebState(state,msg,displayerror)

   def isRunning(self):
     return self.running

   def run ( self ):

      while True:
	
	try:
	  self.httpd = ExitableSocketServer(('127.0.0.1', self.port), httpRequestHandler)
	except Exception, e:
	  log('!', e)
	  self.__changeState(False, 'Port ' + str(self.port) + ' unavailable,\nplease shutdown any other process that keep port open.\nRetry in 10s.',True)
	  time.sleep(10)
	else:
	  break

	if self.forced_quit:
	  break

      if self.httpd:
	self.__changeState(True, "Running on port " + str(self.port))
	self.httpd.serve_forever()

      self.__changeState(False, 'Web interface stopped')
