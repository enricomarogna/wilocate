# -*- coding: utf-8 -*-

import os, sys, time, re
from subprocess import Popen, PIPE, STDOUT
from threading import Thread, Lock
from commons import *

try: import json
except ImportError: import simplejson as json

try:
  import wx
except ImportError:
  log('! Install wxPython library version 2.6 with \'sudo apt-get install python-wxgtk2.6\'')
  sys.exit(1)


from locationHandler import *
from dataHandler import *

class Scan(Thread):
  
    def __init__(self,parent,sudo=False):
      self.parent = parent
      self.sudo = sudo
      Thread.__init__(self)
    def run(self):
      """ Run wifi scan.
      
      """
      self.parent.getScan()
      self.parent.locateScan()
      self.parent.datahdl.jsonDump()
      self.parent.changeState()


class loadScanHandler:

  parent = None
  datahdl=None

  scanwifi = {}
  scanloc = {}
  sortedloctimestamps = []
  
  scanisrunning = False
  
  lastscan = { }
  lastscaninfo = { }
  
  lastfilepath = ''
  
  def __init__(self,parent,options,data):

    self.datahdl=data
    self.options=options
    self.parent=parent
    
    
  def loadFile(self,filepath):
    
    try:
      fl = open(filepath,'r')
      filescan = json.loads(fl.read())
    except Exception, e:
      log('! Error opening', filepath, 'file:', e)
      return False
    else:
      fl.close()
      self.scanwifi = filescan['wifi']
      self.scanloc = filescan['locations']
      self.sortedloctimestamps = [ k for k in sorted(self.scanloc.keys())]
      
      
  def launchScan(self):
    
      scanthread = Scan(self)
      scanthread.start()

  def changeState(self):
    
    if self.lastscaninfo:
      self.parent.ScanState(self.lastscaninfo)
      
  def getScan(self):
    
    if self.sortedloctimestamps:
      timestamp = self.sortedloctimestamps.pop(0)
      if self.scanloc[timestamp].has_key('APs'):
	self.lastscan = {}
	for ap in self.scanloc[timestamp]['APs']:
	  if self.scanwifi.has_key(ap):
	    self.lastscan[ap]=self.scanwifi[ap].copy()
    

  def locateScan(self):

      tm = time.time()

      if self.lastscan:
	pos = { }
	lonpos = 0
	latpos = 0
	nl = 0
	rel = 0
	if not self.options['NotLocate']:
	  nl, pos = addPosition(self.lastscan,self.datahdl,self.options['lang'],self.options['always-loc'])
	  
	  if not 'latitude' in pos and 'longitude' in pos:
	    return
	  
	  rel = setReliable(self.lastscan)
	  lonpos=pos['longitude']
	  latpos=pos['latitude']

	newscanned,newreliable,newbest = self.datahdl.saveScan(self.lastscan, pos, tm)

	self.lastscaninfo = {
	  'timestamp' : time.strftime("%H:%M:%S", time.localtime(tm)),
	  'seen' : str(len(self.lastscan)),
	  'located' : str(nl),
	  'newscanned' : str(newscanned),
	  'newreliable' : str(newreliable),
	  'newbest' : str(newbest),
	  'latitude' : str(lonpos),
	  'longitude' : str(latpos),
	  'sudo' : str(False)
	}

  msgbox = None
