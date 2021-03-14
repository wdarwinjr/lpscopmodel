// ***** GLOBAL VARIABLES *****//
var multiproc = false;
sessionStorage.clear();
var static_dir = '';
var proj_name = '';
var proj_list = [];
var stage_block_dic = {'acquisition':1,'slicing':2,'descriptive':2,'margin':3,'copula':4};
/*var mcmc_params = ['model_str','comps_nr','rounds_nr','samples_nr','tune'];
var mcmc_options = [['Beta','Weibull','Normal'],['auto','1','2','3','4','5','6','7','8','9','10'],
				['1','2','3','5','10','20'],['200','500','1000','5000','10000'],
				['100','500','1000','2000']];*/
var mcmc_params = ['model_str','comps_nr','samples_nr','tune'];
var mcmc_options = [['Beta','Weibull','Normal'],['1','2','3','4','5','6','7','8','9','10'],
				['200','500','1000','5000','10000'],['100','500','1000','2000']];
var fitting_div_list = ['histogram_result','fitting_result','conv_result'];
var margin_box_mtx = [[{'id':'params','num_title':'Modeling Parameters','cat_title':'Parameters'},
					  {'id':'conv','num_title':'Modeling Convergence','cat_title':'Convergence'}],
					 [{'id':'histogram','num_title':'Histogram','cat_title':'Histogram'},
					  {'id':'fitting','num_title':'Margin Fitting','cat_title':'Margin Fitting'}]];
var copula_box_mtx = [[{'id':'s1','type':'surface','title':'Copula 2D Projection - Surface'},{'id':'s2','type':'surface','title':'Copula 2D Projection - Surface'},{'id':'s3','type':'surface','title':'Copula 2D Projection - Surface'}],
					  [{'id':'l1','type':'levels','title':'Copula 2D Projection - Levels'},{'id':'l2','type':'levels','title':'Copula 2D Projection - Levels'},{'id':'l3','type':'levels','title':'Copula 2D Projection - Levels'}]];
var dataset_list = ['DATASUS','toy_up','toy_indep','toy_down','generic']; //'ForestFire',
var datasus_sel_dic = {
	'datatype':{'title':'Data Type','class':'col-md-2'},
	'type':{'title':'Info Type','class':'col-md-2'},
	'year':{'title':'Year','class':'col-md-3'},
	'uf':{'title':'UF','class':'col-md-3'},
	'month':{'title':'Month','class':'col-md-2'},
};
var session = {'stage':0};
var value_list = [];
var exec_window = null;



//******** FUNCTIONS **********//
function initPage() {
	static_dir = static_dir_init; //proj_dir+'uspdarwinapp/static/';
	proj_name = proj_name_init;
	proj_list = proj_list_init;
	loadBanner();
	loadProjBar();
	loadProjChoice();
	loadModelingDiagram();
}

//*****************************//
//******** MAIN PAGE **********//
//*****************************//
function loadBanner() {
	var banner = document.getElementById('banner');
	var fig = document.createElement('figure');
	banner.appendChild(fig);
	fig.style.margin = '1px 5px';
	fig.style.border = 'solid 1px';
	fig.classList.add('row');
	var img = document.createElement('img');
	fig.appendChild(img);
	img.src = static_dir+'images/lps_banner.png';
	img.alt = 'banner.png';
	img.style.width = '1286px';
	img.style.height = '80px';
	var head_div = document.createElement('div');
	banner.appendChild(head_div);
	head_div.style.width = '1290px';
	head_div.style.margin = 'auto';
	head_div.style.padding = '1px';
	head_div.classList.add('row');
	var title_head = document.createElement('div');
	head_div.appendChild(title_head);
	title_head.classList.add('col-md-10');
	title_head.style = 'background-color:#777;color:white;text-align:center;font-weight:bold;text-decoration-color:white;font-size:18px;height:25px;';
	title_head.innerHTML = 'DATA MODELING USING COPULA';
	var proj_head = document.createElement('div');
	head_div.appendChild(proj_head);
	proj_head.id = 'proj_head';
	proj_head.classList.add('col-md-2');
	proj_head.style = 'background-color:#EEE; text-align:center; font-weight:bold; border:solid 1px; font-size:12px; height:25px;';
	proj_head.innerHTML = '--no project yet--';
}
function loadProjBar() {
	var container = document.getElementById('container');
	var proj_div = document.createElement('div');
	container.appendChild(proj_div);
	proj_div.id = 'proj_div';
	proj_div.classList.add('row','frame_row');
		var proj_lbl = document.createElement('label');
		proj_div.appendChild(proj_lbl);
		proj_lbl.classList.add('col-md-1');//,'frame_row_label');
		proj_lbl.style = 'font-size:14px;padding:7px;';
		proj_lbl.innerHTML = 'Project:';
		var proj_sel = document.createElement('select');
		proj_div.appendChild(proj_sel);
		proj_sel.id = 'proj_action';
		proj_sel.style = 'font-size:12px;padding:0px;';
		proj_sel.classList.add('col-md-1');//,'frame_row_sel');
		proj_sel.onchange = function() { loadProjChoice(); };
			var proj_opt_new = document.createElement('option');
			proj_sel.appendChild(proj_opt_new);
			proj_opt_new.value = 'new';
			proj_opt_new.text = 'New Project';
			proj_opt_new.selected = true;
			var proj_opt_load = document.createElement('option');
			proj_sel.appendChild(proj_opt_load);
			proj_opt_load.value = 'load';
			proj_opt_load.text = 'Load Project';
		var proj_choice = document.createElement('div');
		proj_div.appendChild(proj_choice);
		proj_choice.id = 'proj_choice';
		proj_choice.classList.add('col-md-2');//,'frame_row_div');
			var proj = document.createElement("input");
			proj_choice.appendChild(proj);
			proj.id = "project";
			proj.type = "text";
		var proj_btn = document.createElement('button');
		proj_div.appendChild(proj_btn);
		proj_btn.type = 'button';
		proj_btn.classList.add('col-md-1');//,'frame_row_button');
		proj_btn.innerHTML = 'OK';
		proj_btn.onclick = function() { setProj(); };
		var proj_space_div = document.createElement('div');
		proj_div.appendChild(proj_space_div);
		proj_space_div.classList.add('col-md-5');
		var proj_session_div = document.createElement('div');
		proj_div.appendChild(proj_session_div);
		proj_session_div.classList.add('col-md-2');
			var clearDB_btn = document.createElement('button');
			proj_session_div.appendChild(clearDB_btn);
			clearDB_btn.type = 'button';
			clearDB_btn.id = 'clearDB_btn';
			clearDB_btn.style = 'font-size:10px;padding:0px;';
			clearDB_btn.innerHTML = 'Clear Projects';
			clearDB_btn.onclick = function() { doClearProjects(); };
			var download_btn = document.createElement('button');
			proj_session_div.appendChild(download_btn);
			download_btn.type = 'button';
			download_btn.id = 'download_btn';
			download_btn.style = 'font-size:10px;padding:0px;';
			download_btn.innerHTML = 'Download results';
			download_btn.onclick = function() { doDownloadResults(); };
}
function loadProjChoice() {
	var proj_choice = document.getElementById("proj_choice");
	proj_choice.innerHTML = "";
	var sel = document.getElementById("proj_action");
	var proj_action = sel.options[sel.selectedIndex].value;
	if (proj_action=="new") {
		var proj = document.createElement("input");
		proj.id = "project";
		proj.type = "text";
	}
	if (proj_action=="load") {
		var proj = document.createElement("select");
		proj.id = "project";
		for (var i=0; i<proj_list.length; i++) {
			var opt = document.createElement("option");
			opt.text = proj_list[i];
			opt.value = proj_list[i];
			proj.appendChild(opt);
		}
	}
	proj_choice.appendChild(proj);
}
function setProj() {
	var sel = document.getElementById("proj_action");
	var proj_action = sel.options[sel.selectedIndex].value;
	var proj = document.getElementById("project");
	var proj_name = "";
	if (proj_action=="new") {
		if (proj.value=='--no project yet--') { proj_name = 'noname'; }
		else { proj_name = proj.value; }
		proj.value = "";
	}
	if (proj_action=="load") {
		proj_name = proj.options[proj.selectedIndex].text;
		sessionStorage.setItem("proj_name",proj_name);
	}
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		method : 'POST',
		url: 'defineProj',
		data: {'proj_name':proj_name},
		success: function(data) {
			proj_list = data['proj_list'];
			session = JSON.parse(data['j_session']);
			$("#proj_head").text(session['proj_name']);
			document.getElementById('proj_head').style.color = 'blue';
			alert("Project successfully loaded and saved!");
			loadModelingDiagram();
		}
	});
}
function doClearProjects() {
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		method : 'POST',
		url: 'doClearProjects',
		data: {},
		success: function(data) {
			proj_name = data['proj_name'];
			proj_list = data['proj_list'];
			loadProjBar();
			loadProjChoice();
			loadModelingDiagram();
			alert('Projects cleared!');
		}
	});
	return true;
}
function doDownloadResults() {
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		method: 'GET',
		url: 'doDownloadResults',
		data: {},
        xhrFields: {
            responseType: 'blob'
        },
		success: function(data) {
			//document.getElementById('download').click();
			alert('Results downloaded!');
            var a = document.createElement('a');
            var url = window.URL.createObjectURL(data);
            a.href = url;
            a.download = session['proj_name']+'_session.pkl';
            document.body.append(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
		}
	});
	return true;
}
function saveSession() {
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		method : 'POST',
		url: 'saveProjectSession',
		data: {},
		success: function(data) {
			document.getElementById('proj_head').style.color = 'blue';
			alert("Session successfully saved for this project!");
		}
	});
}

