# -*- coding: utf-8 -*-
import sys, httplib, math

from commons import *
try: import json
except ImportError: import simplejson as json


def addPosition(scan, data, lang, alwaysRelocate=False, retrysingle = 1, retrytotal=8):

    singleparam  = {"version": "1.1.0", "host": "maps.google.com", "request_address": "true", "address_language":lang, "wifi_towers": [] }
    totalparam = singleparam.copy()
    headers = { "Pragma" : "no-cache", "Cache-control" : "no-cache" }

    locnum=0
    alreadylocnum=0
    j={}

    for a in scan:

      quality=5
      level=-60

      if 'Quality' in scan[a]:
	q = scan[a]['Quality']
	if '/70' in q:
	  quality = int(round(int(q.split('/')[0])/7))
      if 'Level' in scan[a]:
	level = scan[a]['Level']

      totalparam['wifi_towers'] += [ { 'mac_address' : a.replace(':','-'), 'signal_strength' : level, 'age' : 0 } ]
      singleparam['wifi_towers'] = [ { 'mac_address' : a.replace(':','-'), 'signal_strength' : level, 'age' : 0 } ]

      if not alwaysRelocate and data.wifi and a in data.wifi and 'location' in data.wifi[a]:
	scan[a]['location']=data.getData('wifi',a)['location']
	alreadylocnum+=1
      else:
	for r in range(retrysingle):
	  j = httpQuery(headers,singleparam)
	  if 'location' in j:
	    j = j['location'].copy()
	    if 'address' in j:
	      locnum+=1
	      scan[a]['location']=j
	      break

    if totalparam:
      position = {}
      for r in range(retrytotal):
	position = httpQuery(headers,totalparam)
	if 'location' in position:
	  if 'address' in position['location']:
	    position = position['location'].copy()
	    print position
	    break
	  elif not position:
	    position = position['location'].copy()

      # Se non mi ha restituito l'address della position con indirizzo, cerco l'address piu vicino e ce lo metto
      if not 'address' in position:
	bestlvl=0
	best={}
	for a in scan:
	  if 'location' in scan[a] and 'address' in scan[a]['location'] and 'Level' in scan[a] and int(scan[a]['Level']) < bestlvl:
	    best=scan[a]['location']['address'].copy()
	    bestlvl=int(scan[a]['Level'])

	if best:
	  position['address']=best.copy()

    return locnum, position


def httpQuery(headers,params):

  j = {}

  conn = httplib.HTTPConnection("www.google.com:80")
  try:
    conn.request("POST", "/loc/json", json.dumps(params), headers)
    response = conn.getresponse()
  except Exception, e:
    log('! Error on HTTP request:', e, '. Are you connected to Internet? Try offline scan with \'-l\'.')
  else:
    jtext = response.read()
    try:
      j = json.loads(jtext)
    except ValueError, e:
      log('! Error parsing JSON:', e, '.')

  return j

def standard_deviation(sequence):
  med = sum(sequence) / len(sequence)
  variance = sum([(x-med)**2 for x in sequence]) / len(sequence)
  return math.sqrt(variance)

def setReliable(scan):

  tot_lat=[]
  tot_lng=[]

  for a in scan:
    if 'location' in scan[a]:
      scan[a]['location']['reliable']=0
      if 'latitude' in scan[a]['location'] and 'longitude' in scan[a]['location']:
	tot_lat.append(scan[a]['location']['latitude'])
	tot_lng.append(scan[a]['location']['longitude'])

  if not (tot_lat and tot_lng):
    return 0

  sd_lat=standard_deviation(tot_lat)*1.5
  sd_lng=standard_deviation(tot_lng)*1.5
  media_lat = sum(tot_lat) / len(tot_lat)
  media_lng = sum(tot_lng) / len(tot_lng)
  summ_num=0

  for a in scan:

    if not ('location' in scan[a] and 'latitude' in scan[a]['location'] and 'longitude' in scan[a]['location']):
      continue

    if scan[a]['location']['latitude'] >= media_lat-sd_lat and scan[a]['location']['latitude'] <= media_lat+sd_lat and scan[a]['location']['longitude'] >= media_lng-sd_lng and scan[a]['location']['longitude'] <= media_lng+sd_lng:
	summ_num+=1
	scan[a]['location']['reliable']=1


    if scan[a]['location']['accuracy'] > 22000:
      log(1,'(' + str(scan[a]['location']['accuracy']) + ' accuracy rejected)')
      scan[a]['location']['reliable']=0

  return summ_num



