# -*- coding: utf-8 -*-
import sys, httplib, json, math


def addPosition(scan, retry = 3):

    singleparam  = {"version": "1.1.0", "host": "maps.google.com", "request_address": "true", "address_language":"en_GB", "wifi_towers": [] }
    totalparam = singleparam.copy()
    headers = { "Pragma" : "no-cache", "Cache-control" : "no-cache" }

    locnum=0
    j={}

    for a in scan:

      quality=5

      if 'Quality' in scan[a]:
	q = scan[a]['Quality']
	if '/70' in q:
	  quality = int(int(q.split('/')[0])/7)
      if 'Level' in scan[a]:
	level = scan[a]['Level']

      totalparam['wifi_towers'] += [ { 'mac_address' : a.replace(':','-'), 'signal_strength' : quality, 'age' : 0 } ]
      singleparam['wifi_towers'] = [ { 'mac_address' : a.replace(':','-'), 'signal_strength' : 10, 'age' : 0 } ]

      for r in range(retry):
	j = httpQuery(headers,singleparam)
	if 'location' in j:
	  j = j['location'].copy()
	  if 'address' in j:
	    locnum+=1
	    scan[a]['location']=j
	    break

    position = {}
    for r in range(retry):
      position = httpQuery(headers,totalparam)
      if 'location' in position:
	position = position['location'].copy()
	break

    return locnum, position


def httpQuery(headers,params):

  j = {}

  conn = httplib.HTTPConnection("www.google.com:80")
  try:
    conn.request("POST", "/loc/json", json.dumps(params), headers)
    response = conn.getresponse()
  except Exception, e:
    print '! Error querying Google Maps about ' + a + ': (%s)' % (e.strerror)

  jtext = response.read()
  try:
    j = json.loads(jtext)
  except ValueError, e:
    print '! Error parsing Google Maps JSON data:', e

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
      print a + ' (' + str(scan[a]['location']['accuracy']) + ') rejected, low accuracy.'
      scan[a]['location']['reliable']=0

  return summ_num