//************************************//
//******** MODELING DIAGRAM **********//
//************************************//
function loadModelingDiagram() {
	var container = document.getElementById('container');
	container.innerHTML = '';
	loadProjBar();
	var modeling_diagram = document.createElement('div');
	container.appendChild(modeling_diagram);
	modeling_diagram.id = 'modeling_diagram';
	modeling_diagram.classList.add('row');
	var modeling_row = document.createElement('div');
	modeling_diagram.appendChild(modeling_row);
	modeling_row.id = 'modeling_row';

	box_list = [{'id':'phenom_db','class':['col-md-1', 'db_div']},
				{'id':'data_acq','class':['col-md-1', 'block_div']},
				{'id':'data_slice','class':['col-md-1', 'block_div']},
				{'id':'selected_db','class':['col-md-1', 'db_div']},
				{'id':'desc_stats','class':['col-md-1', 'block_div']},
				{'id':'norm_db','class':['col-md-1', 'db_div']},
				{'id':'modeling_box','class':['col-md-4', 'block_div']},
				{'id':'copula_graphic','class':['col-md-2', 'block_div']}];
	for (var i=0; i<box_list.length; i++) {
		var dic = box_list[i];
		var div = document.createElement('div');
		modeling_row.appendChild(div);
		div.id = dic['id'];
		for (var j=0; j<dic['class'].length; j++) {
			div.classList.add(dic['class'][j]);
		}
	}

	var phenom_db = document.getElementById('phenom_db');
	var phenom_db_lbl = document.createElement('label');
	phenom_db.appendChild(phenom_db_lbl);
	phenom_db_lbl.id = 'dataset_label';
	phenom_db_lbl.classList.add('db_label');
	phenom_db_lbl.for = 'dataset_img';
	phenom_db_lbl.innerHTML = 'Phenomenon\nData';
	var img_list = [{'class':'img_db','id':'dataset_img','src':'db.jpeg','oc':''},
					{'class':'arrow','id':'arrow_1','src':'arrow_right.png','oc':''}];
	for (var i=0; i<img_list.length; i++) {
		putImg(img_list[i],phenom_db);
	}

	var data_acq = document.getElementById('data_acq');
	var data_acq_div = document.createElement('div');
	data_acq.appendChild(data_acq_div);
	data_acq_div.classList.add('block_div_div');
	data_acq_div.id = 'dataset_acquisition';
	data_acq_div.innerHTML = 'Data<br>Acquisition';
	data_acq_div.onclick = function() { doModelingAction('dataset_selection'); };
	putImg({'class':'process_img','id':'acquisition','src':'process.png','oc':'doModelingAction("dataset_selection")'},data_acq);
	var data_acq_filter_div = document.createElement('div');
	data_acq.appendChild(data_acq_filter_div);
	data_acq_filter_div.classList.add('example');
	data_acq_filter_div.id = 'example_filter';
	var p_list = [	{'class':'example_title','text':'FILTER'},
					{'class':'p_filter','text':'Period: "2008","2009"'},
					{'class':'p_filter','text':'Region: "MG","SP"'},
					{'class':'p_filter','text':'Subject:'},
					{'class':'p_filter','text':'CID: "S720",...,"S729"'},
					{'class':'p_filter','text':'Age: 60'}];
	for (var i=0; i<p_list.length; i++) {
		p_dic = p_list[i];
		putP(p_dic,data_acq_filter_div);
	}
	var data_acq_feature_div = document.createElement('div');
	data_acq.appendChild(data_acq_feature_div);
	data_acq_feature_div.classList.add('example');
	data_acq_feature_div.id = 'example_feature';
	var p_list = [	{'class':'example_title','text':'FEATURES'},
					{'class':'p_filter','text':'Feature_1'},
					{'class':'p_filter','text':'Feature_2'},
					{'class':'p_filter','text':'Feature_3'},
					{'class':'p_filter','text':'Feature_4'},
					{'class':'p_filter','text':'Feature_5'}];
	for (var i=0; i<p_list.length; i++) {
		p_dic = p_list[i];
		putP(p_dic,data_acq_feature_div);
	}

	var data_slice = document.getElementById('data_slice');
	putImg({'class':'arrow','id':'arrow_slice','src':'arrow_right.png','oc':''},data_slice);
	putImg({'class':'process_img','id':'slicing','src':'process.png','oc':'doModelingAction("dataset_slicing")'},data_slice);
	var data_slice_div = document.createElement('div');
	data_slice.appendChild(data_slice_div);
	data_slice_div.classList.add('block_div_div');
	data_slice_div.id = 'dataset_slicing';
	data_slice_div.innerHTML = 'Data Filter<br>and Slicing';
	data_slice_div.onclick = function() { doModelingAction('dataset_slicing'); };

	var selected_db = document.getElementById('selected_db');
	var selected_db_lbl = document.createElement('label');
	selected_db.appendChild(selected_db_lbl);
	selected_db_lbl.id = 'data_sel_label';
	selected_db_lbl.classList.add('db_label');
	selected_db_lbl.for = 'data_sel';
	selected_db_lbl.innerHTML = 'Selected<br>DataFrame';
	var img_list = [{'class':'arrow','id':'arrow_2','src':'arrow_right.png','oc':''},
					{'class':'img_db','id':'data_sel','src':'db.jpeg','oc':''},
					{'class':'arrow','id':'arrow_3','src':'arrow_right.png','oc':''}];
	for (var i=0; i<img_list.length; i++) {
		putImg(img_list[i],selected_db);
	}

	var desc_stats = document.getElementById('desc_stats');
	var desc_stats_div = document.createElement('div');
	desc_stats.appendChild(desc_stats_div);
	desc_stats_div.classList.add('block_div_div');
	desc_stats_div.id = 'descriptive_stats';
	desc_stats_div.innerHTML = 'Descriptive<br>Statistics';
	desc_stats_div.onclick = function() { doModelingAction('descriptive_stats'); };
	putImg({'class':'process_img','id':'descriptive','src':'process.png','oc':'doModelingAction("descriptive_stats")'},desc_stats);

	var norm_db = document.getElementById('norm_db');
	var norm_db_lbl = document.createElement('label');
	norm_db.appendChild(norm_db_lbl);
	norm_db_lbl.id = 'data_norm_lbl';
	norm_db_lbl.classList.add('db_label');
	norm_db_lbl.for = 'data_norm';
	norm_db_lbl.innerHTML = 'Normalized\nDataFrame';
	var img_list = [{'class':'arrow','id':'arrow_4','src':'arrow_right.png','oc':''},
					{'class':'img_db','id':'data_sel','src':'db.jpeg','oc':''},
					{'class':'arrow','id':'arrow_5','src':'arrow_right.png','oc':''}];
	for (var i=0; i<img_list.length; i++) {
		putImg(img_list[i],norm_db);
	}

	var modeling_box = document.getElementById('modeling_box');
	var box_title = document.createElement('div');
	modeling_box.appendChild(box_title);
	box_title.id = 'box_title';
	box_title.innerHTML = 'MODELING';
	var box_content = document.createElement('div');
	modeling_box.appendChild(box_content);
	box_content.id = 'box_content';
	box_margin = document.createElement('div');
	box_content.appendChild(box_margin);
	box_margin.classList.add('box_margin');
	box_margin.onclick = function() { doModelingAction('margin_modeling'); };
	box_margin.innerHTML = 'MARGIN<br>Modeling';
	box_copula = document.createElement('div');
	box_content.appendChild(box_copula);
	box_copula.classList.add('box_copula');
	box_copula.onclick = function() { doModelingAction('copula_modeling'); };
	box_copula.innerHTML = 'COPULA<br>Modeling';
	var box_img_list = [{'class':'box_arrow','id':'box_arrow_1','src':'arrow_right.png','oc':''},
						{'class':'box_process','id':'margin','src':'process.png','oc':'doModelingAction("margin_modeling")'},
						{'class':'box_arrow','id':'box_arrow_2','src':'arrow_right.png','oc':''},
						{'class':'model_img1','id':'model_img1','src':'margin_model.png','oc':''},
						{'class':'box_arrow','id':'box_arrow_3','src':'arrow_right.png','oc':''},
						{'class':'copula','id':'copula','src':'process.png','oc':'doModelingAction("copula_modeling")'},
						{'class':'box_arrow','id':'box_arrow_4','src':'arrow_right.png','oc':''},
						{'class':'model_img2','id':'model_img2','src':'copula_model.jpeg','oc':''},
						{'class':'box_arrow','id':'box_arrow_5','src':'arrow_right.png','oc':''}];
	for (var i=0; i<box_img_list.length; i++) {
		putImg(box_img_list[i],box_content);
	}

	var copula_graphic = document.getElementById('copula_graphic');
	var img_list = [{'class':'arrow','id':'arrow_6','src':'arrow_right.png','oc':''},
					{'class':'model_img3','id':'copula_img','src':'copula.jpeg','oc':''}];
	for (var i=0; i<img_list.length; i++) {
		putImg(img_list[i],copula_graphic);
	}

	Object.entries(stage_block_dic).forEach(([key, val]) => {
		if (val > session['stage']) { document.getElementById(key).style.border = 'solid grey 2px'; }
		else { document.getElementById(key).style.border = 'solid blue 2px'; }
	});

}
function putImg(img_dic,parent) {
	var img = document.createElement('img');
	parent.appendChild(img);
	img.id = img_dic['id'];
	img.classList.add(img_dic['class']);
	img.src = static_dir+'images/'+img_dic['src'];
	img.setAttribute('onclick',img_dic['oc']);
}
function putP(p_dic,parent) {
	var p = document.createElement('p');
	parent.appendChild(p);
	p.classList.add(p_dic['class']);
	p.innerHTML = p_dic['text'];
}
function doModelingAction(action) {
	var up_data = {'action':action};
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		method : 'POST',
		url: 'doModelingAction',
		data: up_data,
		success: function(data) {
			session['stage'] = data['stage'];
			if (action=='dataset_selection') { loadDataSelection(data); }
			if (action=='dataset_slicing') { goDataSlicing(data); }
			if (action=='descriptive_stats') { loadDescriptiveStats(data); }
			if (action=='margin_modeling') { loadMarginModeling(data); }
			if (action=='copula_modeling') { loadCopulaModeling(data); }
		}
	});
}

