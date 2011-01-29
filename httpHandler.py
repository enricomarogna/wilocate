# -*- coding: utf-8 -*-

from threading import Thread, Lock
import SimpleHTTPServer, SocketServer, os, sys, urllib,json, socket

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

      elif self.path=='/' or self.path.endswith(".html"):
	f = open(os.curdir + os.sep + 'html' + os.sep + 'wilocate.html')
	self.send_response(200)
	self.send_header('Content-type','text/html')
	self.end_headers()
	self.wfile.write(f.read())
	f.close()
	return

      elif self.path.endswith(".png"):
	f = open(os.curdir + os.sep + 'html' + self.path)

	self.send_response(200)
	self.send_header('Content-type','image/png')
	self.end_headers()
	self.wfile.write(f.read())
	f.close()
	return

    except IOError:
      self.send_error(404, 'File not found: %s' % self.path)

    #return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

class httpHandler ( Thread ):

   port = -1

   def __init__(self,jsondata, port):
     global data
     data=jsondata
     self.port=port

     Thread.__init__ ( self )

   def stop(self):
     global http_running
     http_running=False
     try:
	urllib.urlopen('http://localhost:' + port + '/')
     except Exception, e:
	pass

     print "+ Quitting web interface."

   def run ( self ):
      global http_running

      try:
	httpd = StoppableHttpServer(('127.0.0.1', self.port), httpRequestHandler)
	httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      except Exception, e:
	print '! HTTP web interface disabled:', e
	print '! Port', str(self.port), 'seems used. Stop this session, wait few seconds and restart.'

      else:
	http_running=True
	sa = httpd.socket.getsockname()
	print "+ Running web interface. Point browser to http://" + str(sa[0]) + ":" + str(sa[1])
	httpd.serve_forever()
