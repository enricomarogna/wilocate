# -*- coding: utf-8 -*-
import time, os, pprint, json

def touch(files):
  for f in files:
    fo = open(f,'w')
    if not fo.closed:
      fo.close()

class dataHandler:

  wifi={}
  locations={}

  jsonpath=''

  def __init__(self):
    self.jsonpath=self.genPath()


  def saveFile(self,json):
    self.locations=json['locations'].copy()
    self.wifi=json['wifi'].copy()

  def saveScan(self,scan,pos=None):

    timestamp = int(time.time())

    n=0
    b=0
    r=0
    self.locations[timestamp]={'APs' : {}}

    for s in scan:

      rel=False
      try:
	if(self.wifi[s]['location']['reliable'] > scan[s]['location']['reliable']):
	  rel = True
	  b+=1
      except KeyError:
	pass

      acc=False
      try:
	if(self.wifi[s]['location']['accuracy'] < scan[s]['location']['accuracy']):
	  acc = True
	  b+=1
      except KeyError:
	pass

      if not s in self.wifi.keys() or acc or rel:
	self.wifi[s]=scan[s].copy()
	n+=1

	self.locations[timestamp]['APs'][s]=0
	try:
	  self.locations[timestamp]['APs'][s]=self.wifi[s]['location']['reliable']
	  if not self.wifi[s]['location']['reliable'] == 0:
	    r+=1
	except KeyError:
	  pass

    if pos:
      self.locations[timestamp]['position'] = pos

    return n,r,b

  def jsonDump(self):
    toret = self.getJson()
    f = open(self.jsonpath,'w')
    f.write(json.dumps(toret, indent=4))
    f.close()

  def getJson(self):
    return { 'locations' : self.locations, 'wifi' : self.wifi }

  def genPath(self):

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

    print '+ Log file:', path
    return path

