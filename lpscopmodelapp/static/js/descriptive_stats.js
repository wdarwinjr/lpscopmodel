// ***** FUNCTIONS *****

function selFeat() {
	var select = $("#sel_feat")[0];
	var idx = select.selectedIndex;
	feature = select.options[idx].value;
}
function makeDescription() {
	data = {'feature':feature};
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		method : 'POST',
		url: 'make_description.php',
		data: data,
		success: function(data) { loadDescription(data); }
	});
}
function loadDescription(data) {
	fig_type_list = data['fig_type_list'];
	addTable("measure_result",['Measure','Value'],data['val_mtx']);
	addMatrix("concordance_result",data['feature_list'],data['conc_mtx']);
	data = {'feature':feature,'fig_id':fig_id};
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		method : 'POST',
		url: 'sendFigure.php',
		data: data,
		success: function(data) { loadFigure(data); }
	});
}
function loadFigure(img_data) {
	addFigure("data:image/png;base64,"+img_data,"180","fig"+fig_id+"_result");
	fig_id = fig_id+1;
	if (fig_id<fig_type_list.length) {
		data = {'feature':feature,'fig_id':fig_id};
		$.ajax({
			headers: { 'X-CSRFToken': csrftoken },
			method : 'POST',
			url: 'sendFigure.php',
			data: data,
			success: function(data) {  loadFigure(data); }
		});
	}
	else {
		fig_id=0;
	}
}
function goModelDiagram() {
	window.location.href = "model_diagram.php";
	return true;
}