//*************************************//
//******** DATASET SELECTION **********//
//*************************************//
function loadDataSelection(data) {
	var container = document.getElementById('container');
	container.innerHTML = '';
	var title = document.createElement('h4');
	container.appendChild(title);
	title.innerHTML = 'DATA SELECTION';
	var datasel_div = document.createElement('div');
	container.appendChild(datasel_div);
	datasel_div.id = 'datasel_div';
	datasel_div.classList.add('row','datasel_div');
	var datasel_lbl = document.createElement('label');
	datasel_div.appendChild(datasel_lbl);
	datasel_lbl.innerHTML = 'Define dataset:';
	var datasel_sel = document.createElement('select');
	datasel_div.appendChild(datasel_sel);
	datasel_sel.id = 'datasel_sel';
	for (var i = 0; i < dataset_list.length; i++) {
		var val = dataset_list[i];
		var opt = document.createElement('option');
		datasel_sel.appendChild(opt);
		opt.value = val;
		opt.text = val;
	}
	var datasel_btn = document.createElement('button');
	datasel_div.appendChild(datasel_btn);
	datasel_btn.type = 'button';
	datasel_btn.innerHTML = 'OK';
	datasel_btn.onclick = function() { loadDataset(datasel_sel.options[datasel_sel.selectedIndex].value); };
}
function loadDataset(dataset) {
	session['dataset'] = dataset;
	var up_data = {'action':'load_'+dataset};
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		method : 'POST',
		url: 'doModelingAction',
		data: up_data,
		success: function(data) {
			session['stage'] = data['stage'];
			if (dataset=='DATASUS') { loadDatasusFileSelection(data); }
			if (dataset=='toy_up') { loadToyDatasetSelection(data); }
			if (dataset=='toy_indep') { loadToyDatasetSelection(data); }
			if (dataset=='toy_down') { loadToyDatasetSelection(data); }
			if (dataset=='ForestFire') { loadForestFireSelection(data); }
			if (dataset=='generic') { loadOtherDatasetSelection(data); }
		}
	});
}

//*************************************//
//****** TOY DATASET SELECTION ********//
//*************************************//
function loadToyDatasetSelection(data) {
	session['data'] = data;
	alert('Data successfully acquired from files!');
	loadModelingDiagram();
}

//*************************************//
//***** DATASUS DATA SELECTION ********//
//*************************************//
function loadDatasusFileSelection(data) {
	//sessionStorage.setItem('data',JSON.stringify(data));
	session['data'] = data;
    var proj_name = data['proj_name'];
    var dataset_list = data['dataset_list'];
    var datatype_list = data['datatype_list'];
    var type_list = data['type_list'];
    var year_list = data['year_list'];
    var uf_list = data['uf_list'];
    var month_list = data['month_list'];
	var container = document.getElementById('container');
	var main_div = document.createElement('div');
	container.appendChild(main_div);
    var title = document.createElement('h4');
	main_div.appendChild(title);
	title.innerHTML = 'FILE SELECTION';
	var boxes_row = document.createElement('div');
	main_div.appendChild(boxes_row);
	boxes_row.classList.add('row','datasus_file_row');
	Object.entries(datasus_sel_dic).forEach(([key, val]) => {
		var col_div = document.createElement('div');
		boxes_row.appendChild(col_div);
		col_div.classList.add(val['class'],'datasus_file_box');
		var col_title_div = document.createElement('h5');
		col_div.appendChild(col_title_div);
		col_title_div.innerHTML = val['title'];
		var box_div = document.createElement('div');
		col_div.appendChild(box_div);
		box_div.id = key+'_div';
		box_div.classList.add('datasus_file_div');
	});
	var button_row = document.createElement('div');
	main_div.appendChild(button_row);
	button_row.classList.add('row','datasus_file_row');
	var acq_btn = document.createElement('button');
	button_row.appendChild(acq_btn);
	acq_btn.type = 'button';
	acq_btn.innerHTML = 'OK';
	acq_btn.onclick = function () { acquireDataFromFiles(); };

	var datatype_sel = document.createElement('select');
	var box_div = document.getElementById('datatype_div');
	datatype_div.appendChild(datatype_sel);
	datatype_sel.id = 'datatype_sel';
	datatype_sel.onchange = function () { selDatatype(); };
	//datatype_sel.setAttribute('onchange','selDatatype();');
	addOptions("datatype_sel",datatype_list);
	document.getElementById("datatype_sel").setAttribute('selectedIndex',0);
	addChkBoxes(type_list,"type_div");
	addChkBoxes(year_list,"year_div");
	addChkBoxes(uf_list,"uf_div");
	addChkBoxes(month_list,"month_div");
}
function selDatatype() {
	var sel = document.getElementById("datatype_sel");
	var idx = sel.selectedIndex;
	var opt = sel.options[idx].value;
	data = {'dataset':session['dataset'],'datatype':opt};
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		method : 'POST',
		url: 'selectDataFileOptions',
		data: data,
		success: function(data) { loadDataFileOptions(data); }
	});
	return true;
}
function loadDataFileOptions(data) {
	session['data'] = data;
	addChkBoxes(data['type_list'],"type_div");
	addChkBoxes(data['year_list'],"year_div");
	addChkBoxes(data['uf_list'],"uf_div");
	addChkBoxes(data['month_list'],"month_div");
}

//*************************************//
//**** OTHER DATASET SELECTION ********//
//*************************************//
function loadForestFireSelection(data) {
	alert('Not yet implemented...');
}
function loadOtherDatasetSelection(data) {
	var upload_div = document.createElement('div');
	document.getElementById('datasel_div').appendChild(upload_div);
	upload_div.style = 'margin:20px;';
	var upload_lbl = document.createElement('label');
	upload_div.appendChild(upload_lbl);
	upload_lbl.for = 'upfile';
	upload_lbl.classList.add("col-md-3");
	upload_lbl = 'Upload file';
	var upload_ipt = document.createElement('input');
	upload_div.appendChild(upload_ipt);
	upload_ipt.classList.add('col-md-9');
	upload_ipt.type = 'file';
	upload_ipt.id = 'upfile';
	upload_ipt.name = 'upfile';
	upload_ipt.onchange = function () { doUploadDataset(); };
}

function doUploadDataset() {
	var formData = new FormData();
	formData.append('file', $('#upfile')[0].files[0]);
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		type : 'POST',
		processData: false,  // tell jQuery not to process the data
		contentType: false,  // tell jQuery not to set contentType
		cache: false,
		enctype: 'multipart/form-data',
		url: 'doUploadDataset',
		data: formData,
		success: function(data) {
			alert('Data successfully acquired from uploaded file!');
			loadModelingDiagram();
		}
	});
	return true;
}

//*************************************//
//********* DATA ACQUISITION **********//
//*************************************//
function acquireDataFromFiles() {
	var sels = {'dataset':'datasus','datatype':'','type_list':[],'year_list':[],'uf_list':[],'month_list':[]};
	var datatype_sel = document.getElementById('datatype_sel');
	var idx = datatype_sel.selectedIndex;
	sels['datatype'] = datatype_sel.options[idx].value;
	var data = session['data'];
	var lists = {'type':data['type_list'],'year':data['year_list'],
		'uf':data['uf_list'],'month':data['month_list']};
	lists_keys = Object.keys(lists);
	for (var i=0; i<lists_keys.length; i++) {
		var_str = lists_keys[i];
		list = lists[var_str];
		var sel_list = [];
		for (var j=0; j<list.length; j++) {
			var chkbox_id = var_str+"_div_chkbox"+j;
			var chkbox = document.getElementById(chkbox_id);
			if (chkbox.checked) { sel_list.push(chkbox.value); }
		};
		sels[var_str+"_list"] = sel_list;
	}
	var jreq = JSON.stringify(sels);
	var data = {'jreq':jreq};
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		method : 'POST',
		url: 'data_acquisition',
		data: data,
		success: function(data) {
			if (multiproc) { exec_window = window.open('', 'ExecWindow', 'width=400,height=200,top=350,left=600,titlebar=no'); }
			else { exec_window = null; }
			waitProcessing(exec_window,'',0,'acquireDataFromFiles_end');
		}
	});
	return true;
}
function acquireDataFromFiles_end() {
	data = {};
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		method : 'POST',
		url: 'data_acquisition_end',
		data: data,
		success: function(data) {
			alert('Data successfully acquired from files!');
			loadModelingDiagram();
		}
	});
}

