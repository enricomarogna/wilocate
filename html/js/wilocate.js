    google.load("maps", "3",  {other_params:"sensor=false"});

    var locs={};
    var wifi={};
    var mappedaps={};
    var unmappedaps={};
    var poslist={};
    var lastpos;
    var lastposaddr=false;
    var seentime=[];


    var userquit = false;
    var map;
    var geoXml;
    var toggleState = 1;

    var zoomed=true; //To avoid first autozoom

    var wifiTable;

	$.fn.dataTableExt.oApi.fnGetHiddenTrNodes = function ( oSettings )
	{
		/* Note the use of a DataTables 'private' function thought the 'oApi' object */
		var anNodes = this.oApi._fnGetTrNodes( oSettings );
		var anDisplay = $('tbody tr', oSettings.nTable);

		/* Remove nodes which are being displayed */
		for ( var i=0 ; i<anDisplay.length ; i++ )
		{
			var iIndex = jQuery.inArray( anDisplay[i], anNodes );
			if ( iIndex != -1 )
			{
				anNodes.splice( iIndex, 1 );
			}
		}

		/* Fire back the array to the caller */
		return anNodes;
	}




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
	for (a in mappedaps) {
	  if(!bounds.contains(mappedaps[a].getPosition())) {
	    bounds.extend (mappedaps[a].getPosition());
	    toZoom=true;

	  }
	}


	if(toZoom) {
 	  map.fitBounds (bounds);
	}
    }

    function printDate(t) {
      var date = new Date(b * 1000);
      var dateString = /*date.getDate() + '/' + date.getMonth() + '/' + date.getFullYear() + ' ' + */date.getHours() + ':' + date.getMinutes() + ':' + date.getSeconds();
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


	streetprint='';
	cityprint='';
	latprint=''
	if ('location' in wf) {

	    j2=wf['location'];
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
	      blockprint += '<tr><td>Address</td><td>' + streetprint + ' ' + cityprint + '</td></tr>';


	      if ('latitude' in j2 && 'longitude' in j2) {
	      latprint+= j2['latitude'] + ',' + j2['longitude'];
	    }
	    blockprint += '<tr><td>Coordinate</td><td>' + latprint + '</td></tr>';

	}


	blocklist.push(streetprint,cityprint);
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

	var iconpath='img/default_unselect.png';
	if('Encryption' in wifi[m]) {
	    for (e in wifi[m]['Encryption']) {
	      if (e == 'open' || e == 'WEP') {
		iconpath='img/unsecure_unselect.png';
		break;
	      }
	      if (e == 'WPA1' || e == 'WPA2') {
		iconpath='img/secure_unselect.png';
		break;
	      }

	    }
	}

	var marker = new google.maps.Marker({
	    position: pos,
	    map: map,
	    title:wifi[m]['ESSID'] + '\n' + m,
	    icon:iconpath
	});

	mappedaps[m]=marker;

	google.maps.event.addListener(marker, 'mouseover', function(event) {
	    w = parseWifi(m,b);
	    $("#marker_info_text").html('');
 	    $("#marker_info_table").find('tbody').html('');
	    $("#marker_info_table").find('tbody').append(w.p);
	});


	google.maps.event.addListener(marker, 'dblclick', function(event) {
	  wifiTable.fnFilter(m);
// 	  window.scrollTo(0, $('#myTable').position().top);
// 	  if(m in wifi && 'location' in wifi[m] && 'latitude' in wifi[m]['location'] && 'longitude' in wifi[m]['location']) {
// 	    var p = new google.maps.LatLng(wifi[m]['location']['latitude'],wifi[m]['location']['longitude']);
// 	    break;
// 	  }
// 	  map.setCenter(p);
	});

    }


    function update(text) {
	j=eval("(" + text + ")");
	locs=j['locations'];
	wifi=j['wifi'];

	if(locs) {

	  for (b in locs) {

	    if(!(b in seentime)) {

		    seentime.push(b);
		    aps=0;
		    newaps=0;
		    newlocaps=0;

		    if('APs' in locs[b]) {

			for (m in locs[b]['APs']) {

			    aps+=1;

			    if(!((m in unmappedaps) || (m in mappedaps)) && b in locs && 'APs' in locs[b] && m in locs[b]['APs']) {

			      if(m in wifi && 'location' in wifi[m] && 'latitude' in wifi[m]['location'] && 'longitude' in wifi[m]['location']) {
				newlocaps+=1;
				updateMarker(m);
			      }
			      else {
				unmappedaps[m]=0;
			      }
			      w = parseWifi(m,b);
			      wifiTable.fnAddData(w.l);
			      newaps+=1;

			    }
			}


			if (newaps>0) {
			  if (newlocaps)
			    $("#map_canvas").css({background: 'white'});
			  $("#status").html("[" + printDate(b) + "] " + aps + " WiFi spots detected, " + newaps + " new, " + newlocaps  + " located.");
			}
		    }

		    if('position' in locs[b] && 'latitude' in locs[b]['position'] && 'longitude' in locs[b]['position']) {

			  var actual_pos = new google.maps.LatLng(locs[b]['position']['latitude'],locs[b]['position']['longitude']);


			  if(lastpos == null || (lastpos && distance(actual_pos,lastpos.getPosition()) >= 0.04)) {

			      map.setCenter(actual_pos, 18);
			      var marker = new google.maps.Marker({
				  position: actual_pos,
				  map: map,
				  title:"Current position"
			      });

			      marker.setZIndex(0);

			      lastpos=marker;
			      tablepos = parsePosition(b);
			      $("#pos_info_table").last().append(tablepos);

			  }
			  else if ((lastpos && distance(actual_pos,lastpos.getPosition()) < 0.04) || ('address' in locs[b]['position'] && lastposaddr==false) ) {

// 			    map.setCenter(actual_pos,18);
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
	  if (!userquit) {
	    toprint = 'Connection error while requesting APs data. Please restart wilocate application.';
	    $('#status').html(toprint);
	  }
	}
      }

      client.onreadystatechange = handler;
      client.open("GET", "http://localhost:8000/wilocate.json", true);
      client.send();

    }


    function showMarker() {

	  if(!wifiTable)
	    return

	  var nHidden = wifiTable.fnGetHiddenTrNodes();

	  var hiddenlist = [];

	  for( var i=0; i<nHidden.length; i++) {
		hiddenlist.push($(nHidden[i]).find('td:eq(1)').text());
	  }

	  for (mac in mappedaps) {


		if (hiddenlist.indexOf(mac)!=-1) {
		  if (mappedaps[mac].getVisible()==true) {
		    mappedaps[mac].setVisible(false);
		  }
		}
		else {
		  if (mappedaps[mac].getVisible()==false) {
		    mappedaps[mac].setVisible(true);
		  }
		}

	  }

    }


    function initialize() {

      request()

      var myLatlng = new google.maps.LatLng(45.0665322,7.6509678);
      var myOptions = {
	zoom: 18,
	mapTypeId: google.maps.MapTypeId.HYBRID
      };


      map = new google.maps.Map(document.getElementById("map_canvas"),myOptions);

      google.maps.event.addListener(map, 'move', function() {
	zoomed=true;
      });

      wifiTable = $('#myTable').dataTable({"bPaginate": false });


      $('#center_button').click(function() {
 	map.setCenter(lastpos.getPosition());
      });

      $('#quit_button').click(function() {
	  var client = new XMLHttpRequest();
          client.open("GET", "http://localhost:8000/control?quit", true);
	  client.send();
	  userquit=true;
	  toprint = 'Wilocate is now stopped, and no more wifi are loaded.';
	  $('#status').html(toprint);
      });

      $('#clear_button').click(function() {
 	  wifiTable.fnFilter('');

      });

      $("#myTable tbody").delegate("tr", "click", function() {
	  var m = $("td:eq(1)", this).text();
	  wifiTable.fnFilter(m);
	  if(m in wifi && 'location' in wifi[m] && 'latitude' in wifi[m]['location'] && 'longitude' in wifi[m]['location']) {
	    var p = new google.maps.LatLng(wifi[m]['location']['latitude'],wifi[m]['location']['longitude']);
	  }
	  map.setCenter(p);
      });

    }

