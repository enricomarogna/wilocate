# -*- coding: utf-8 -*-

from threading import Thread, Lock
import SimpleHTTPServer, SocketServer, os, sys, urllib2,json, socket, mimetypes

http_running=False
data = None

class StoppableHttpServer (SocketServer.TCPServer):
    def serve_forever (self):
	global http_running
        while http_running:
            self.handle_request()

class httpRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

  def log_request(self, code='-', size='-'):
    pass

  def do_GET(self):

    global http_running

    try:
      if self.path.endswith(".json"):

	self.send_response(200)
	self.send_header('Content-type','application/x-javascript')
	self.end_headers()

	self.wfile.write(json.dumps(data.getJson()))
	return

      else:
	if self.path=='/':
	  self.path='/wilocate.html'

	self.path = os.curdir + os.sep + 'html' + self.path
	f = open(self.path)
	self.send_response(200)
	self.send_header('Content-type',mimetypes.guess_type(self.path))
	self.end_headers()
	self.wfile.write(f.read())
	f.close()
	return

    except IOError:
      self.send_error(404, 'File not found: %s' % self.path)

    #return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

class httpHandler ( Thread ):

   port = -1

   def __init__(self,jsondata, port=8000):

     global data
     data=jsondata
     self.port=port

     Thread.__init__ ( self )

   def stop(self):

     global http_running
     http_running=False
     while 1:
	try:
	    #print "+ Try to quit web interface on port", self.port
	    urllib2.urlopen('http://localhost:' + str(self.port) + '/', timeout=1)
	except Exception, e:
	    break

   def isRunning(self):
     global http_running
     return http_running

   def run ( self ):
      global http_running

      try:
	httpd = StoppableHttpServer(('127.0.0.1', self.port), httpRequestHandler)
	httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      except Exception, e:
	print '! Web interface and browser opening disabled:', e.strerror
	print '! Port', str(self.port), 'unavailable. Quit this session, wait few seconds and restart wilocate.'

      else:
	http_running=True
	sa = httpd.socket.getsockname()
	print "+ Web interface is running on port ", self.port
	httpd.serve_forever()
	print "! Quitting web interface."