//***************************************************//
//*********** DATA FILTERING AND SLICING ************//
//***************************************************//
function goDataSlicing() {
	alert('Loading data. This may take some moments, please wait.');
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		method : 'POST',
		url: 'load_data_slicing',
		data: {},
		success: function(data) {
			loadDataSlicing(data);
		}
	});
	return true;
}
function loadDataSlicing(data) {
    var proj_name = data['proj_name'];
    var feature_list = data['feature_list'];
    var val_mtx = data['val_mtx'];
    value_list = data['value_list'];
    var example = data['example'];
    var description_list = data['feature_list'];
	var container = document.getElementById('container');
	container.innerHTML = '';

	var title_div = document.createElement('div');
	container.appendChild(title_div);
	title_div.classList.add('row');
		var title = document.createElement('h4');
		title_div.appendChild(title);
		title.innerHTML = 'DATA ACQUISITION';
		title.classList.add('title');

	var data_acq_main_div = document.createElement('div');
	container.appendChild(data_acq_main_div);
	data_acq_main_div.classList.add('row','data_acquisition_row');

		var data_full_div = document.createElement('div');
		data_acq_main_div.appendChild(data_full_div);
		data_full_div.classList.add('col-md-4','data_acquisition_col');

			var data_full_title = document.createElement('h4');
			data_full_div.appendChild(data_full_title);
			data_full_title.innerHTML = 'DATASUS DATA';

			var data_full_ftdesc_title = document.createElement('h5');
			data_full_div.appendChild(data_full_ftdesc_title);
			data_full_ftdesc_title.innerHTML = 'Features Description';
			var data_full_ftdesc_div = document.createElement('div');
			data_full_div.appendChild(data_full_ftdesc_div);
			data_full_ftdesc_div.id = 'feat_desc';
			data_full_ftdesc_div.classList.add('data_acquisition_box')

			var data_full_ftexamp_title = document.createElement('h5');
			data_full_div.appendChild(data_full_ftexamp_title);
			data_full_ftexamp_title.innerHTML = 'Example';
			var data_full_ftexamp_div = document.createElement('div');
			data_full_div.appendChild(data_full_ftexamp_div);
			data_full_ftexamp_div.id = 'feat_examp';
			data_full_ftexamp_div.classList.add('data_acquisition_box')

		var data_picking_div = document.createElement('div');
		data_acq_main_div.appendChild(data_picking_div);
		data_picking_div.classList.add('col-md-4','data_acquisition_col');
		data_picking_div.style.border = 'solid 1px';

			var data_picking_title = document.createElement('h4');
			data_picking_div.appendChild(data_picking_title);
			data_picking_title.innerHTML = 'FILTERING AND SLICING';

			var data_filter_title = document.createElement('h5');
			data_picking_div.appendChild(data_filter_title);
			data_filter_title.innerHTML = 'Filter Selection';

			var data_filter_sel_div = document.createElement('div');
			data_picking_div.appendChild(data_filter_sel_div);
			data_filter_sel_div.classList.add('row');
			data_filter_sel_div.style = 'margin:0px;padding:0px;';

				var data_filter_feat_div = document.createElement('div');
				data_filter_sel_div.appendChild(data_filter_feat_div);
				data_filter_feat_div.classList.add('col-md-5');

					var data_filter_feat_title = document.createElement('div');
					data_filter_feat_div.appendChild(data_filter_feat_title);
					data_filter_feat_title.innerHTML = 'Feature';

					var data_filter_feat_sel = document.createElement('select');
					data_filter_feat_div.appendChild(data_filter_feat_sel);
					data_filter_feat_sel.id = 'filter_feature_sel'; 
					data_filter_feat_sel.onchange = function () { updateChkBoxes('filter_feature_sel','filter_divboxes'); };
					data_filter_feat_sel.style = 'font-size:9px; width:120px;';

					var data_filter_allcheck_btn = document.createElement('button');
					data_filter_feat_div.appendChild(data_filter_allcheck_btn);
					data_filter_allcheck_btn.type = 'button';
					data_filter_allcheck_btn.onclick = function () { markAllBoxes('filter_divboxes'); };
					data_filter_allcheck_btn.style = 'font-size:12px;margin-top:10px;';
					data_filter_allcheck_btn.innerHTML = 'All';

					var data_filter_alluncheck_btn = document.createElement('button');
					data_filter_feat_div.appendChild(data_filter_alluncheck_btn);
					data_filter_alluncheck_btn.type = 'button';
					data_filter_alluncheck_btn.onclick = function () { unmarkAllBoxes('filter_divboxes'); };
					data_filter_alluncheck_btn.style = 'font-size:12px;margin-top:10px;';
					data_filter_alluncheck_btn.innerHTML = 'None';

				var data_filter_val_div = document.createElement('div');
				data_filter_sel_div.appendChild(data_filter_val_div);
				data_filter_val_div.classList.add('col-md-5');

					var data_filter_val_title = document.createElement('div');
					data_filter_val_div.appendChild(data_filter_val_title);
					data_filter_val_title.innerHTML = 'Values';

					var data_filter_val_boxes = document.createElement('div');
					data_filter_val_div.appendChild(data_filter_val_boxes);
					data_filter_val_boxes.id = 'filter_divboxes';
					data_filter_val_boxes.classList.add('row');
					data_filter_val_boxes.style = 'height:75px;overflow-y:auto;border:solid 1px;background-color:#FFF;';

				var data_filter_btn_div = document.createElement('div');
				data_filter_sel_div.appendChild(data_filter_btn_div);
				data_filter_btn_div.classList.add('col-md-2');

					var data_filter_btn = document.createElement('button');
					data_filter_btn_div.appendChild(data_filter_btn);
					data_filter_btn.type = 'button';
					data_filter_btn.onclick = function () { addFilter(); };
					data_filter_btn.style = 'font-size:12px;margin-top:20px;margin-right:5px;';
					data_filter_btn.innerHTML = 'Add';

			var data_filter_textarea_div = document.createElement('div');
			data_picking_div.appendChild(data_filter_textarea_div);
			data_filter_textarea_div.classList.add('row','data_acquisition_box');
			data_filter_textarea_div.style = 'height:50px;';

				data_filter_textarea = document.createElement('textarea');
				data_filter_textarea_div.appendChild(data_filter_textarea);
				data_filter_textarea.classList.add('data_acquisition_textarea');
				data_filter_textarea.id = 'filter_text';
				data_filter_textarea.name = 'filter_text';
				data_filter_textarea.value = '';

			var data_slice_title = document.createElement('h5');
			data_picking_div.appendChild(data_slice_title);
			data_slice_title.innerHTML = 'Slicing Selection';

			var data_slice_div = document.createElement('div');
			data_picking_div.appendChild(data_slice_div);
			data_slice_div.classList.add('row');
			data_slice_div.style = 'margin:0px; padding:0px;';

				/*
				var data_slice_feat_div = document.createElement('div');
				data_slice_div.appendChild(data_slice_feat_div);
				data_slice_feat_div.classList.add('col-md-3');

					var data_slice_feat_title = document.createElement('div');
					data_slice_feat_div.appendChild(data_slice_feat_title);
					data_slice_feat_title.innerHTML = 'Feature';

				var data_slice_sel_div = document.createElement('div');
				data_slice_div.appendChild(data_slice_sel_div);
				data_slice_sel_div.classList.add('col-md-7');

					var data_slice_feat_sel = document.createElement('select');
					data_slice_sel_div.appendChild(data_slice_feat_sel);
					data_slice_feat_sel.id = 'feature_slc'; 
					data_slice_feat_sel.style = 'font-size:9px; width:100px;';
				*/
				var data_slice_allcheck_div = document.createElement('div');
				data_slice_div.appendChild(data_slice_allcheck_div);
				data_slice_allcheck_div.classList.add('col-md-4');

					var data_slice_allcheck_btn = document.createElement('button');
					data_slice_allcheck_div.appendChild(data_slice_allcheck_btn);
					data_slice_allcheck_btn.type = 'button';
					data_slice_allcheck_btn.onclick = function () { markAllBoxes('slice_divboxes'); };
					data_slice_allcheck_btn.style = 'font-size:10px;margin-top:10px;';
					data_slice_allcheck_btn.innerHTML = 'All';

					var data_slice_alluncheck_btn = document.createElement('button');
					data_slice_allcheck_div.appendChild(data_slice_alluncheck_btn);
					data_slice_alluncheck_btn.type = 'button';
					data_slice_alluncheck_btn.onclick = function () { unmarkAllBoxes('slice_divboxes'); };
					data_slice_alluncheck_btn.style = 'font-size:10px;margin-top:10px;';
					data_slice_alluncheck_btn.innerHTML = 'None';

				var data_slice_feat_div = document.createElement('div');
				data_slice_div.appendChild(data_slice_feat_div);
				data_slice_feat_div.classList.add('col-md-6');

					var data_slice_feat_title = document.createElement('div');
					data_slice_feat_div.appendChild(data_slice_feat_title);
					data_slice_feat_title.innerHTML = 'Features';

					var data_slice_feat_boxes = document.createElement('div');
					data_slice_feat_div.appendChild(data_slice_feat_boxes);
					data_slice_feat_boxes.id = 'slice_divboxes';
					data_slice_feat_boxes.classList.add('row');
					data_slice_feat_boxes.style = 'height:50px;overflow-y:auto;border:solid 1px;background-color:#FFF;';

				var data_slice_btn_div = document.createElement('div');
				data_slice_div.appendChild(data_slice_btn_div);
				data_slice_btn_div.classList.add('col-md-2');
				data_slice_btn_div.style = 'text-align:center;margin:0px;padding:0px;font-size:10px;';

					var data_slice_btn = document.createElement('button');
					data_slice_btn_div.appendChild(data_slice_btn);
					data_slice_btn.type = 'button';
					data_slice_btn.onclick = function () { addSlicing(); };
					data_slice_btn.style = 'font-size:12px;';
					data_slice_btn.innerHTML = 'Add';

				var data_slice_textarea_div = document.createElement('div');
				data_picking_div.appendChild(data_slice_textarea_div);
				data_slice_textarea_div.id = 'filter_acq_feat_desc';
				data_slice_textarea_div.classList.add('row','data_acquisition_box');
				data_slice_textarea_div.style = 'height:50px;';

					data_slice_textarea = document.createElement('textarea');
					data_slice_textarea_div.appendChild(data_slice_textarea);
					data_slice_textarea.classList.add('data_acquisition_textarea');
					data_slice_textarea.id = 'slicing_text';
					data_slice_textarea.name = 'slicing_text';
					data_slice_textarea.value = '';

			var data_filter_apply_div = document.createElement('div');
			data_picking_div.appendChild(data_filter_apply_div);
			data_filter_apply_div.classList.add('row');
			data_filter_apply_div.style = 'text-align:center;font-size:10px;';

				var data_filter_apply_space_title = document.createElement('span');
				data_filter_apply_div.appendChild(data_filter_apply_space_title);
				data_filter_apply_space_title.innerHTML = 'Space';

				var data_filter_apply_space_sel = document.createElement('select');
				data_filter_apply_div.appendChild(data_filter_apply_space_sel);
				data_filter_apply_space_sel.id = 'apply_space';
				data_filter_apply_space_sel.style = 'font-size:9px; width:100px;';

				var data_filter_apply_time_title = document.createElement('span');
				data_filter_apply_div.appendChild(data_filter_apply_time_title);
				data_filter_apply_time_title.innerHTML = 'Time';

				var data_filter_apply_time_sel = document.createElement('select');
				data_filter_apply_div.appendChild(data_filter_apply_time_sel);
				data_filter_apply_time_sel.id = 'apply_time';
				data_filter_apply_time_sel.style = 'font-size:9px; width:100px;';

				var data_filter_apply_btn = document.createElement('button');
				data_filter_apply_div.appendChild(data_filter_apply_btn);
				data_filter_apply_btn.type = 'button';
				data_filter_apply_btn.onclick = function () { getSelectedDataframe(); };
				data_filter_apply_btn.innerHTML = 'Apply';

		var data_cut_div = document.createElement('div');
		data_acq_main_div.appendChild(data_cut_div);
		data_cut_div.classList.add('col-md-4','data_acquisition_col');

			var data_cut_title = document.createElement('h4');
			data_cut_div.appendChild(data_cut_title);
			data_cut_title.innerHTML = 'ACQUIRED DATAFRAME';

			var data_cut_ftdesc_title = document.createElement('h5');
			data_cut_div.appendChild(data_cut_ftdesc_title);
			data_cut_ftdesc_title.innerHTML = 'Features Description';

			var data_cut_ftdesc_div = document.createElement('div');
			data_cut_div.appendChild(data_cut_ftdesc_div);
			data_cut_ftdesc_div.id = 'feat_desc_out';
			data_cut_ftdesc_div.classList.add('data_acquisition_box')

			var data_cut_ftexamp_title = document.createElement('h5');
			data_cut_div.appendChild(data_cut_ftexamp_title);
			data_cut_ftexamp_title.innerHTML = 'Example';

			var data_cut_ftexamp_div = document.createElement('div');
			data_cut_div.appendChild(data_cut_ftexamp_div);
			data_cut_ftexamp_div.id = 'feat_examp_out';
			data_cut_ftexamp_div.classList.add('data_acquisition_box');

			var data_cut_btn_div = document.createElement('div');
			data_cut_div.appendChild(data_cut_btn_div);
			data_cut_btn_div.classList.add('row')
			data_cut_btn_div.style = 'text-align:center;font-size:12px;';

				var data_cut_btn = document.createElement('button');
				data_cut_btn_div.appendChild(data_cut_btn);
				data_cut_btn.type = 'button';
				data_cut_btn.onclick = function () { loadModelingDiagram(); };
				data_cut_btn.innerHTML = 'Return to Model';

	head_list = ['Features','Description'];
	value_mtx = [];
	for (var i = 0; i<feature_list.length; i++) {
		value_mtx.push([feature_list[i],'No feature description in imported data.']);
	};
	addTable('feat_desc',head_list,value_mtx);
	addTable('feat_examp',feature_list,val_mtx.slice(0,5));
	addOptions('filter_feature_sel',feature_list);
	var box_list = value_list[0];
	addChkBoxes(box_list,'filter_divboxes');
	//addOptions('feature_slc',feature_list);
	//document.getElementById('feature_slc').options[0].selected = true;
	var box_list = feature_list;
	addChkBoxes(box_list,'slice_divboxes');
	addOptions('apply_time',['no_time']);
	addOptions('apply_time',feature_list);
	addOptions('apply_space',['no_space']);
	addOptions('apply_space',feature_list);
}
function updateChkBoxes(sel_id,boxes_id) {
	var ftr_sel = document.getElementById(sel_id);
	var idx = ftr_sel.selectedIndex;
	var opt = ftr_sel.options[idx].value;
	var box_list = value_list[idx];
	$("#"+boxes_id).text("");
	addChkBoxes(box_list,boxes_id);
}
function markAllBoxes (boxes_id) {
	var i = 0;
	var go = true;
	while (go) {
		var chkbox_id = boxes_id+"_chkbox"+i;
		var chkbox = document.getElementById(chkbox_id);
		if( chkbox != null ){
			chkbox.checked = true;
			i++;
		}
		else { go = false; }
	}
}
function unmarkAllBoxes (boxes_id) {
	var i = 0;
	var go = true;
	while (go) {
		var chkbox_id = boxes_id+"_chkbox"+i;
		var chkbox = document.getElementById(chkbox_id);
		if( chkbox != null ){
			chkbox.checked = false;
			i++;
		}
		else { go = false; }
	}
}
function addFilter() {
	var ftr_sel = document.getElementById("filter_feature_sel");
	var ftr_idx = ftr_sel.selectedIndex;
	var ftr = ftr_sel.options[ftr_idx].value;
	var box_list = value_list[ftr_idx];
	var vals = [];
	for (var i=0; i<box_list.length; i++) {
		var chkbox = document.getElementById("filter_divboxes_chkbox"+i);
		if (chkbox.checked) { vals.push(chkbox.value); }
	}
	var e_flt = document.getElementById("filter_text");
	e_flt.value = e_flt.value+ftr+"="+String(vals)+"; ";
}
function addSlicing() {
	/*
	//var e_slc = document.getElementById("feature_slc");
	//var slc = e_slc.options[e_slc.selectedIndex].text;
	var box_list = data['feature_list'];
	var vals = [];
	for (var i=0; i<box_list.length; i++) {
		var chkbox = document.getElementById("filter_divboxes_chkbox"+i);
		if (chkbox.checked) { vals.push(chkbox.value); }
	}
	var e_slc_txt = document.getElementById("slicing_text");
	if (e_slc_txt.value=='<no filter>') {e_slc_txt.value='';}
	e_slc_txt.value = e_slc_txt.value+slc+";";
	*/
	var vals = '';
	var i=0;
	var go=true;
	while (go) {
		var chkbox_id = "slice_divboxes_chkbox"+i;
		var chkbox = document.getElementById(chkbox_id);
		if( chkbox != null ){
			if (chkbox.checked) { vals = vals+chkbox.value+';'; }
			i++;
		}
		else { go=false; }
	}
	var e_slc_txt = document.getElementById("slicing_text");
	//if (e_slc_txt.value=='<no filter>') {e_slc_txt.value='';}
	e_slc_txt.value = e_slc_txt.value+vals;
}
function getSelectedDataframe() {
	var filter_text = document.getElementById('filter_text').value;
	var slicing_text = document.getElementById('slicing_text').value;
	var e_time = document.getElementById("apply_time");
	var time_col = e_time.options[e_time.selectedIndex].text;
	var e_space = document.getElementById("apply_space");
	var space_col = e_space.options[e_space.selectedIndex].text;
	data = {'filter_text':filter_text,'slicing_text':slicing_text,'time_col':time_col,'space_col':space_col};
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		method : 'POST',
		url: 'selectData',
		data: data,
		success: function(data) { loadDataframe(data); }
	});
	return true;
}
function loadDataframe(data) {
	var feature_list = data['feature_list'];
	session['feature_list'] = feature_list;
	val_mtx = data['val_mtx'];
	value_mtx = [];
	for (var i = 0; i<feature_list.length; i++) {
		value_mtx.push([feature_list[i],'Here goes a detailed but concise feature description.']);
	};
	head_list = ['Features','Description'];
	$("#feat_desc_out").text("");
	$("#feat_examp_out").text("");
	addTable("feat_desc_out",head_list,value_mtx);
	mtx = val_mtx.slice(0,5);
	addTable("feat_examp_out",feature_list,mtx);
	return true;
}


