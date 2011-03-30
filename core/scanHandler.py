# -*- coding: utf-8 -*-

import os, sys, time, re
from subprocess import Popen, PIPE, STDOUT

try: import json
except ImportError: import simplejson as json

try:
  import wx
except ImportError:
  print '! Install wxPython library version 2.6 with \'sudo apt-get install python-wxgtk2.6\''
  sys.exit(1)


from locationHandler import *
from dataHandler import *

def which(program, moredirs = []):
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)

    dirs = os.environ["PATH"].split(os.pathsep) + moredirs

    if fpath:
	if is_exe(program):
            return program
    else:
        for path in dirs:
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


class scanHandler:

  command=''
  command_su=''

  lastscan={}

  datahdl=None

  def __init__(self,options,data):


    bin_iwlist = 'iwlist'
    path_iwlist = which(bin_iwlist, ['/sbin/', '/usr/sbin/'])
    if not path_iwlist:
      print '! Error, no', bin_iwlist, 'founded in $PATH'
    else:
      self.command=path_iwlist

    bin_su = 'sudo'
    path_su = which(bin_su, ['/sbin/', '/usr/sbin/'])
    if path_su:
      self.command_su=path_su
    else:
      print '! No sudo program founded, triggered scan is disabled.'

    #bin_kdesu = 'kdesudo'
    #path_su = which(bin_kdesu, ['/sbin/', '/usr/sbin/'])
    #if not path_su:
      #self.command_su=path_su
      #print '! No gtksu or kdesudo founded, triggered scan is disabled.'
    #else:
      #self.command_su=path_su

    self.datahdl=data
    self.options=options

  def wifiScan(self,sudo=False):
    self.getScan(sudo)
    newscaninfo = self.locateScan()
    self.datahdl.jsonDump()
    return newscaninfo

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
	  rel = setReliable(self.lastscan)
	  lonpos=pos['longitude']
	  latpos=pos['latitude']

	newscanned,newreliable,newbest = self.datahdl.saveScan(self.lastscan, pos, tm)

	return {
	  'timestamp' : time.strftime("%H:%M:%S", time.localtime(tm)),
	  'seen' : str(len(self.lastscan)),
	  'located' : str(nl),
	  'newscanned' : str(newscanned),
	  'newreliable' : str(newreliable),
	  'newbest' : str(newbest),
	  'latitude' : str(lonpos),
	  'longitude' : str(latpos)
	}

  msgbox = None

  def getScan(self, sudo=False):

    data = {}
    lastcell=''
    lastauth=''

    dlg=None

    if sudo or self.options['password']:
      if self.command_su and self.options['password']:
	cmd = [ 'echo ' + self.options['password'] + ' | ' + self.command_su + ' -S ' + self.command + ' scan' ]
	pop = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
      else:
	msg = 'Error executing ' + self.command_su + ' with password ' + '*'*len(self.options['password']) + '.'
	self.dlg = wx.MessageDialog(None, msg, "Error", wx.OK)
	self.dlg.ShowModal()
	self.dlg.Destroy()
	return

    else:
      cmd = [ self.command + ' scan' ]
      pop = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)

    ret = pop.wait()
    if ret != 0:
	msg = 'Something gone wrong with scan execution.'
	if sudo and self.options['password']:
	  msg += ' Check your \'sudo\' root password or disable triggered scans.'
	  self.options['password']=''

	self.dlg = wx.MessageDialog(None, msg, "Error", wx.OK)
	self.dlg.ShowModal()
	self.dlg.Destroy()
	return

    try:
      for l in pop.stdout.read().split('\n'):

	p = l.strip()
	spa = [x.strip() for x in p.split(' ')]
	sp = [x.strip(':') for x in spa]

	# If Cell i create new key with mac address
	if len(sp) == 5 and sp[0] == 'Cell' and sp[3] == 'Address' and re.match("(?:[0-9A-Z][0-9A-Z](:|-)?){6}", sp[4]):
	  lastcell=sp[4]
	  data[lastcell]={}
	  lastauth=''

	elif sp[0].startswith('Channel') or sp[0].startswith('Frequency') or sp[0].startswith('Mode') or sp[0].startswith('ESSID'):
	  splitted = sp[0].split(':') + sp[1:]
	  data[lastcell][splitted[0]]=splitted[1].strip('"') # For ESSID
	  #append
	  if sp[0].startswith('Frequency') and len(splitted)==5 and splitted[3]=='(Channel':
	    data[lastcell][splitted[0]]+=splitted[2]
	    data[lastcell]['Channel']=splitted[4][0]
	  if sp[0].startswith('ESSID') and not data[lastcell][splitted[0]]:
	    data[lastcell][splitted[0]] = '<hidden>'

	elif sp[0].startswith('Quality'):
	  if '=' in sp[0] and len(sp[0].split('='))==2:
	    quality = sp[0].split('=')[1]
	    data[lastcell]['Quality'] = quality
	  if len(sp)>=3 and sp[2] == 'Signal' and '=' in sp[3] and len(sp[3].split('='))==2:
	    level = sp[3].split('=')[1]
	    data[lastcell]['Level'] = level
	elif sp[0] == 'Encryption' and sp[1].startswith('key'):
	  if sp[1].split(':')[1] == 'on':
	    if 'Encryption' not in data[lastcell]:
	      data[lastcell]['Encryption']= { 'WEP' : {} }
	      lastauth='WEP'
	  if sp[1].split(':')[1] == 'off':
	    if 'Encryption' not in data[lastcell]:
	      data[lastcell]['Encryption']= { 'open' : {} }
	      lastauth='open'

	elif sp[0] == 'IE' and sp[1] != 'Unknown':
	  lastauth=self.encodeAuth(' '.join(sp[1:]))
	  if 'Encryption' not in data[lastcell]:
	    data[lastcell]['Encryption']= {}
	  if lastauth and 'WEP' in data[lastcell]['Encryption']:
	    del data[lastcell]['Encryption']['WEP']
	  if lastauth and 'open' in data[lastcell]['Encryption']:
	    del data[lastcell]['Encryption']['open']

	  data[lastcell]['Encryption'][lastauth]={}
	elif sp[0] == 'Group' or sp[0] == 'Pairwise' or sp[0] == 'Authentication':
	  # The separator is '' (void array slot), because i stripped out :
	  value=''
	  if '' in sp:
	    where = sp.index('')
	    value=' '.join(sp[where:]).strip()

	  if 'Encryption' not in data[lastcell]:
	    data[lastcell]['Encryption']= {}
	  data[lastcell]['Encryption'][lastauth][sp[0]]=value

    except Exception, e:
      print '! Error parsing scan command output:', e

    self.lastscan=data.copy()

  def encodeAuth(self,string):
    if 'WPA ' in string and string.endswith('1'):
      return 'WPA1'
    if 'WPA2' in string:
      return 'WPA2'