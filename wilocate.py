#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, core.privilege, signal, pprint, re, sys, webbrowser
from core.scanHandler import *
from core.locationHandler import *
from core.dataHandler import *
from core.httpHandler import *

pid=-1
options={ 'web' : True, 'browser' : True, 'port' : 8000}

banner = "+ WiLocate		Version 0.1"

usagemsg = """
Usage:

 ./wilocate.py [options]			Locate current position scanning wifi networks
 ./wilocate.py [options] -s <MAC address>	Locate given MAC address position

Options:

 -h|--help	This help
 -w|--web	Disable web HTTP interface daemon run on start (default: Enabled)
 -b|--browser	Disable web browser run on start (default: Enabled)
 -p|--port

"""

def getUserId():

  import pwd, grp

  user="nobody"
  group="nogroup"

  if os.getenv("SUDO_UID") and os.getenv("SUDO_GID"):
    uid=int(os.getenv("SUDO_UID"))
    gid=int(os.getenv("SUDO_GID"))
  else:
    uid = pwd.getpwnam( user )[2]
    gid = grp.getgrnam( group )[2]

  return uid, gid


def parseOptions():

  import getopt

  try:
      opts, args = getopt.getopt(sys.argv[1:], 'hwbs:p:', ['help','web', 'browser', 'single', 'port'])
  except getopt.error, msg:
      print "! Error:", msg
      print usagemsg
      sys.exit(1)

  ## process options
  for o, a in opts:
      if o in ('-h', '--help'):
	  print usagemsg
	  sys.exit(1)
      elif o in ('-s', '--single'):
	  if not re.match("(?:[0-9A-Z][0-9A-Z](:|-)?){6}", a):
	    print '! Error: \'' + a + '\' is not a MAC address with AA:BB:CC:DD:EE:FF format. Exiting.'
	    sys.exit(1)
	  else:
	    if 'single' not in options:
	      options['single']=[]

	    options['single'] = a.split(',')
      elif o in ('-w', '--web'):
	  options['web']=False
      elif o in ('-b', '--browser'):
	  options['browser']=False
      elif o in ('-p', '--port'):
	  options['port']=int(a)

      else:
	  print usagemsg
	  sys.exit(1)

  if os.getuid() != 0:
    print '+ Warning: triggered scan needs root privileges. Restart with \'sudo -E ' + sys.argv[0] + '\' to get more results.'


def webInterfaceStart(data):

  if options['web']:
    try:
      httpd = httpHandler(data,options['port'])
      httpd.start()
    except Exception, e:
      print '! Error creating new thread.', e
    else:

      r=False
      for i in range(2):
	if httpd.isRunning():
	  r=True
	  break
	time.sleep(1)


      if options['browser'] and r:
	if os.getenv("SUDO_UID") and os.getenv("SUDO_GID") and 'root' in os.getenv("HOME"):
	  print '! Webbrowser autorun disabled. Enable enviroinment variables using \'sudo -E ' + sys.argv[0] + '\''
	else:
	  # webbrowser.open() fails on KDE with kfmclient http://portland.freedesktop.org/wiki/TaskOpenURL
	  webbrowser.get('x-www-browser').open('http://localhost:' + str(options['port']))
	  print '! Webbrowser autorun enabled. Point browser to http://localhost:' + str(options['port'])

      return httpd

def mainSingle():

  if os.geteuid() == 0:
    uid, gid = getUserId()
    core.privilege.drop_privileges_permanently(uid, gid, [1])

  data = dataHandler()

  scan={}
  for a in options['single']:
    scan[a]={}

  print '+', str(len(scan)), 'MAC to localize,',
  nl = addLocation(scan)
  print str(nl), 'locations recovered,',
  ns,nb = data.saveScan(scan)
  print '+' + str(ns) + ' (' + str(nb) + ')'
  data.jsonDump()


def mainScan():

  global pid

  pin, pout = os.pipe()
  try:
    pid = os.fork()
    if pid == 0:
      # child
      scanHandler(pout,pin,5)
      sys.exit(0)

  except OSError, e:
    print 'Fork failed: %d (%s)' % (e.errno, e.strerror)
    sys.exit(1)

  if os.geteuid() == 0:
    uid, gid = getUserId()
    core.privilege.drop_privileges_permanently(uid, gid, [1])

  data = dataHandler()
  httpd = webInterfaceStart(data)

  scantext=''
  buf=''

  try:
    while 1:

      buf=''
      while 1:
	buf+=os.read(pin,1)
	if '\n%%WILOCATE%%\n' in buf:
	  scantext=buf[:buf.find('\n%%WILOCATE%%\n')]
	  break

      try:
	scan = json.loads(scantext)
      except ValueError, e:
	print '! Error decoding JSON: (%s)' % (e.strerror)
	continue


      print '+', str(len(scan)), 'APs,',
      sys.stdout.flush()
      nl = addLocation(scan)
      print str(nl), 'located,',
      sys.stdout.flush()
      pos = calcPosition(scan)
      if not pos:
	print 'no reliable locations found.',
      else:
	print pos[0], 'reliable, current position:', pos[1], pos[2], '.',


      sys.stdout.flush()

      newscanned,newreliable,newbest = data.saveScan(scan, pos[1:])
      print '+ ' + str(newscanned) + '/' + str(newreliable) + '/' + str(newbest)
      sys.stdout.flush()
      data.jsonDump()

      time.sleep(5)

  except (KeyboardInterrupt, SystemExit):
    if httpd:
      httpd.stop()
    raise

if __name__ == "__main__":

  print banner

  try:
    parseOptions()

    if 'single' in options and options['single']:
      mainSingle()
    else:
      mainScan()

  except (KeyboardInterrupt, SystemExit):
    sys.exit(0)
