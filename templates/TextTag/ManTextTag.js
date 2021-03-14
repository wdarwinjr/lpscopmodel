// ***** FUNCTIONS *****

// *** Auxiliary Functions *** //

function sendInputs(txt_fname_out,text_out,tag_list_out,link_list_out,action_out) {
	var frm = document.getElementById("page_form");
	makeInput(frm,"txt_fname",txt_fname_out);
	makeInput(frm,"tag_list",tag_list_out);
	var link_list_json = encodeJsonArray(link_list_out);
	makeInput(frm,"link_list_json",link_list_json);
	makeInput(frm,"text",text_out);
	makeInput(frm,"action",action_out);
	frm.submit();
	return true;
}

function completeLinks(links) {
    loc = 0;
    complete_links = [];
    for (var i=0; i<links.length; i++){
	    var link = links[i];
	    //if (link[0]!=-1) {
		    if (link[1]>loc) {
		    	complete_links.push([-1,loc,link[1]-1]);
		    	complete_links.push(link);
		    }
		    else {
		    	complete_links.push(link);
		    }
	    //}
    	loc = link[2]+1;
    }
    if (loc<text.length) {complete_links.push([-1,loc,text.length-1]);}
    return complete_links;
}

function makeTag(tag_text,tag_id,clr) {
	var div = document.createElement("div");
	var ipt = document.createElement("input");
	var clr_spn = document.createElement("span");
	var lbl = document.createElement("label");
	ipt.type = "radio";
	ipt.id = "chkbox"+tag_id;
	ipt.name = "tag_group";
	ipt.value = tag_text;
	ipt.style = "width:20px;";
	clr_spn.innerHTML = "&nbsp;&nbsp;&nbsp;&nbsp;";
	clr_spn.style = "width:40px;font-size:10px;background-color:"+clr;
	lbl.htmlFor = "chkbox"+tag_id;
	lbl.style = "width:60px;font-size:14px;font-weight:normal;";
	lbl.innerHTML = "&nbsp;"+tag_text;
	div.appendChild(ipt);
	div.appendChild(clr_spn);
	div.appendChild(lbl);
	return div;
}

function insertLink(new_link,link_list_in) {
	// clear from blank links
    links = [];
    for (var i=0; i<link_list_in.length; i++){
	    link = link_list_in[i];
	    if (link[0]!=-1) {
		    	links.push(link);
		    }
    }
    // insert new link in start-ordered position
    var start = new_link[1];
    var ok = false;
	for (var i=0; i<links.length; i++) {
    	if (start<links[i][1]) {
		    links.splice(i, 0, new_link);
		    ok = true;
		    break;
    	}
    }
    if (!ok) {links.push(new_link);}
    // complete with blank links
    complete_links = completeLinks(links);
    return complete_links;
}

function getTagId() {
    var tag_id = -1;
    for (var i=0; i <tag_list.length; i++){
        var chkbox = document.getElementById("chkbox"+i);
        if (chkbox.checked) {
        	tag_id = i;//chkbox.value;
        	break;
        }
    }
    return tag_id;
}

function linkTag() {
	var txt_sel = window.getSelection();
	var node_id = txt_sel.anchorNode.parentNode.id; //get text parent "span"
	var start = txt_sel.anchorOffset;
	var finish = txt_sel.focusOffset-1;
    var tag_id = getTagId();
	var link_id = parseInt(node_id.substring(8,node_id.length));
	var offset = 0;
	if (link_id>0) {offset=link_list[link_id-1][2]+1;}
    var new_link = [tag_id,start+offset,finish+offset];
    link_list = insertLink(new_link,link_list);
    loadTaggedText();
    return true;
}

function loadArea(link_list_mask) {
	var txtarea = document.getElementById("txtarea");
	txtarea.innerHTML = "";
	if (link_list_mask.length>0) {
		for (var i=0; i<link_list_mask.length; i++) {
			link = link_list_mask[i];
			var spn = document.createElement("span");
			spn.id = "span_tag"+i;
			spn.name = "span_tag"+i;
			clr_id = link[0]%hlt_color.length;
			if (clr_id<0) {clr_id=clr_id+hlt_color.length;}
			spn.style = "background-color:"+hlt_color[clr_id];
			spn.innerHTML = text.substring(link[1],link[2]+1);
			txtarea.appendChild(spn);
		}
	}
	else {
		txtarea.innerHTML = text;
	}
	return true;
}

