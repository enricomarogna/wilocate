# -*- coding: utf-8 -*-
import sys, httplib, json, math

def addLocation(scan):

  jsons={}
  locnum=0

  for a in scan:

    for r in range(3):

      params = "{ \"version\": \"1.1.0\", \"host\": \"maps.google.com\", \"request_address\": \"true\", \"address_language\":\"en_GB\", \"wifi_towers\": [ { \"mac_address\": " + a.replace(':','-') + ", \"signal_strength\": 8, \"age\": 0 } ] }"
      headers = { "Pragma" : "no-cache", "Cache-control" : "no-cache" }
      conn = httplib.HTTPConnection("www.google.com:80")
      try:
	conn.request("POST", "/loc/json", params, headers)
	response = conn.getresponse()
      except Exception, e:
	print '! Error querying Google about ' + a + ': (%s)' % (e.strerror)
	errnum+=1
	continue

      try:
	j = json.loads(response.read())
      except ValueError, e:
	print '! Error decoding JSON:', e
	continue

      if 'location' in j:
	j = j['location'].copy()
	if 'address' in j:
	  locnum+=1
	  scan[a]['location']=j
	  break

  return locnum

def standard_deviation(sequence):
  med = sum(sequence) / len(sequence)
  variance = sum([(x-med)**2 for x in sequence]) / len(sequence)
  return math.sqrt(variance)

def calcPosition(scan):

  tot_lat=[]
  tot_lng=[]

  for a in scan:
    if 'location' in scan[a]:
      scan[a]['location']['reliable']=0
      if 'latitude' in scan[a]['location'] and 'longitude' in scan[a]['location']:
	tot_lat.append(scan[a]['location']['latitude'])
	tot_lng.append(scan[a]['location']['longitude'])

  if not (tot_lat and tot_lng):
    return []

  sd_lat=standard_deviation(tot_lat)*1.2
  sd_lng=standard_deviation(tot_lng)*1.2
  media_lat = sum(tot_lat) / len(tot_lat)
  media_lng = sum(tot_lng) / len(tot_lng)
  sum_lat=0
  sum_lng=0
  summ_num=0

  for a in scan:

    if not ('location' in scan[a] and 'latitude' in scan[a]['location'] and 'longitude' in scan[a]['location']):
      continue

    if scan[a]['location']['latitude'] >= media_lat-sd_lat and scan[a]['location']['latitude'] <= media_lat+sd_lat and scan[a]['location']['longitude'] >= media_lng-sd_lng and scan[a]['location']['longitude'] <= media_lng+sd_lng:
	sum_lng+=scan[a]['location']['longitude']
	sum_lat+=scan[a]['location']['latitude']
	summ_num+=1
	scan[a]['location']['reliable']=1


    if scan[a]['location']['accuracy'] > 22000:
      print a + ' (' + str(scan[a]['location']['accuracy']) + ') rejected, low accuracy.'
      scan[a]['location']['reliable']=0

    #self.pprint(scan[a]['location'],a)

  latavg=sum_lat/summ_num
  lngavg=sum_lng/summ_num
  if summ_num > 0 and latavg and lngavg:
    return [ summ_num, latavg , lngavg ]

  return []



