{% load static %}

<!DOCTYPE HTML>
<html lang="pt-br">
	<head>
		<meta charset="UTF-8">

		<title>User Home</title>
		
		<!-- jquery - link cdn -->
		<script src="https://code.jquery.com/jquery-2.2.4.min.js"></script>

		<!-- bootstrap - link cdn -->
		<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css">
	
		<!--<link rel="stylesheet" type="text/css" href="{% static 'uspdarwin_app/css/wd-style.css' %}">-->
		<!--<link rel="stylesheet" type="text/css" href="{% static 'uspdarwin_app/style.css' %}">-->
	
	</head>


	<body style="background-color: #EEE;">

		{% include 'dv_std.php' %}

		<script type="text/javascript">
			var years = {{ years|safe }};
			var months = {{ months|safe }};
			var ufs = {{ ufs|safe }};
			var dbf_fname_list = {{ dbf_fname_list|safe }};
			var dbf_fname_idx = {{ dbf_fname_idx|safe }};
			var dbf_qtt_mtx = {{ dbf_qtt_mtx|safe }};
			var dbf_size_mtx = {{ dbf_size_mtx|safe }};
			var dbf_mo_mtx = {{ dbf_mo_mtx|safe }};
			var pkl_fname_list = {{ pkl_fname_list|safe }};
			var pkl_fname_idx = {{ pkl_fname_idx|safe }};
			var pkl_qtt_mtx = {{ pkl_qtt_mtx|safe }};
			var pkl_size_mtx = {{ pkl_size_mtx|safe }};
			var pkl_indiv_mtx = {{ pkl_indiv_mtx|safe }};
		</script>

    	<div style="background-color:#FFF;border:solid 2px;width:1280px;margin:auto;">
    		<div style="font-weight:bold;font-size:16px;text-align:center;">FILE CHECKING</div>
    		<div class="row" id="dbf" style="border:solid 1px;width:1260px;margin:auto;">
		    	<div class="col-md-2" id="file_list" style="border:solid 1px;height:260px;overflow-y:scroll;font-size:10px;">
		    		<div style="font-weight:bold;text-align:center;">DBF FILES</div>
		    		<div id="dbf_file_total" style=""></div>
		    		<div id='dbf_folders'></div>
		    	</div>
		    	<div class="col-md-10" id="dbf_file_data" style="border:solid 1px;height:260px;font-size:10px;">
		    		<div>
		    			<div style="font-size:12px;font-weight:bold;">DBF Categories</div>
		    			<div id="dbf_categories_data" style="border:solid 1px;font-size:12px;"></div>
		    		</div>
		    		<div>
		    			<div class="col-md-4">
			    			<div style="font-size:12px;font-weight:bold;">DBF Files Year Nr</div>
				    		<div id="dbf_qtt_matrix_data" style="border:solid 1px;height:180px;overflow-y:scroll;"></div>
			    		</div>
		    			<div class="col-md-4">
			    			<div style="font-size:12px;font-weight:bold;">DBF Files Size</div>
				    		<div id="dbf_size_matrix_data" style="border:solid 1px;height:180px;overflow-y:scroll;"></div>
			    		</div>
		    			<div class="col-md-4">
			    			<div style="font-size:12px;font-weight:bold;">DBF Files Month Size</div>
				    		<div id="dbf_mo_matrix_data" style="border:solid 1px;height:180px;overflow-y:scroll;"></div>
			    		</div>
		    		</div>
		    	</div>
    		</div>
    		<div class="row" id="pkl" style="border:solid 1px;width:1260px;margin:auto;">
		    	<div class="col-md-2" id="file_list" style="border:solid 1px;height:260px;overflow-y:scroll;font-size:10px;">
		    		<div style="font-weight:bold;text-align:center;">PKL FILES</div>
		    		<div id="pkl_file_total" style=""></div>
		    		<div id='pkl_folders'></div>
		    	</div>
		    	<div class="col-md-10" id="pkl_file_data" style="border:solid 1px;height:260px;font-size:10px;">
		    		<div>
		    			<div style="font-size:12px;font-weight:bold;">PKL Categories</div>
		    			<div id="pkl_categories_data" style="border:solid 1px;font-size:12px;"></div>
		    		</div>
		    		<div>
		    			<div class="col-md-4">
			    			<div style="font-size:12px;font-weight:bold;">PKL Files Nr</div>
				    		<div id="pkl_qtt_matrix_data" style="border:solid 1px;height:180px;overflow-y:scroll;"></div>
			    		</div>
		    			<div class="col-md-4">
			    			<div style="font-size:12px;font-weight:bold;">PKL Files Size</div>
				    		<div id="pkl_size_matrix_data" style="border:solid 1px;height:180px;overflow-y:scroll;"></div>
			    		</div>
		    			<div class="col-md-4">
			    			<div style="font-size:12px;font-weight:bold;">PKL Files Register Individuos</div>
				    		<div id="pkl_reg_matrix_data" style="border:solid 1px;height:180px;overflow-y:scroll;"></div>
			    		</div>
		    		</div>
		    	</div>
    		</div>
	    </div>

	    <script type="text/javascript">
			putFileDescription('dbf_file_total',dbf_fname_list,dbf_fname_idx,'dbf_folders','dbf_categories_data');
	    	putTable(years,ufs,dbf_qtt_mtx,'dbf_qtt_matrix_data');
	    	putTable(years,ufs,dbf_size_mtx,'dbf_size_matrix_data');
	    	putTable(months,ufs,dbf_mo_mtx,'dbf_mo_matrix_data');
			putFileDescription('pkl_file_total',pkl_fname_list,pkl_fname_idx,'pkl_folders','pkl_categories_data');
	    	putTable(years,ufs,pkl_qtt_mtx,'pkl_qtt_matrix_data');
	    	putTable(years,ufs,pkl_size_mtx,'pkl_size_matrix_data');
	    	putTable(years,ufs,pkl_indiv_mtx,'pkl_reg_matrix_data');

	    	function putFileDescription(total_id,fname_list,fname_idx,folders_id,categories_id) {
		    	var total = document.getElementById(total_id);
		    	total.innerHTML = 'Total='+fname_list.length;
		    	var folders = document.getElementById(folders_id);
		    	var fname_str = '';
		    	for (var i=0; i<fname_idx.length; i++) {
		    		fname_str = fname_str+fname_list[fname_idx[i]]+'<br>';
		    	}
		    	folders.innerHTML = fname_str;
		    	var categories = document.getElementById(categories_id);
		    	categories.innerHTML = years.length+' years: '+years+'<br>'+ufs.length+' UFs: '+ufs;
	    	}

	    	function putTable(h_header_list,v_header_list,content_mtx,parent_id) {
		    	var parent = document.getElementById(parent_id);
		    	var tab = document.createElement('table');
		    	parent.appendChild(tab);
		    	tab.style = 'margin:auto;border:solid 2px;';
		    	var tr = document.createElement('tr');
		    	tab.appendChild(tr);
		    	var td = document.createElement('td');
	    		tr.appendChild(td);
	    		td.style = 'border:solid 1px;text-align:center;font-weight:bold;background-color:#DDD;';
	    		td.innerHTML = 'UF|Ano';
		    	for (var i=0; i<h_header_list.length; i++) {
			    	var td = document.createElement('td');
		    		tr.appendChild(td);
		    		td.style = 'border:solid 1px;text-align:center;font-weight:bold;background-color:#DDD;padding:2px;';
		    		td.innerHTML = h_header_list[i];
		    	}
		    	for (var i=0; i<content_mtx.length; i++) {
		    		var row = content_mtx[i];
		    		var row_mean = 0;
			    	for (var ii=0; ii<row.length; ii++) {
			    		row_mean = row_mean+row[ii];
			    	}
			    	row_mean = row_mean/row.length;
		    		var row_stdv = 0;
			    	for (var ii=0; ii<row.length; ii++) {
			    		row_stdv = row_stdv+(row[ii]-row_mean)**2;
			    	}
			    	row_stdv = Math.sqrt(row_stdv/row.length);
			    	if (row_stdv==0) { row_stdv = 1; }
			    	var tr = document.createElement('tr');
			    	tab.appendChild(tr);
			    	var td = document.createElement('td');
		    		tr.appendChild(td);
		    		td.style = 'font-weight:bold;text-align:center;border:solid 1px;background-color:#DDD;padding:2px;';
		    		td.innerHTML = v_header_list[i];
			    	for (var j=0; j<row.length; j++) {
			    		var val = row[j].toFixed(1);
			    		var xc = Math.min(Math.max(0,val-row_mean+2*row_stdv),4*row_stdv);
			    		var c = getDegradeColor(4*row_stdv-xc,4*row_stdv);
				    	var td = document.createElement('td');
			    		tr.appendChild(td);
			    		td.style = 'text-align:center;border:solid 1px;background-color:'+c;
			    		td.innerHTML = val;
			    	}
		    	}
		    }

			function getDegradeColor(r,l) {
				var bot = 0x60;
				var top = 0x100-1;
				var f = (1.0*r)/l;
				var b = 0.0;
				var g = 0.0;
				var r = 0.0;
				if (f<=0.5) { r=0.0; g=2*f; b=2*(0.5-f); }
				else { r=2*(f-0.5); g=2*(1.0-f); b=0.0; }
				var ri = Math.floor( r*(top-bot)+bot );
				var gi = Math.floor( g*(top-bot)+bot );
				var bi = Math.floor( b*(top-bot)+bot );
				var v = ri*0x10000 + gi*0x100 + bi*0x1;
				var c = '#'+v.toString(16).padStart(6,'0');
				return c;
			}
	    </script>

		<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script>
	
	</body>
</html>