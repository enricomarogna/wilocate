    google.load("maps", "3",  {other_params:"sensor=false"});

    //risolvere che zooma sempre

    var locs={};
    var wifi={};
    var aplist={};
    var poslist={};
    var lastpos;
    var lastposaddr=false;
    var lasttime=0;

    var map;
    var geoXml;
    var toggleState = 1;

    var zoomed = false;

    var wifiTable;



    function distance(X,Y) {

      var lat_diff=Math.abs(X.lat()-Y.lat());
      var lng_diff=Math.abs(X.lng()-Y.lng());

      return Math.sqrt(Math.pow(lat_diff,2)+Math.pow(lng_diff,2))

    }

  // Strip out malicious tags from wilocate scan json
  function htmlEncode(s)
  {
    var el = document.createElement("div");
    el.innerText = el.textContent = s;
    s = el.innerHTML;
    delete el;
    return s;
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
 	  map.fitBounds (bounds);
	}
    }

    function printDate(t) {
      var date = new Date(b * 1000);
      var dateString = date.getDate() + '/' + date.getMonth() + '/' + date.getYear() + ' ' + date.getHours() + ':' + date.getMinutes() + ':' + date.getSeconds();
      return dateString;
    }

    function parsePosition(b) {
      loc=locs[b];
      var date = printDate(b);

      if('position' in loc) {
	j2=loc['position'];
	lat = j2['latitude'];
	lng = j2['longitude'];

	streetprint='';
	cityprint='';

	if('address' in j2) {

	  if('street' in j2['address'])
	    streetprint +=  j2['address']['street'] + ' ';

	  if('street_number' in j2['address'])
	    streetprint +=  j2['address']['street_number'] + ' ';


	  if ('country' in j2['address'])
	    cityprint += j2['address']['country'] + ' ';

	  if ('country_code' in j2['address'])
	    cityprint +=  '(' + j2['address']['country_code'] + ') ';

	  if('region' in j2['address'])
	    cityprint +=  j2['address']['region'] + ' ';

	  if('postal_code' in j2['address'])
	    cityprint +=  j2['address']['postal_code'] + ' ';

	  if('county' in j2['address'])
	    county = j2['address']['county'] + ' ';

	  if('city' in j2['address'])
	    city = j2['address']['city'] + ' ';

	  if (county != city)
	    cityprint +=  city + ' ' + county + ' ';
	  else if (!city)
	    cityprint +=  county + ' ';
	  else
	    cityprint +=  city + ' ';

	  }


      }

      blockprint = '<tr><td>' +date+ '</td><td>' + streetprint + '</td><td>' + cityprint + '</td><td>' + lat + ',' + lng + '</td></tr>';
      return blockprint

    }

    function parseWifi(m,b) {
	wf=wifi[m];

	var blockprint = '';
	var blocklist = []

	blockprint = '<tr><td>Essid</td><td>' + htmlEncode(wf['ESSID']) + '</td></tr><tr><td>Mac address</td><td>' + m  + '</td></tr>';
	blocklist.push(htmlEncode(wf['ESSID']),m);

	encrstring='';
	if('Encryption' in wf) {
	    for (e in wf['Encryption']) {
	      encrstring += e + ' ( ';
	      for (c in wf['Encryption'][e]) {
		encrstring += wf['Encryption'][e][c] + ' ';
	      }
	      encrstring += ')<br>';
	    }
	}
	blockprint += '<tr><td> Encryption: </td><td>' + encrstring + '</td></tr>';
	blocklist.push(encrstring);

	qualityprint='';
	if('Quality' in wf) {
	  qualityprint+= wf['Quality'];
	}
// 	blockprint+='<tr><td> Quality </td><td>' + qualityprint + '</td></tr>';
	blocklist.push(qualityprint);

	levelprint='';
	if('Level' in wf) {
	  levelprint+= wf['Level'];
	}
	blockprint+='<tr><td> Signal Level </td><td>' + levelprint + ' dBm</td><td> Quality </td><td>' + qualityprint + '</td</tr>';
	blocklist.push(levelprint);

	channelprint='';
	if('Channel' in wf) {
	  channelprint+= wf['Channel'];
	}
	blockprint+='<tr><td> Channel </td><td>' + channelprint + '</td></tr>';
	blocklist.push(channelprint);

	j2=wf['location'];
	streetprint='';
	cityprint='';
	if('address' in j2) {

	  if('street' in j2['address'])
	    streetprint +=  j2['address']['street'] + ' ';

	  if('street_number' in j2['address'])
	    streetprint +=  j2['address']['street_number'] + ' ';


	  if ('country' in j2['address'])
	    cityprint += j2['address']['country'] + ' ';

	  if ('country_code' in j2['address'])
	    cityprint +=  '(' + j2['address']['country_code'] + ') ';

	  if('region' in j2['address'])
	    cityprint +=  j2['address']['region'] + ' ';

	  if('postal_code' in j2['address'])
	    cityprint +=  j2['address']['postal_code'] + ' ';

	  if('county' in j2['address'])
	    county = j2['address']['county'] + ' ';

	  if('city' in j2['address'])
	    city = j2['address']['city'] + ' ';

	  if (county != city)
	    cityprint +=  city + ' ' + county + ' ';
	  else if (!city)
	    cityprint +=  county + ' ';
	  else
	    cityprint +=  city + ' ';

	  }
	  blocklist.push(streetprint,cityprint);
	  blockprint += '<tr><td>Address</td><td>' + streetprint + ' ' + cityprint + '</td></tr>';


	  latprint=''
	  if ('latitude' in j2 && 'longitude' in j2) {
	  latprint+= j2['latitude'] + ',' + j2['longitude'];
	}
	blockprint += '<tr><td>Coordinate</td><td>' + latprint + '</td></tr>';
	blocklist.push(latprint);

	blocklist.push(printDate(b));

	relprint='';
	if (locs[b]['APs'][m] == 1) {
	  relprint += 'Yes';
	}
	else {
	  relprint += 'No';
	}
	blocklist.push(relprint);


	return { p: blockprint, l: blocklist }
    }

    function updateMarker(m) {


	var pos = new google.maps.LatLng(wifi[m]['location']['latitude'],wifi[m]['location']['longitude']);

	var marker = new google.maps.Marker({
	    position: pos,
	    map: map,
	    title:wifi[m]['ESSID'] + '\n' + m,
	    icon:'img/wifi.png'
	});

	aplist[m]=marker;

	google.maps.event.addListener(marker, 'mouseover', function(event) {
	    w = parseWifi(m,b);
	    $("#marker_info_table").html(w.p);
	});


	google.maps.event.addListener(marker, 'dblclick', function(event) {
	  wifiTable.fnFilter(m);
	  window.scrollTo(0, $('#myTable').position().top);
	});

    }


    function update(text) {
	j=eval("(" + text + ")");
	locs=j['locations'];
	wifi=j['wifi'];

	if(locs) {

 	  $('#status').html("Loaded new APs.");

	  for (b in locs) {

	    if(b>lasttime) {

		    lasttime=b

		    if('APs' in locs[b]) {

			for (m in locs[b]['APs']) {

			    if(m in aplist) {

			    }
			    else if(b in locs && 'APs' in locs[b] && m in locs[b]['APs'] && m in wifi && 'location' in wifi[m] && 'latitude' in wifi[m]['location'] && 'longitude' in wifi[m]['location']) {

			      //Togliere il sistema di reliability
// 			      if (locs[b]['APs'][m] == 1) {
				  updateMarker(m);
// 			      }
			      w = parseWifi(m,b);
			      wifiTable.fnAddData(w.l);

			    }


			}
		    }

		    if('position' in locs[b]) {

			  var actual_pos = new google.maps.LatLng(locs[b]['position']['latitude'],locs[b]['position']['longitude']);
			  map.setCenter(actual_pos, 20);

			  if(lastpos == null || (lastpos && distance(actual_pos,lastpos.getPosition()) >= 0.04)) {

			      map.setCenter(actual_pos, 15);
			      var marker = new google.maps.Marker({
				  position: actual_pos,
				  map: map,
				  title:"Current position"
			      });

			    lastpos=marker;
			    tablepos = parsePosition(b);
			    $("#pos_info_table").last().append(tablepos);

			  }
			  else if ((lastpos && distance(actual_pos,lastpos.getPosition()) < 0.04) || ('address' in locs[b]['position'] && lastposaddr==false) ) {
			    lastpos.setPosition(actual_pos);
			    tablepos = parsePosition(b);
			    if('address' in locs[b]['position'])
			      lastposaddr=true;
			    else
			      lastposaddr=false;
			  }

		    }

		    if (!zoomed) {
		      autozoom();
		    }

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
	    toprint = 'Error parsing APs datas from wilocate (null). ' + client.readyState + ' ' + client.status;
	    $('#status').html(toprint);
	  }
	} else if (client.readyState == 4 && client.status != 200) {
	  toprint = 'Connection error while requesting APs data. Please restart wilocate application.';
	  $('#status').html(toprint);
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

      google.maps.event.addListener(map, 'bounds_changed', function() {
	zoomed=true;
      });

      wifiTable = $('#myTable').dataTable({
		"bPaginate": false });

    }