//*************************************//
//********* DATA DESCIPTION ***********//
//*************************************//
function loadDescriptiveStats(data) {
    var proj_name = data['proj_name'];
	var feature_list = data['feature_list'];
	sessionStorage.setItem('feature',feature_list[0]);
	sessionStorage.setItem('fig_id',0);
	var fig_type_list = [];
	var container = document.getElementById('container');
	container.innerHTML = '';
	var title_div = document.createElement('div');
	container.appendChild(title_div);
	title_div.classList.add('row','dw-row');
	title_div.style = 'height:6%;position:relative;width:100%;border:solid 1px;background-color:#CCC;margin:0px;font-size:9px;';
		var title1_div = document.createElement('div');
		title_div.appendChild(title1_div);
		title1_div.classList.add('col-md-8');
		title1_div.style = 'font-size:16px;font-weight:bold;text-align:center;';
		title1_div.innerHTML = 'DESCRIPTIVE STATISTICS';
		var title2_div = document.createElement('div');
		title_div.appendChild(title2_div);
		title2_div.classList.add('col-md-2');
			var title2_sel = document.createElement('select');
			title2_div.appendChild(title2_sel);
			title2_sel.id = 'sel_feat';
			title2_sel.style = 'width:120px;';
			var title2_btn = document.createElement('button');
			title2_div.appendChild(title2_btn);
			title2_btn.type="button";
			title2_btn.onclick = function () { makeDescription(); };
			title2_btn.innerHTML = 'OK';
		var title3_div = document.createElement('div');
		title_div.appendChild(title3_div);
		title3_div.classList.add('col-md-2');
			var title3_btn = document.createElement('button');
			title3_div.appendChild(title3_btn);
			title3_btn.type = 'button';
			title3_btn.onclick = function () { loadModelingDiagram(); };
			title3_btn.innerHTML = 'Return to Model';

	var row1_div = document.createElement('div');
	container.appendChild(row1_div);
	row1_div.classList.add('row','dw-row');
	row1_div.style = 'width:100%;height:47%;position:relative;border:solid 1px;background-color:#FFF;margin:0px;';

		row1_list = [{'title':'Descriptive Measures','id':'measure'},
					{'title':'Histogram','id':'histogram'},
					{'title':'Boxplot','id':'boxplot'}];
		for (var i = 0; i < row1_list.length; i++) {
			dic = row1_list[i];
			var div = document.createElement('div');
			row1_div.appendChild(div);
			div.id = dic['id'];
			div.classList.add('col-md-4');
			div.style = 'border:solid 1px;position:relative;height:100%;';
			var tit_div = document.createElement('div');
			div.appendChild(tit_div);
			tit_div.style = 'font-weight:bold;text-align:center;';
			tit_div.innerHTML = dic['title'];
			var fig_div = document.createElement('div');
			div.appendChild(fig_div);
			fig_div.id = dic['id']+'_result';
			fig_div.style = 'text-align:center;';
		}

	var row2_div = document.createElement('div');
	container.appendChild(row2_div);
	row2_div.classList.add('row','dw-row');
	row2_div.style = 'position:relative;width:100%;height:47%;border:solid 1px;background-color:#FFF;margin:0px;';

		row2_list = [{'title':'Time Distribution','id':'time_dist'},
					{'title':'Space Distribution','id':'space_dist'},
					{'title':'Concordance','id':'concordance'}];
		for (var i=0; i<row2_list.length; i++) {
			dic = row2_list[i];
			var div = document.createElement('div');
			row2_div.appendChild(div);
			div.id = dic['id'];
			div.classList.add('col-md-4');
			div.style = 'border:solid 1px;position:relative;height:100%;';
			var tit_div = document.createElement('div');
			div.appendChild(tit_div);
			tit_div.style = 'font-weight:bold;text-align:center;';
			tit_div.innerHTML = dic['title'];
			var fig_div = document.createElement('div');
			div.appendChild(fig_div);
			fig_div.id = dic['id']+'_result';
			fig_div.classList.add('desc_stats_fig');
			fig_div.style = 'text-align:center;';
		}
		document.getElementById('concordance_result').style.overflow = 'auto';

	var sel = document.getElementById("sel_feat");
	for (opt_text of feature_list) {
		var opt = document.createElement("option");
		opt.text = opt_text;
		opt.value = opt_text;
		sel.appendChild(opt);
	}
}
function makeDescription() {
	document.getElementById('measure_result').innerHTML = '';
	document.getElementById('histogram_result').innerHTML = '';
	document.getElementById('boxplot_result').innerHTML = '';
	document.getElementById('time_dist_result').innerHTML = '';
	document.getElementById('space_dist_result').innerHTML = '';
	document.getElementById('concordance_result').innerHTML = '';
	var select = $("#sel_feat")[0];
	feature = select.options[select.selectedIndex].value;
	session['feature'] = feature;
	session['fig_id'] = 0;
	data = {'feature':feature};
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		method : 'POST',
		url: 'make_description',
		data: data,
		success: function(data) { loadDescription(data); }
	});
}
function loadDescription(data) {
	fig_type_list = data['fig_type_list'];
	addTable("measure_result",['Measure','Value'],data['val_mtx']);
	addMatrix('concordance_result',data['feature_list'],data['conc_mtx']);
	for (var i=0; i<data['conc_mtx'].length; i++) {
		var row = data['conc_mtx'][i];
		for (var j=0; j<row.length+1; j++) {
			cell_id = 'concordance_result_tab_'+i+'_'+j;
			var cell = document.getElementById(cell_id);
	    	if (j==0) { cell.style.backgroundColor = '#DDD'; }
			else {
				if (i==j-1) { cell.style.backgroundColor = 'lightgreen'; }
				if (i>j-1) { cell.style.backgroundColor = 'lightblue'; }
				if (i<j-1) { cell.style.backgroundColor = 'yellow'; }
			}
		}
	}
	var conc_names = document.createElement('div');
	document.getElementById('concordance_result').appendChild(conc_names);
	var rho_div = document.createElement('span');
	conc_names.appendChild(rho_div);
	rho_div.style = 'margin-left:0px;font-size:10px;font-weight:bold;color:blue;text-align:left;';
	rho_div.innerHTML = 'Spearman`s RHO in BLUE (lower half)';
	var br = document.createElement('br');
	conc_names.appendChild(br);
	var tau_div = document.createElement('span');
	conc_names.appendChild(tau_div);
	tau_div.style = 'margin-right:0px;font-size:10px;font-weight:bold;color:orange;text-align:right;';
	tau_div.innerHTML = 'Kendall`s TAU in YELLOW (upper half)';
	data = {'feature':session['feature'],'fig_id':session['fig_id']};
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		method : 'POST',
		url: 'sendFigure',
		data: data,
		success: function(data) { loadFigure(data); }
	});
}
function loadFigure(img_data) {
	var figures = {0:'histogram_result',1:'boxplot_result',2:'time_dist_result',3:'space_dist_result'};
	addFigure("data:image/png;base64,"+img_data,"270","170",figures[session['fig_id']]);
	session['fig_id'] = session['fig_id']+1;
	if (session['fig_id']<fig_type_list.length) {
		data = {'feature':session['feature'],'fig_id':session['fig_id']};
		$.ajax({
			headers: { 'X-CSRFToken': csrftoken },
			method : 'POST',
			url: 'sendFigure',
			data: data,
			success: function(data) {  loadFigure(data); }
		});
	}
	else {
		session['fig_id']=0;
	}
}



