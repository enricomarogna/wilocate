# -*- coding: utf-8 -*-

import os, sys, time, re
from subprocess import Popen, PIPE, STDOUT
try: import json
except ImportError: import simplejson as json

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
  pout=None
  pin=None

  def __init__(self,pout,pin,delay=5):

    self.pout=pout
    self.pin=pin

    bin = 'iwlist'
    path = which(bin, ['/sbin/', '/usr/sbin/'])
    if not path:
      print '! Error, no', bin, 'founded in $PATH'

    self.command = path

    try:
      while 1:
	self.getScan()
	time.sleep(delay)
    except (KeyboardInterrupt, SystemExit):
      print '! Quitting scan subprocess.'
      sys.exit(0)

  def getScan(self):

    data = {}
    lastcell=''
    lastauth=''

    cmd = self.command + ' scan'
    pop = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)

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

    if data:
      self.sendData(data)


  def sendData(self,data):
    os.write(self.pout,json.dumps(data) + '\n%%WILOCATE%%\n')

  def encodeAuth(self,string):
    if 'WPA ' in string and string.endswith('1'):
      return 'WPA1'
    if 'WPA2' in string:
      return 'WPA2'