function makeInput(frm,inpt_name,inpt_var) {
	var inpt = document.createElement("input");
	inpt.setAttribute("type", "hidden");
	inpt.setAttribute("name", inpt_name);
	inpt.setAttribute("value", inpt_var);
	frm.appendChild(inpt);
	return true;
}



// *** AJAX Functions *** //

function selTxtDownFile() {
	txt_fname = $('#txt_downfile').children("option:selected").val();
	data = {'txt_fname':txt_fname};
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		method : 'POST',
		url: 'selTextDownFile',
		data: data,
		success: function(data) { loadDownloadedFile(data['text'],data['tag_list'],data['link_list']); }
	});
	return true;
}

function selTxtUpFile() {
	var formData = new FormData();
	formData.append('file', $('#txt_upfile')[0].files[0]);
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		type : 'POST',
		processData: false,  // tell jQuery not to process the data
		contentType: false,  // tell jQuery not to set contentType
		cache: false,
		enctype: 'multipart/form-data',
		url: 'selTextUpFile',
		data: formData,
		success: function(data) { loadUploadedFile(data['text'],data['txt_fname'],data['file_list']); }
	});
	return true;
}

function saveTextTagging() {
	jreq = JSON.stringify({'txt_fname':txt_fname,'tag_list':tag_list,'link_list':link_list});
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		method : 'POST',
		url: 'saveTextTagging',
		data: {'jreq':jreq},
		success: function(data) {
			if (data['ok']) {alert('Text tagging saved successfully!');}
			else {alert('Text tagging NOT saved! Please verify if text was already loaded.');}
		}
	});
	return true;
}


// *** Executive Functions *** //

function loadDownloadedFile(downfile_text,downfile_tag_list,downfile_link_list) {
	text = downfile_text;
	tag_list = downfile_tag_list;
	link_list = downfile_link_list;
	loadInitialSets();
	return true;
}

function loadUploadedFile(upfile_text,upfile_name,upfile_list) {
	txt_fname = upfile_name;
	tag_list = [];
	link_list = [];
	text = upfile_text;
	file_list = upfile_list;
	loadInitialSets();
	return true;
}

function loadFileList() {
	var sel = document.getElementById("txt_downfile");
	sel.innerHTML='';
	if (txt_fname=='') {sel.innerHTML='<option disabled selected value> -- select an option -- </option>';}
	for (var i = 0; i < file_list.length; i++) {
		fname = file_list[i];
		var opt = document.createElement("option");
		opt.setAttribute("value", fname);
		opt.setAttribute("label", fname);
		//opt.setAttribute("text", fname);
		opt.innerHTML = fname.substring(0,50);
		if (fname==txt_fname) {opt.setAttribute("selected", true);}
		sel.appendChild(opt);
	}
	return true;
}

function loadTags() {
	var parent = document.getElementById("tags");
	parent.innerHTML = "";
	for (i=0; i<tag_list.length; i++) {
		var tag_text = tag_list[i];
		var clr = hlt_color[i%hlt_color.length];
		var div = makeTag(tag_text,i,clr);
		parent.appendChild(div);
	}
	return true;
}

function insertNewTag() {
	var tag_inpt = document.getElementById("tag_inpt");
	var tag_text = tag_inpt.value;
	tag_inpt.value = "";
	var tags = document.getElementById("tags");
	var clr_id = tag_list.length%hlt_color.length;
	var clr = hlt_color[clr_id];
	var div = makeTag(tag_text,tag_list.length,clr);
	var parent = document.getElementById("tags");
	parent.appendChild(div);
	tag_list.push(tag_text);
	return true;
}

function filterTags() {
	var txtarea = document.getElementById("txtarea");
    var tag_id = getTagId();
	filtered_link_list = [];
	for (var i=0; i<link_list.length; i++) {
		link = link_list[i];
		if (link[0]==tag_id) {filtered_link_list.push(link)}
	}
	filtered_link_list = completeLinks(filtered_link_list);
	loadArea(filtered_link_list);
	return true;
}

function loadTaggedText() {
	loadArea(link_list);
	return true;
}

function loadInitialSets() {
	loadFileList();
	loadTaggedText();
	loadTags();
	return true;
}
/*
function getCookie(cname) {
  var name = cname + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var ca = decodedCookie.split(';');
  for(var i = 0; i <ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}
*/