//*************************************//
//********* MARGIN MODELING ***********//
//*************************************//
function loadMarginModeling(data) {
    var proj_name = session['proj_name'];
	var feature_list = session['feature_list'];
	var feature = feature_list[0];
	var figs_nr = 0;
	var fig_id = 0;
	//session['feature_list'] = feature_list;
	session['feature'] = feature;
	session['fig_id'] = fig_id;
	var fig_type_list = [];
	var container = document.getElementById('container');
	container.innerHTML = '';

	var title_row = document.createElement('div');
	container.appendChild(title_row);
	title_row.classList.add('row');
	title_row.style = 'width:100%;height:6%;position:relative;border:solid 1px;background-color:#CCC;margin:0px;font-size:16px;font-weight:bold;text-align:center;';
	var title = document.createElement('div');
	title_row.appendChild(title);
	title.classList.add('col-md-10');
	title.innerHTML = 'MARGIN MODELING';
	var btn = document.createElement('button');
	title_row.appendChild(btn);
	btn.classList.add('col-md-2');
	btn.innerHTML = 'Return to Model';
	btn.style = 'font-size:9px;width:150px;margin-top:2px;';
	btn.onclick = function () { loadModelingDiagram(); }; //goCopula();

	var containt_row = document.createElement('div');
	container.appendChild(containt_row);
	containt_row.classList.add('row','dw-row');
	containt_row.style = 'width:100%;height:93.8%;position:relative;border:solid 1px;background-color:#CCC;margin:0px;font-size:16px;font-weight:bold;text-align:center;';
	containt_row.classList.add('row','dw-row');

	var lateral = document.createElement('div');
	containt_row.appendChild(lateral);
	lateral.classList.add('col-md-2');
	lateral.style = 'height:100%;border:solid 1px;padding:0px;';
	var feat_div = document.createElement('div');
	lateral.appendChild(feat_div);
		var feat_title = document.createElement('div');
		feat_div.appendChild(feat_title);
		feat_title.style = 'text-align:center;';
		feat_title.innerHTML = 'FEATURES';
		var btn_list = feature_list;
		for (var i=0; i<btn_list.length; i++) {
			var feature = btn_list[i];
			var btn = document.createElement('button');
			lateral.appendChild(btn);
			btn.id = btn_list[i]+'_btn';
			btn.innerHTML = feature;
			btn.style = 'font-size:9px;width:80px;margin:5px;color:black;';
			if (session['margins_modeled'].includes(feature)) { btn.style.color = 'blue'; }
			btn.onclick = function () { loadMarginStartData(this.innerHTML); };
		}
	var params_div = document.createElement('div');
	lateral.appendChild(params_div);
	params_div.id = 'params_div';
	params_div.style = 'margin:10px;padding:10px;';

	var central = document.createElement('div');
	containt_row.appendChild(central);
	central.classList.add('col-md-10');
	central.style = 'height:100%;border:solid 1px;padding:0px;';
	for (var i=0; i<margin_box_mtx.length; i++) {
		var box_row = margin_box_mtx[i];
		var row = document.createElement('div');
		central.appendChild(row);
		row.classList.add('row');
		row.style = 'width:100%;height:50%;position:relative;border:solid 1px;background-color:#FFF;margin:0px;padding:0px;';
		for (var j=0; j<box_row.length; j++) {
			var dic = box_row[j];
			var square = document.createElement('div');
			row.appendChild(square);
			square.classList.add('col-md-6');
			square.id = dic['id'];
			square.style = 'border:solid 1px;position:relative;height:100%;';
			var title = document.createElement('div');
			square.appendChild(title);
			title.id = dic['id']+'_title';
			title.style = 'font-weight:bold;text-align:center;';
			//title.innerHTML = dic['title'];
			var result = document.createElement('div');
			square.appendChild(result);
			result.id = dic['id']+'_result';
			result.style = 'text-align:center;width:99.5%;overflow:auto;';
		}
	}
}
/*function loadSelections(sel,list) {
	var sel = document.getElementById(sel);
	for (opt_text of list) {
		var opt = document.createElement("option");
		opt.text = opt_text;
		opt.value = opt_text;
		sel.appendChild(opt);
	}
}
function selFeat() {
	var sel = $("#sel_feat")[0];
	var idx = sel.selectedIndex;
	feature = sel.options[idx].value;
}*/
function loadMarginStartData(feature) {
	document.getElementById('params_div').innerHTML = '';
	for (var i=0; i<margin_box_mtx.length; i++) {
		var row = margin_box_mtx[i];
		for (var j=0; j<row.length; j++) {
			var dic = row[j];
			document.getElementById(dic['id']+'_result').innerHTML = '';
		}
	}
	session['feature'] = feature;
	data = {'feature':feature};
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		method : 'POST',
		url: 'loadMarginStartData',
		data: data,
		success: function(data) {
			document.getElementById(session['feature']+'_btn').style.color = 'red';
			if (data['mcmc_go']!=0) { var vtype = 'num'; }
			else  { var vtype = 'cat'; }
			for (var i=0; i<margin_box_mtx.length; i++) {
				var row = margin_box_mtx[i];
				for (var j=0; j<row.length; j++) {
					var dic = row[j];
					document.getElementById(dic['id']+'_title').innerHTML = dic[vtype+'_title']+' - '+feature;
				}
			}
			if (data['mcmc_go']!=0) {
				var div = document.getElementById("params_div");
				var params_div = makeMCMCParamsDiv(feature,mcmc_params,mcmc_options,data['auto_comps_nr']);
				div.innerHTML = '';
				div.appendChild(params_div);
			}
			else {
				data = {};
				$.ajax({
					headers: { 'X-CSRFToken': csrftoken },
					method : 'POST',
					url: 'makeMargin_end',
					data: data,
					success: function(data) { showMarginModeling(data); }
				});
			}
		}
	});
}
function makeMCMCParamsDiv(feature,params,options,auto_comps_nr) {
	var div = document.createElement("div");
	div.style = 'margin:auto;border:solid 1px;background-color:beige;';
	var params_title = document.createElement('div');
	div.appendChild(params_title);
	params_title.style = 'font-size:12px;';
	params_title.innerHTML = feature+' - MCMC Parameters';
	for (var i=0; i<params.length; i++) {
		param = params[i];
		opt_list = options[i];
		var sel_div = document.createElement("div");
		div.appendChild(sel_div);
		sel_div.style = 'text-align:left;font-size:10px;margin-left:10px;';
		var label = document.createElement("label");
		sel_div.appendChild(label);
		label.style = 'font-size:10px;font-weight:normal;width:60px;';
		label.for = sel;
		label.innerHTML = param;
		var sel = document.createElement("select");
		sel_div.appendChild(sel);
		sel.id = param;
		sel.style = 'width:60px;height:20px;';
		for (opt_text of opt_list) {
			var opt = document.createElement("option");
			opt.text = opt_text;
			opt.value = opt_text;
			sel.appendChild(opt);
		}
	}
	var btn = document.createElement("button");
	div.appendChild(btn);
	btn.type = 'button';
	btn.style = 'font-size:10px;';
	btn.textContent = 'Run MCMC';
	btn.onclick = function() { loadMCMCParams(); };
	var auto_div = document.createElement("div");
	div.appendChild(auto_div);
	auto_div.style = 'font-size:10px;font-weight:normal;';
	auto_div.innerHTML = '';//'*auto: Components nr detected = '+auto_comps_nr;
	return div;
}
function loadMCMCParams() {
	var mcmc = {'mcmc_round':0};
	for (var i=0; i<mcmc_params.length; i++) {
		sel_id = mcmc_params[i];
		var sel = $("#"+sel_id)[0];
		var idx = sel.selectedIndex;
		mcmc[sel_id] = sel.options[idx].value;
	}
	mcmc['rounds_nr'] = 1; // while not user chosen
	data = mcmc;
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		method : 'POST',
		url: 'loadMCMCParams',
		data: data,
		success: function(data) { makeMCMCMargin(data); }
	});
}
function makeMCMCMargin(data) {
	data = {};
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		method : 'POST',
		url: 'makeMCMCMargin',
		data: data,
		success: function(data) {
			if (multiproc) { exec_window = window.open('Ongoing processing, please wait.\n', 'ExecWindow', 'width=600,height=200,top=300,left=500,titlebar=no'); }
			else { exec_window = null; }
			waitProcessing(exec_window,'',0,'makeMCMCMargin_end');
		} 
	});
}
function makeMCMCMargin_end() {
	data = {};
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		method : 'POST',
		url: 'makeMCMCMargin_end',
		data: data,
		success: function(data) { goMargin_end(data); }
	});
}
function goMargin_end() {
	data = {};
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		method : 'POST',
		url: 'makeMargin_end',
		data: data,
		success: function(data) { showMarginModeling(data); }
	});
}
function showMarginModeling(data) {
	var params_result = document.getElementById('params_result');
	params_result.style = 'font-size:12px;font-weight:normal;margin:auto;padding:10px;width:99.5%;overflow:auto;';
	var head_list = ['comp\\param'].concat(data['labels']);
	var value_mtx = [];
	for (var i=0; i<data['params'].length; i++) {
		var row = ['Comp_'+(i+1)];
		for (var j=0; j<data['params'][i].length; j++) {
			row.push(data['params'][i][j]+' +/- '+data['params_std'][i][j]);
		}
		value_mtx.push(row);
	}
	addTable('params_result',head_list,value_mtx);
	figs_nr = parseInt(data['figs_nr']);
	fig_id = 0;
	data = {'fig_id':fig_id};
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		method : 'POST',
		url: 'sendMarginFigure',
		data: data,
		success: function(data) { loadMarginFigure(data); }
	});
}
function loadMarginFigure(img_data) {
	var fig_spot = fitting_div_list[fig_id];
	addFigure("data:image/png;base64,"+img_data,"250","180",fig_spot);
	document.getElementById(session['feature']+'_btn').style.color = 'blue';
	session['margins_modeled'].push(session['feature']);
	fig_id = fig_id+1;
	if (fig_id<figs_nr) {
		data = {'fig_id':fig_id};
		$.ajax({
			headers: { 'X-CSRFToken': csrftoken },
			method : 'POST',
			url: 'sendMarginFigure',
			data: data,
			success: function(data) {  loadMarginFigure(data); }
		});
	}
	else {
		fig_id=0;
	}
}
function goCopula() {
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		method : 'POST',
		url: 'copula_modeling', //'makeAllMargins',
		data: {},
		success: function(data) {
			if (data['margin_status']=='all') { loadModelingDiagram(); }
			else { alert('Not all margins modeled. Please model all margins.'); }
		}
	});
	return true;
}

