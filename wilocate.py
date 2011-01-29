#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, core.privilege, signal, pprint, re, sys
from core.scanHandler import *
from core.locationHandler import *
from core.dataHandler import *
from core.httpHandler import *

pid=-1
options={}

banner = "+ WiLocate		Version 0.1"

usagemsg = """
Usage:

 ./wilocate.py				Locate current position scanning wifi networks
 ./wilocate.py -s <MAC address>	Locate given MAC address position
 ./wilocate.py --help|-h		This help

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
      opts, args = getopt.getopt(sys.argv[1:], 'hws:', ['help','web','single'])
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
	  pass

      else:
	  print usagemsg
	  sys.exit(1)

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

  try:
    httpd = httpHandler(data,8000)
    httpd.start()
  except Exception, e:
    print '! Error creating new thread.', e


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

      print '+', str(len(scan)), 'APs founded,',
      nl = addLocation(scan)
      print str(nl), 'locations recovered,',
      pos = calcPosition(scan)
      print 'Current position:', pos[0], pos[1] , '.',
      ns,nb = data.saveScan(scan, pos)
      print '+' + str(ns) + ' (' + str(nb) + ')'
      data.jsonDump()

      time.sleep(5)

  except (KeyboardInterrupt, SystemExit):
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
