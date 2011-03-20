# -*- coding: utf-8 -*-
import os, time, json

default_options={ 'ScanOnStart' : True, 'WebOnStart' : True, 'BrowserOnWebStart' : True, 'port' : 8000, 'lang' : '', 'NotLocate': False, 'always-loc': False, 'sleep':(5,60,10) }
options = {}

def touch(files):
  for f in files:
    fo = open(f,'w')
    if not fo.closed:
      fo.close()

def genLogPath():

  tm = time.strftime("%d-%b-%Y", time.gmtime())

  dirr = 'log-' + tm
  if not os.path.exists(dirr):
    os.makedirs(dirr)

  i=0
  path = dirr + os.sep + str(i) + '.log'
  while os.path.exists(path):
    i+=1
    path = dirr + os.sep + str(i) + '.log'

  touch([ path ])

  return path

def saveOptions():
    f = open(os.getenv("HOME") + os.sep + '.wilocate.conf','w')

    f.write(json.dumps(options, indent=4))
    f.close()

def setDefaultOptions():

  global options

  options = default_options.copy()

  lang = os.getenv('LANG')
  if lang:
    if '.' in lang:
      lang=lang.split('.')[0]
    options['lang']=lang

def loadOptions():

  global options

  if not os.path.exists(os.getenv("HOME") + os.sep + '.wilocate.conf'):
    setDefaultOptions()
    print 'No config founded, loaded default options.'
    saveOptions()

  else:
    f = open(os.getenv("HOME") + os.sep + '.wilocate.conf','r')
    options = json.loads(f.read())

  return options
