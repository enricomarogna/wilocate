    google.load("maps", "3",  {other_params:"sensor=false"});

    //risolvere che zooma sempre

    var json={};
    var json2={};
    var aplist={};
    var poslist={};
    var lastpos;
    var lasttime=0;

    var map;
    var geoXml;
    var toggleState = 1;

    function distance(X,Y) {

      var lat_diff=X.lat()-Y.lat();
      var lng_diff=X.lng()-Y.lng();

      return Math.sqrt(Math.pow(lat_diff,2)+Math.pow(lng_diff,2))

    }

    function autozoom() {

	var toZoom=false;
	var bounds = new google.maps.LatLngBounds ();
	for (a in aplist) {
	  if(!bounds.contains(aplist[a].getPosition())) {
	    bounds.extend (aplist[a].getPosition());
	    toZoom=true;

	  }
	}


	if(toZoom) {
// 	  document.getElementById('marker_info').innerHTML = "ZOOOMO"
 	  map.fitBounds (bounds);
	}
    }

    function htmlify(m,b) {

	j=json[b]['APs'][m]
	j2=json2[m]

	var blockprint = '<h3>' + j2['ESSID'] + '</h3>' + m + '<br/>';


	if('Encryption' in j2) {
	    for (e in j2['Encryption']) {
	      blockprint += e + ' ';
	      for (c in j2['Encryption'][e]) {
		blockprint += j2['Encryption'][e][c] + ' ';
		}
	    }
	}

	blockprint += '<br/>';

	j2=j2['location']

	if('address' in j2) {

	  if ('country' in j2['address'])
	    blockprint += j2['address']['country'] + ' ';

	  if ('country_code' in j2['address'])
	    blockprint +=  '(' + j2['address']['country_code'] + ') ';

	  if('region' in j2['address'])
	    blockprint +=  j2['address']['region'] + ' ';

	  if('postal_code' in j2['address'])
	    blockprint +=  j2['address']['postal_code'] + ' ';

	  if('county' in j2['address'])
	    county = j2['address']['county'] + ' ';

	  if('city' in j2['address'])
	    city = j2['address']['city'] + ' ';

	  if (county != city)
	    blockprint +=  city + ' ' + county + ' ';
	  else if (!city)
	    blockprint +=  county + ' ';
	  else
	    blockprint +=  city + ' ';

	  if('street' in j2['address'])
	    blockprint +=  j2['address']['street'] + ' ';

	  if('street_number' in j2['address'])
	    blockprint +=  j2['address']['street_number'] + ' ';

	  }
	blockprint += '(' + j2['accuracy'] + ') ';
	return blockprint
    }

    function updateMarker(m) {


	var pos = new google.maps.LatLng(json2[m]['location']['latitude'],json2[m]['location']['longitude']);

	var marker = new google.maps.Marker({
	    position: pos,
	    map: map,
	    title:json2[m]['ESSID'] + '\n' + m,
	    icon:'ap.png'
	});

	aplist[m]=marker;

	google.maps.event.addListener(marker, 'mouseover', function(event) {
// 	    alert(marker.getTitle());
	    document.getElementById('marker_info').innerHTML = htmlify(m,b);
	});



    }

    function update(text) {
	j=eval("(" + text + ")");
	json=j['locations'];
	json2=j['wifi'];

	if(json) {
	  document.getElementById('marker_info').innerHTML = "APs datas loaded.";

	  for (b in json) {

	    if(b>lasttime) {

	      lasttime=b

	      if('APs' in json[b]) {

		  for (m in json[b]['APs']) {

		      if(m in aplist) {

		      }
		      else if(b in json && 'APs' in json[b] && m in json[b]['APs'] && json[b]['APs'][m]==1) {
			    updateMarker(m);

		      }


		  }
	      }

	      if('position' in json[b]) {

		    var actual_pos = new google.maps.LatLng(json[b]['position'][0],json[b]['position'][1]);
		    map.setCenter(actual_pos, 20);

		    if(!lastpos) {

			map.setCenter(actual_pos, 15);
			var marker = new google.maps.Marker({
			    position: actual_pos,
			    map: map,
			    title:"Actual position"
			});

		      lastpos=marker;

		    }
		    else {
			dist = distance(actual_pos,lastpos.getPosition());
			// Tra 1.113 km e 111.3 m
			if(dist > 0.001) {

			  lastpos.setPosition(actual_pos);

			}
		    }

	      }

	      autozoom();

	    }

 	  }
	}

    }

    function request() {

      setTimeout("request()",5000);

      var client = new XMLHttpRequest();
      function handler() {

	if(client.readyState == 4 && client.status == 200) {
	  if(client.responseText != null && client.responseText != "") {
	    update(client.responseText);

	  }
	  else {
	    toprint = 'Error getting json (null) ' + client.readyState + ' ' + client.status;
	    document.getElementById('marker_info').innerHTML = toprint;
	  }
	} else if (client.readyState == 4 && client.status != 200) {
	  toprint = 'Error getting json (!=200)';
	  document.getElementById('marker_info').innerHTML = toprint;
	}
      }

      client.onreadystatechange = handler;
      client.open("GET", "http://localhost:8000/wilocate.json", true);
      client.send();

    }


    function initialize() {

      request()

      var myLatlng = new google.maps.LatLng(-34.397, 150.644);
      var myOptions = {
	zoom: 16,
// 	center: myLatlng,
	mapTypeId: google.maps.MapTypeId.HYBRID
      };
      map = new google.maps.Map(document.getElementById("map_canvas"),myOptions);

    }


