$(function() {
		$("table").tablesorter({debug: true})
		$("a.append").click(appendData);


	});


function appendData() {

	$("table").trigger('update');
	return false;
}