/*
function makeMargin_roundstep(data) {
	if (data['mcmc_go']!=0) {
		data = {};
		$.ajax({
			headers: { 'X-CSRFToken': csrftoken },
			method : 'POST',
			url: 'makeMargin_roundstep',
			data: data,
			success: function(data) { makeMargin_roundstep(data); } 
		});
	}
	else {
		data = {};
		$.ajax({
			headers: { 'X-CSRFToken': csrftoken },
			method : 'POST',
			url: 'makeMargin_end',
			data: data,
			success: function(data) { showMarginModeling(data); }
		});
	}
}
function makeMargin_roundstep(data) {
	data = {};
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		method : 'POST',
		url: 'makeMargin_roundstep',
		data: data,
		success: function(data) { waitProcessing({},'makeMargin_roundstep',''); }
	});
}
*/


//*************************************//
//********* COPULA MODELING ***********//
//*************************************//
function loadCopulaModeling() {
	var feature_list = session['feature_list'];

	var container = document.getElementById('container');
	container.innerHTML = '';

	var title_row = document.createElement('div');
	container.appendChild(title_row);
	title_row.classList.add('row');
	title_row.style = 'width:100%;height:6%;position:relative;border:solid 1px;background-color:#CCC;margin:0px;font-size:16px;font-weight:bold;text-align:center;';
	var title = document.createElement('div');
	title_row.appendChild(title);
	title.classList.add('col-md-10');
	title.innerHTML = 'COPULA MODELING';
	var btn = document.createElement('button');
	title_row.appendChild(btn);
	btn.classList.add('col-md-2');
	btn.innerHTML = 'Return to Model';
	btn.style = 'font-size:9px;width:150px;margin-top:2px;';
	btn.onclick = function () { loadModelingDiagram(); };

	var containt_row = document.createElement('div');
	container.appendChild(containt_row);
	containt_row.classList.add('row','dw-row');
	containt_row.style = 'width:100%;height:93.8%;position:relative;border:solid 1px;background-color:#CCC;margin:0px;font-size:16px;font-weight:bold;text-align:center;';

	var lateral = document.createElement('div');
	containt_row.appendChild(lateral);
	lateral.classList.add('col-md-2');
	lateral.style = 'height:100%;border:solid 1px;padding:0px;';
	var cop_title = document.createElement('div');
	lateral.appendChild(cop_title);
	cop_title.style = 'text-align:center;font-size:12px;';
	cop_title.innerHTML = 'COPULA MODELING';
	var cop_btn = document.createElement('button');
	lateral.appendChild(cop_btn);
	cop_btn.id = 'cop_btn';
	cop_btn.innerHTML = 'Model copula';
	cop_btn.style = 'font-size:10px;width:150px;margin-top:2px;';
	cop_btn.onclick = function () { runCopulaModeling(); };

	var feat_2d_div = document.createElement('div');
	lateral.appendChild(feat_2d_div);
	feat_2d_div.id = 'feat_2d_div';
	feat_2d_div.style = 'margin:10px;border:solid 1px;background-color:beige;font-size:10px;font-weight:normal;';
		var feat_title = document.createElement('div');
		feat_2d_div.appendChild(feat_title);
		feat_title.style = 'text-align:center;font-size:12px;';
		feat_title.innerHTML = 'FEATURES PAIR ANALYSIS';
		for (var i=0; i<copula_box_mtx.length; i++) {
			var box_row = copula_box_mtx[i];
			for (var j=0; j<box_row.length; j++) {
				if (i==0) {
					var sel_div = document.createElement('div');
					feat_2d_div.appendChild(sel_div);
					sel_div.id = 'sel_div_'+j;
					sel_div.style = 'font.size:9px';
					var title = document.createElement('div');
					sel_div.appendChild(title);
					title.style = 'font.size:9px';
					title.innerHTML = 'Feature Pair '+(j+1);
				}
				else {
					var sel_div = document.getElementById('sel_div_'+j);
				}
				var sel = document.createElement('select');
				sel_div.appendChild(sel);
				sel.id = 'sel_d'+(i+1)+'_'+j;
				sel.style = 'width:80px;font-size:9px;';
				for (opt_text of feature_list) {
					var opt = document.createElement("option");
					opt.text = opt_text;
					opt.value = opt_text;
					opt.style = 'font-size:9px;'
					sel.appendChild(opt);
				}
			}
		}
		var graphic_btn = document.createElement('button');
		feat_2d_div.appendChild(graphic_btn);
		graphic_btn.innerHTML = 'Make 2D graphics';
		graphic_btn.style = 'font-size:9px;width:150px;margin-top:2px;';
		graphic_btn.onclick = function () { runCopulaGraphics(); };
		feat_2d_div.style.display = 'none';

	var central = document.createElement('div');
	containt_row.appendChild(central);
	central.classList.add('col-md-10');
	central.id = "empirical_result";
	central.style = 'height:100%;border:solid 1px;padding:0px;';

	for (var i=0; i<copula_box_mtx.length; i++) {
		var box_row = copula_box_mtx[i];
		var row = document.createElement('div');
		central.appendChild(row);
		row.classList.add('row');
		row.style = 'width:100%;height:50%;position:relative;border:solid 1px;background-color:#FFF;margin:0px;padding:0px;';
		for (var j=0; j<box_row.length; j++) {
			var dic = box_row[j];
			var square = document.createElement('div');
			row.appendChild(square);
			square.classList.add('col-md-4');
			square.id = dic['id'];
			square.style = 'border:solid 1px;position:relative;height:100%;';
			var title = document.createElement('div');
			square.appendChild(title);
			title.id = dic['id']+'_title';
			title.style = 'font-size:10px;font-weight:bold;text-align:center;';
			title.innerHTML = dic['title'];
			var subtitle = document.createElement('div');
			square.appendChild(subtitle);
			subtitle.id = dic['id']+'_subtitle';
			subtitle.style = 'font-size:10px;font-weight:normal;text-align:center;';
			subtitle.innerHTML = '';
			var result = document.createElement('div');
			square.appendChild(result);
			result.id = dic['id']+'_result';
			result.style = 'text-align:center;';
		}
	}

}
function runCopulaModeling() {
	alert('Copula modeling may take some time, please wait...');
	data = {};
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		method : 'POST',
		url: 'copula_modeling',
		data: data,
		success: function(data) {
			if (data['margin_status']=='all') {
				alert('Copula modeling successfully accomplished!');
				document.getElementById('cop_btn').style.color = 'blue';
				loadInitialGraphics();
				document.getElementById('feat_2d_div').style.display = 'block';
			}
			else { alert('Not all margins modeled. Please model all margins.'); }
		}
	});
}
function loadInitialGraphics() {
	var fig_param_list = [];
	for (var i=0; i<copula_box_mtx.length; i++) {
		var box_row = copula_box_mtx[i];
		for (var j=0; j<box_row.length; j++) {
			var dic = box_row[j];
			var d1 = j;
			var d2 = j+1;
			if (d2>(session['feature_list'].length-1)) {
    			d1=0;
    			d2=1;
    		}
			fig_param_list.push([d1,d2,dic['type'],dic['id']]);
		}
	}
	loadCopulaFigures(fig_param_list,0);
}
function runCopulaGraphics() {
	for (var i=0; i<copula_box_mtx.length; i++) {
		var box_row = copula_box_mtx[i];
		for (var j=0; j<box_row.length; j++) {
			var dic = box_row[j];
			document.getElementById(dic['id']+'_subtitle').style.display = 'none';
			document.getElementById(dic['id']+'_result').style.display = 'none';
		}
	}
	var fig_param_list = [];
	for (var i=0; i<copula_box_mtx.length; i++) {
		var box_row = copula_box_mtx[i];
		for (var j=0; j<box_row.length; j++) {
			var dic = box_row[j];
			var d1 = document.getElementById('sel_d1_'+j).selectedIndex;
			var d2 = document.getElementById('sel_d2_'+j).selectedIndex;
			fig_param_list.push([d1,d2,dic['type'],dic['id']]);
		}
	}
	loadCopulaFigures(fig_param_list,0);
}
function loadCopulaFigures(fig_param_list,state) {
	if (state<fig_param_list.length) {
		var fig_params = fig_param_list[state];
		data = {'d1':fig_params[0],'d2':fig_params[1],'fig_type':fig_params[2]};
		$.ajax({
			headers: { 'X-CSRFToken': csrftoken },
			method : 'POST',
			url: 'sendCopulaFigure',
			data: data,
			success: function(img_data) {
				document.getElementById(fig_params[3]+'_subtitle').style.display = 'block';
				document.getElementById(fig_params[3]+'_result').style.display = 'block';
				document.getElementById(fig_params[3]+'_subtitle').innerHTML = session['feature_list'][fig_params[0]]+' x '+session['feature_list'][fig_params[1]];
				addFigure("data:image/png;base64,"+img_data,"250","180",fig_params[3]+'_result');
				loadCopulaFigures(fig_param_list,state+1);
			}
		});
	}
	else {
		alert('All graphics loaded!');
	}
}
