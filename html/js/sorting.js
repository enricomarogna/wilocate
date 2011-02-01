$(function() {
		$("table").tablesorter({debug: true})
		$("a.append").click(appendData);
		
		
	});
	
	var lastStudent = 23;
	var limit = 500;
	
	function appendData() {
		
		var tdTagStart = '<td>';
		var tdTagEnd = '</td>';
		var sex = ['male','female'];
		var major = ['Mathematics','Languages'];
		
		
		for(var i = 0; i < limit; i++) { 
			var rnd = i % 2;
			var row = '<tr>';	
			row += tdTagStart + 'student' + (lastStudent++) + tdTagEnd;
			row += tdTagStart + major[rnd] + tdTagEnd;
			row += tdTagStart + sex[rnd] + tdTagEnd;
			
			row += tdTagStart +  randomNumber() + tdTagEnd;
			row += tdTagStart +  randomNumber() + tdTagEnd;
			row += tdTagStart +  randomNumber() + tdTagEnd;
			row += tdTagStart +  randomNumber() + tdTagEnd;
			
			row += '</tr>';
			
			$("table/tbody:first").append(row);
			
		};
		
		
		$("table").trigger('update');
		return false;
	}
	
	function randomNumber() {
		return Math.floor(Math.random()*101)
	}
