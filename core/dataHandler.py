# -*- coding: utf-8 -*-
import time, os, pprint
from threading import Lock
try: import json
except ImportError: import simplejson as json
lock=Lock()



class dataHandler:

  wifi={}
  locations={}

  jsonpath=''

  def __init__(self,jsonpath):
    self.jsonpath=jsonpath

  def saveFile(self,json):
    self.locations=json['locations'].copy()
    self.wifi=json['wifi'].copy()

  def saveScan(self,scan,pos,timestamp):

    n=0
    b=0
    r=0
    lock.acquire()
    self.locations[timestamp]={'APs' : {}}

    for s in scan:

      best_reliability=False
      try:
	if(self.wifi[s]['location']['reliable'] > scan[s]['location']['reliable']):
	  best_reliability = True
	  b+=1
      except KeyError:
	pass

      best_accuracy=False
      try:
	if(self.wifi[s]['location']['accuracy'] < scan[s]['location']['accuracy']):
	  best_accuracy = True
	  b+=1
      except KeyError:
	pass

      best_location=False
      try:
	if not ('latitude' in self.wifi[s]['location'] and 'longitude' in self.wifi[s]['location']) and ('latitude' in scan[s]['location'] and 'longitude' in scan[s]['location']):
	  best_location=True
	  b+=1
      except KeyError:
	pass

      if not s in self.wifi.keys() or best_accuracy or best_reliability or best_location:
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

    lock.release()
    return n,r,b

  def jsonDump(self):
    f = open(self.jsonpath,'w')
    f.write(self.getJson())
    f.close()

  def getJson(self):
    lock.acquire()
    jsonobj = { 'locations' : self.locations, 'wifi' : self.wifi }.copy()
    jsondump = json.dumps(jsonobj, indent=4)
    lock.release()
    return jsondump

  def getData(self,f,v):
    if f=='wifi':
      return self.wifi[v]
    if f=='locations':
      return self.locations[v]



