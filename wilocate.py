#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, core.privilege, signal, pprint, re, sys, webbrowser
from core.scanHandler import *
from core.locationHandler import *
from core.dataHandler import *
from core.httpHandler import *

pid=-1
options={ 'web' : True, 'browser' : True, 'port' : 8000, 'lang' : '', 'localization' : True }

banner = """"+ WiLocate		Version 0.1"""

httpd = None

usagemsg = """
Usage:

 ./wilocate.py [options]			Locate current position scanning wifi networks

Options:

 -h|--help	  	This help
 -w|--web-disable	Disable web HTTP interface daemon run on start (default: Enabled)
 -b|--browser-disable	Disable web browser run on start (default: Enabled)
 -p|--port <#>		Open web HTTP interface to port number (default: 8000)
 -f|--file <path>	Load scan datas from path in JSON format
 -l|--loc-disable 	Disable on-line localization, useful to collect wifi data off-line. (Default: Enabled)


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

  lang = os.getenv('LANG')
  if lang:
    if '.' in lang:
      lang=lang.split('.')[0]
    options['lang']=lang

  try:
      opts, args = getopt.getopt(sys.argv[1:], 'lhwbs:p:f:', ['help','web-disable', 'browser-disable', 'loc-disable', 'single', 'port', 'file'])
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
      elif o in ('-w', '--web-disable'):
	  options['web']=False
      elif o in ('-b', '--browser-disable'):
	  options['browser']=False
      elif o in ('-p', '--port'):
	  options['port']=int(a)
      elif o in ('-f', '--file'):
	  options['file']=a
      elif o in ('-l', '--loc-disable'):
	  options['localization']=False

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

  global httpd

  if os.geteuid() == 0:
    uid, gid = getUserId()
    core.privilege.drop_privileges_permanently(uid, gid, [1])


  data = dataHandler()
  httpd = webInterfaceStart(data)

  try:

    if 'file' in options and options['file']:
      fl = open(options['file'],'r')
      print '+ Scan disabled, reading from', options['file'], '.'
      filescan = json.loads(fl.read())
      fl.close()
      scanwifi = filescan['wifi']
      scanloc = filescan['locations']


      if options['localization']:
	sys.stdout.flush()

	for timestamp in scanloc:
	  if scanloc[timestamp].has_key('APs'):
	    currentwifiscan = {}
	    for ap in scanloc[timestamp]['APs']:
	      if scanwifi.has_key(ap):
		currentwifiscan[ap]=scanwifi[ap].copy()

	    print '+', str(len(currentwifiscan)), 'APs,',
	    sys.stdout.flush()
	    localization(currentwifiscan,data)
	    #nl, pos = addPosition(currentwifiscan,options['lang'])
	    #rel = setReliable(currentwifiscan)

	    #if 'latitude' in pos and 'longitude' in pos:
	      #print str(nl) + ' located, ' + str(rel) + ' reliable, ' + timestamp + ' position: ' + str(pos['latitude']) + ',' + str(pos['longitude']) + ' .',
	    #sys.stdout.flush()

	    #newscanned,newreliable,newbest = data.localizeScan(currentwifiscan, pos)
	    #print ' ' + str(newscanned) + '/' + str(newreliable) + '/' + str(newbest)

      print '! File read entirely.'


    else:
      scan={}
      for a in options['single']:
	scan[a]={}

      print '+', str(len(scan)), 'MAC to localize,',
      nl, pos = addPosition(scan,options['lang'])
      print str(nl), 'locations recovered,',

      newscanned,newreliable,newbest = localize.localizeScan(scan)
      print '+ ' + str(newscanned) + '/' + str(newreliable) + '/' + str(newbest)

    data.jsonDump()

    while 1:
      time.sleep(1)

  except (KeyboardInterrupt, SystemExit, Exception):
    if httpd:
      httpd.stop()
    raise

def localization(scan,data):

  nl, pos = addPosition(scan,options['lang'])
  rel = setReliable(scan)
  if 'latitude' in pos and 'longitude' in pos:
    print str(nl) + ' located, ' + str(rel) + ' reliable, current position: ' + str(pos['latitude']) + ',' + str(pos['longitude']) + ' .',
  sys.stdout.flush()

  newscanned,newreliable,newbest = data.localizeScan(scan, pos)
  print ' ' + str(newscanned) + '/' + str(newreliable) + '/' + str(newbest)


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
      if options['localization']:
	localization(scan,data)
      
      #if options['localization']:
	#nl, pos = addPosition(scan,options['lang'])
	#rel = setReliable(scan)
	#if 'latitude' in pos and 'longitude' in pos:
	  #print str(nl) + ' located, ' + str(rel) + ' reliable, current position: ' + str(pos['latitude']) + ',' + str(pos['longitude']) + ' .',
	#sys.stdout.flush()

	#newscanned,newreliable,newbest = data.localizeScan(scan, pos)
	#print ' ' + str(newscanned) + '/' + str(newreliable) + '/' + str(newbest)

      else:
	newscanned,newreliable,newbest = data.saveScan(scan)
	print 'detected.'

      sys.stdout.flush()
      data.jsonDump()

      time.sleep(5)

  except (KeyboardInterrupt, SystemExit, Exception):
    if httpd:
      httpd.stop()
    raise

if __name__ == "__main__":

  print banner

  try:
    parseOptions()

    if ('single' in options and options['single']) or ('file' in options and options['file']):
      mainSingle()
    else:
      mainScan()

  except (KeyboardInterrupt, SystemExit):
    if httpd:
      httpd.stop()
