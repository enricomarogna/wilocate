# -*- coding: utf-8 -*-

from threading import Thread, Lock
import SimpleHTTPServer, SocketServer, os, sys, urllib2, socket, mimetypes, time
try: import json
except ImportError: import simplejson as json

http_running = (False, 'Not Running', False)


data = None

class StoppableHttpServer (SocketServer.TCPServer):
    def serve_forever (self):
	global http_running
        while http_running[0] and not http_running[2]:
            self.handle_request()

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
	http_running=(False, 'Web interface stopped', True)

      else:
	if self.path=='/':
	  self.path='/wilocate.html'
	self.path = os.curdir + os.sep + 'html' + self.path


	return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)


    except IOError:
      self.send_error(404, 'File not found: %s' % self.path)


class httpHandler ( Thread ):

   port = -1

   def __init__(self, jsondata, port=8000):

     global data
     data=jsondata
     self.port=port

     Thread.__init__ ( self )

   def stop(self):

     global http_running

     http_running=(False, 'Web interface stopped',True)

     for n in range(3):
	try:
	    urllib2.urlopen('http://localhost:' + str(self.port) + '/', timeout=1)
	except Exception, e:
	  pass
	else:
	  break


   def isRunning(self):
     global http_running
     return http_running

   def run ( self ):
      global http_running

      httpd=None

      while True:
	if not http_running[0]:
	  try:
	    httpd = StoppableHttpServer(('127.0.0.1', self.port), httpRequestHandler)
	    httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	  except Exception, e:
	    print '!', e
	    http_running=(False, 'Port ' + str(self.port) + ' busy,\nretrying in 5s',False)
	    time.sleep(5)
	  else:
	    #print 'Chiudo il ciclo del thread, normalmente'
	    break

	if http_running[2]:

	  #print 'Chiudo il ciclo del thread, forced'
	  break


      if httpd:
	http_running=(True, "Running on port " + str(self.port),False)
	sa = httpd.socket.getsockname()
	httpd.serve_forever()
	httpd.socket.close()

      http_running=(False, 'Web interface stopped', True)
      #print 'Esco dal thread, credo'
