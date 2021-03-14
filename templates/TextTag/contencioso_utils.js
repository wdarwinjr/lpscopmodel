// ***** FUNCTIONS *****

function getCookie(cname) {
  var name = cname + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var ca = decodedCookie.split(';');
  for(var i=0; i<ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0)==' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name)==0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

function validateUser() {
	var user = document.getElementById("user");
	var password = document.getElementById("password");
	data = {'user':user.value,'password':password.value};
	$.ajax({
		headers: { 'X-CSRFToken': csrftoken },
		method : 'POST',
		url: 'validateUser',
		data: data,
		success: function(data) {
			sessionStorage.setItem('user',user.value);
			sessionStorage.setItem('perfil',data['perfil']);
			enterSystem(data['perfil']);
			if ((data['perfil']=='desenvolvimento') || (data['perfil']=='divulgacao')) { alert('Login efetuado com sucesso!'); }
			else { alert('Acesso nao autorizado!'); }
		}
	});
}

function highlight_font(opcao,acao) {
	if(acao==1) { document.getElementById(opcao).style.color = "#110055"; }
	else { document.getElementById(opcao).style.color = "#5171AF"; }
}


function putQuadro(parent,quadro_id,quadro_dic) {
  var parent_width = $('#'+parent.id).width();
  var title_div = document.createElement("div");
  title_div.id = quadro_id+'_title';
  title_div.classList.add('quadro_title');
  var quadro_div = document.createElement("div");
  quadro_div.id = quadro_id;
  quadro_div.classList.add('quadro_div');
  var br1 = document.createElement("br");
  title_div.innerHTML = quadro_dic['name'];
  $('#'+quadro_id).width(parent_width-20);
  parent.appendChild(title_div);
  parent.appendChild(quadro_div);
  parent.appendChild(br1);
  return quadro_div;
}

function putFieldLine(parent,line_id,line_dic) {
  var line = document.createElement('div');
  parent.appendChild(line);
  line.id = line_id;
  line.classList.add('lin'+line.id.slice(-1));
  field_id_list = Object.keys(line_dic);
  field_content_list = Object.values(line_dic);
  for (var i=0; i<field_id_list.length; i++) {
    var field = document.createElement('span');
    line.appendChild(field);
    var field_id = line_id+'_'+field_id_list[i];
    var field_dic = field_content_list[i];
    field.id = field_id;
    if (field_id_list.length<4) { field.classList.add('field3_col'+(i+1)); }
    else { if (field_id_list.length==4) { field.classList.add('field4_col'+(i+1)); }
           else { field.classList.add('field5_col'+(i+1)); } }
    if (field_dic['type']=='field') {
        var lbl = document.createElement('label');
        field.appendChild(lbl);
        var ipt = document.createElement('input');
        field.appendChild(ipt);
        ipt.type = 'text';
        ipt.id = field_id+'_ipt';
        lbl.id = field_id+'_lbl';
        lbl.for = ipt.id;
        lbl.innerHTML = field_dic['name'];
        ipt.value = field_dic['content'];
        lbl.classList.add('lbl_col');
        ipt.classList.add('ipt_col');
    }
    else { if (field_dic['type']=='chkbox') { putChkbox(field,field_dic['name']); } }
  }
  return line;
}

function putTextarea(parent,textarea_id,textarea_dic) {
  var txa_div = document.createElement("div");
  parent.appendChild(txa_div);
  txa_div.classList.add('textarea');
  var ttl = document.createElement("div");
  txa_div.appendChild(ttl);
  ttl.classList.add('textarea_ttl');
  ttl.id = textarea_id+"_ttl";
  ttl.innerHTML = textarea_dic['name'];
  var txa = document.createElement("textarea");
  txa_div.appendChild(txa);
  txa.classList.add('textarea_txa');
  txa_div.id = textarea_id;
  txa.id = textarea_id+"_textarea";
  txa.value = textarea_dic['content'];
  return txa_div;
}

function putTable(parent,table_id,table_dic) {
  if (table_dic['orientation']=='vertical') { var tab_div = putVerticalTable(parent,table_id,table_dic); }
  else { var tab_div = putHorizontalTable(parent,table_id,table_dic); }
  return tab_div;
}

function putVerticalTable(parent,table_id,table_dic) {
  var header = table_dic['header'];
  var mtx = table_dic['matrix'];
  var new_mtx = [];
  for (var i=0; i<mtx.length; i++) {
    var row = [header[i]];
    for (var j=0; j<mtx[i].length; j++) {
      row.push(mtx[i][j]);
    }
    new_mtx.push(row);
  }
  header = [];
  mtx = new_mtx;
  var tab_div = document.createElement('div');
  parent.appendChild(tab_div);
  tab_div.classList.add('table_div');
  var tab = document.createElement("table");
  tab_div.appendChild(tab);
  tab.id = table_id
  tab.classList.add('table');
  var tab_head = document.createElement("tr");
  tab.appendChild(tab_head);
  for (var j=0; j<header.length; j++) {
    var hcell = document.createElement("th");
    tab_head.appendChild(hcell);
    var hcell_text = document.createTextNode(header[j]);
    hcell.appendChild(hcell_text);
    hcell.classList.add('table_hcell');
  }
  for (var i=0; i<mtx.length; i++) {
    var row = document.createElement("tr");
    tab.appendChild(row);
    var values = mtx[i];
    for (var j=0; j<values.length; j++) {
      var cell = document.createElement("td");
      row.appendChild(cell);
      if (j==0) { cell.classList.add('table_hcell'); }
      else { cell.classList.add('table_cell'); }
      var cell_elmt = document.createTextNode(values[j]);
      cell.appendChild(cell_elmt);
    }
  };
  return tab_div;
}

function putHorizontalTable(parent,table_id,table_dic) {
  var header = table_dic['header'];
  var mtx = table_dic['matrix'];
  var tab_div = document.createElement('div');
  parent.appendChild(tab_div);
  tab_div.classList.add('table_div');
  var tab = document.createElement("table");
  tab_div.appendChild(tab);
  tab.id = table_id
  tab.classList.add('table');
  var tab_head = document.createElement("tr");
  tab.appendChild(tab_head);
  for (var j=0; j<header.length; j++) {
    var hcell = document.createElement("th");
    tab_head.appendChild(hcell);
    var hcell_text = document.createTextNode(header[j]);
    hcell.appendChild(hcell_text);
    hcell.classList.add('table_hcell');
  }
  for (var i=0; i<mtx.length; i++) {
    var row = document.createElement("tr");
    tab.appendChild(row);
    var values = mtx[i];
    for (var j=0; j<values.length; j++) {
      var cell = document.createElement("td");
      row.appendChild(cell);
      cell.classList.add('table_cell');
      var cell_elmt = document.createTextNode(values[j]);
      cell.appendChild(cell_elmt);
    }
  };
  return tab_div;
}

function putChkbox(parent,label_text) {
  var chkbox = document.createElement("input");
  parent.appendChild(chkbox);
  var lbl = document.createElement("label");
  parent.appendChild(lbl);
  chkbox.id = parent.id+"_chkbox_box";
  chkbox.type = "checkbox";
  lbl.id = parent.id+"_chkbox_lbl";
  lbl.for = chkbox.id;
  lbl.innerHTML = label_text;
  lbl.classList.add('chkbox_lbl');
  chkbox.classList.add('chkbox_box');
  return parent;
}

function putAutotextSelection(parent,atx_html_id,atx_html_dic,atx_dic,chosen_id_list) {
  //var child_order = parent.childNodes.length+1;
  var atx = document.createElement("div");
  parent.appendChild(atx);
  atx.id = atx_html_id;
  atx.classList.add('atx');
  var option_list = Object.keys(atx_dic);
  var selected_text = atx_dic[option_list[0]];
  var sel = document.createElement("select");
  atx.appendChild(sel);
  sel.id = atx.id+"_sel";
  $(sel).change(function(){
    return showOptionText(atx.id,atx_dic); });
  var textarea = document.createElement("textarea");
  atx.appendChild(textarea);
  textarea.id = atx.id+"_textarea";
  var save_text = document.createElement("button");
  atx.appendChild(save_text);
  save_text.id = atx.id+"_save_text";
  save_text.type = "button";
  $(save_text).click(function(){
    return saveNovoAutotexto(atx.id); });
  var ins = document.createElement("button");
  atx.appendChild(ins);
  ins.id = atx.id+"_ins";
  ins.type = "button";
  $(ins).click(function(){
    return insertOptionInDiv(atx.id); });
  var chosen = document.createElement("div");
  atx.appendChild(chosen);
  chosen.id = atx.id+"_chosen";
  var chosen_str = "";
  for (var i=0; i<chosen_id_list.length; i++) {
    chosen_str = chosen_str+','+option_list[chosen_id_list[i]];
  }
  for (var i=0; i<option_list.length; i++) {
    var opt = document.createElement("option");
    opt.value = option_list[i];
    opt.innerHTML = option_list[i];
    sel.appendChild(opt);
  }
  textarea.innerHTML = selected_text;
  save_text.innerHTML = atx_html_dic['save_text']['name'];
  ins.innerHTML = atx_html_dic['insert']['name'];
  chosen.innerHTML = chosen_str;
  //atx.classList.add('div_lin'+child_order);
  sel.classList.add('atx_sel');
  textarea.classList.add('atx_textarea');
  save_text.classList.add('atx_save_text');
  ins.classList.add('atx_ins');
  chosen.classList.add('atx_chosen');
  return {'sel':sel,'textarea':textarea,'ins':ins,'save_text':save_text,'chosen':chosen};
}
function showOptionText(parent_id,autotexto_dic) {
  var sel = document.getElementById(parent_id+'_sel');
  var textarea = document.getElementById(parent_id+'_textarea');
  var idx = sel.selectedIndex;
  textarea.innerHTML = autotexto_dic[sel.options[idx].value];
}
function insertOptionInDiv(parent_id) {
  var sel = document.getElementById(parent_id+"_sel");
  var chosen_div = document.getElementById(parent_id+"_chosen");
  var chosen_list = chosen_div.innerHTML.split(',');
  var idx = sel.selectedIndex;
  var option = sel.options[idx].value;
  chosen_list.push(option);
  chosen_div.innerHTML = chosen_list.toString();
}
function saveNovoAutotexto(parent_id) {
  var textarea = document.getElementById(parent_id+'_textarea');
  alert(textarea.value);
}
function getListFromText(text) {
    var list = text.split(',');
    return list;
}


function putTreeView(parent,tree_dic,click_function) {
    var ul = document.createElement('ul');
    parent.appendChild(ul);
    ul.id = 'myTreeView';
    for (var key in tree_dic) {
        var list = tree_dic[key];
        var li = document.createElement('li');
        ul.appendChild(li);
        var sub_spn = document.createElement('span');
        li.appendChild(sub_spn);
        sub_spn.classList.add('tree_branch');
        sub_spn.innerHTML = key;
        var sub_ul = document.createElement('ul');
        li.appendChild(sub_ul);
        sub_ul.classList.add('nested');
        for (var i=0; i<list.length; i++) {
            var val = list[i];
            var sub_li = document.createElement('li');
            sub_ul.appendChild(sub_li);
            sub_li.id = val;
            sub_li.innerHTML = val;
            sub_li.classList.add('tree_leaf');
            sub_li.onclick = function () { click_function(this); }
        }
    }
    var toggler = document.getElementsByClassName("tree_branch");
    var i;
    for (i=0; i<toggler.length; i++) {
      toggler[i].addEventListener("click", function() {
        this.parentElement.querySelector(".nested").classList.toggle("active");
        //this.classList.toggle("caret-down");
      });
    }
    return ul;
}

function putAcervoTab(tab_dic,items_nr,parent_id) {
    var parent = document.getElementById(parent_id);
    if (items_nr==0) {
      alert('Base de dados vazia!');
      return true;
    }
    var col_list = Object.keys(tab_dic);
    var tab_length = tab_dic[col_list[0]].length;
    var title = document.createElement('div');
    parent.appendChild(title);
    title.style = 'font-size:14px;font-weight:bold; margin:10px;';
    title.innerHTML = 'Numero de itens: '+items_nr+' (mostrando apenas os '+tab_length+' primeiros)';
    var tab = document.createElement('table');
    parent.appendChild(tab);
    tab.style = 'margin:auto;';
    var tr = document.createElement('tr');
    tab.appendChild(tr);
    for (i=0; i<col_list.length; i++) {
        col = col_list[i];
        var td = document.createElement('td');
        tr.append(td);
        td.style = 'font-size:14px;font-weight:bold;text-align:center;border:solid 1px;color:navy;background-color:yellow;';
        td.innerHTML = col;
    }
    for (i=0; i<tab_length; i++) {
        var tr = document.createElement('tr');
        tab.appendChild(tr);
        for (j=0; j<col_list.length; j++) {
            col = col_list[j];
            var td = document.createElement('td');
            tr.append(td);
            td.style = 'font-size:10px;border:solid 1px;text-align:center;margin:0px;padding:0px;';
            var val = String(tab_dic[col][i]);
            if (val.length>20) { val = val.substring(0,20)+'...'; }
            td.innerHTML = val;
        }
    }
}

function putChkboxTable(tab_dic,items_nr,parent_id) {
    var parent = document.getElementById(parent_id);
    if (items_nr==0) {
      alert('Base de dados vazia!');
      return true;
    }
    var col_list = Object.keys(tab_dic);
    var tab_length = tab_dic[col_list[0]].length;
    var title = document.createElement('div');
    parent.appendChild(title);
    title.style = 'font-size:14px; font-weight:bold; margin:10px;';
    title.innerHTML = 'Numero de itens: '+items_nr+' (mostrando apenas os '+tab_length+' primeiros)';
    var tab_div = document.createElement('div');
    parent.appendChild(tab_div);
    tab_div.style = 'margin:auto; width:95%; height:85%; overflow:auto;';
    var tab = document.createElement('table');
    tab_div.appendChild(tab);
    tab.id = parent_id+'_tab';
    var tr = document.createElement('tr');
    tab.appendChild(tr);
    var td = document.createElement('td');
    tr.append(td);
    td.style = 'font-size:14px;font-weight:bold;text-align:center;border:solid 1px;color:navy;background-color:yellow;';
    td.innerHTML = 'check';
    for (i=0; i<col_list.length; i++) {
        col = col_list[i];
        var td = document.createElement('td');
        tr.append(td);
        td.style = 'font-size:14px;font-weight:bold;text-align:center;border:solid 1px;color:navy;background-color:yellow;';
        td.innerHTML = col;
    }
    for (i=0; i<tab_length; i++) {
        var tr = document.createElement('tr');
        tab.appendChild(tr);
        var td = document.createElement('td');
        tr.append(td);
        td.style = 'font-size:10px;border:solid 1px;text-align:center;margin:0px;padding:0px;';
        var cell_elmt = document.createElement('input');
        td.appendChild(cell_elmt);
        cell_elmt.id = parent.id+"_chkbox_box"+i;
        cell_elmt.type = "checkbox";
        cell_elmt.classList.add('chkbox_box');
        for (j=0; j<col_list.length; j++) {
            col = col_list[j];
            var td = document.createElement('td');
            tr.append(td);
            td.style = 'font-size:10px;border:solid 1px;text-align:center;margin:0px;padding:0px;';
            var val = tab_dic[col][i];
            td.innerHTML = val;
        }
    }
}

function putDropbox(parent_id,sel_id,title,opt_list) {
    var parent = document.getElementById(parent_id);
    var div = document.createElement('div');
    parent.appendChild(div);
    div.style = 'width:95%;margin:2px;';
    var label = document.createElement('label');
    div.appendChild(label);
    label.id = sel_id+'_lbl';
    label.innerHTML = title;
    var sel = document.createElement('select');
    div.appendChild(sel);
    sel.id = sel_id;
    sel.style = 'width:95%';
    for (var i=0; i<opt_list.length; i++) {
        var opt = document.createElement('option');
        sel.appendChild(opt);
        opt.value = opt_list[i];
        var val = String(opt_list[i]);
        if (val.length>20) { val = val.substring(0,20)+'...'; }
        opt.innerHTML = val;
    }
    return sel;
}

function putButton(parent_id,title) {
    var parent = document.getElementById(parent_id);
    var btn = document.createElement('button');
    parent.appendChild(btn);
    btn.style = 'margin:auto;';
    btn.innerHTML = title;
    return btn;
}
    
function putFileImportForm(parent_id,import_file_id) {
    var parent = document.getElementById(parent_id);
    var div = document.createElement('div');
    parent.appendChild(div);
    div.style = 'margin:auto;width:130px;height:60px;border:solid navy 1px;';
    var lbl = document.createElement('label');
    div.appendChild(lbl);
    lbl.style = 'text-align:left;width:110px;height:18px;font-size:10px;';
    lbl.innerHTML = 'nenhum arquivo selec.';
    lbl.for = import_file_id;
    var ipt = document.createElement('input');
    div.appendChild(ipt);
    ipt.id = import_file_id;
    ipt.type = 'file';
    ipt.onchange = function() { lbl.innerHTML = ipt.value.substring(12,32)+'...'; };
    ipt.style.display = 'none';
    var browse_btn = document.createElement('button');
    div.appendChild(browse_btn);
    browse_btn.onclick = function() { ipt.click(); };
    browse_btn.style = 'width:75px;height:25px;margin:2px;';
    browse_btn.innerHTML = 'Browse';
    var btn = document.createElement('button');
    div.appendChild(btn);
    btn.id = import_file_id+'_btn';
    btn.style = 'width:35px;height:25px;margin:2px;';
    btn.innerHTML = 'OK';
    return btn;
}

function importFile(ipt_id,url,success_function) {
    var ipt = document.getElementById(ipt_id);
    var file = ipt.files[0];
    var formData = new FormData();
    formData.append('file', file);
    $.ajax({
        headers: { 'X-CSRFToken': csrftoken },
        type : 'POST',
        processData: false,  // tell jQuery not to process the data
        contentType: false,  // tell jQuery not to set contentType
        cache: false,
        enctype: 'multipart/form-data',
        url: url,
        data: formData,
        success: function(data) {
            success_function(data);
        }
    });
}

function putSelectionGrid(parent_id,feature_dic,sel_function) {
    var div = document.createElement('div');
    document.getElementById(parent_id).appendChild(div);
    div.id = parent_id+'_selgrid';
    div.style = 'height:500px; overflow-y:auto; text-align:left; width:120px;';
    var feature_name_list = Object.keys(feature_dic);
    for (var i=0; i<feature_name_list.length; i++) {
        var feature = feature_name_list[i];
        var value_list = feature_dic[feature];
        var sel = putDropbox(div.id,feature,feature,value_list);
    }
    var btn = putButton(parent_id,'Carrega processos');
    btn.onclick = function() { sel_function(); };
}




/******************************* OLD FUNCTIONS ***********************************

function putQuadro(parent,quadro_id,quadro_title,w,h,align_str,quadro_href='index.html') {
  var title_div = document.createElement("div");
  title_div.style="margin:5px;text-align:"+align_str+";font-weight:bold;";
  title_div.innerHTML = '<a href="'+quadro_href+'">'+quadro_title+'</a>';
  var div = document.createElement("div");
  div.id = quadro_id;
  div.style="width:"+w+"px;border:solid 1px;margin-left:5px;background-color:#FFF;padding:10px;position:relative;";
  var br1 = document.createElement("br");
  parent.appendChild(title_div);
  parent.appendChild(div);
  parent.appendChild(br1);
}
function putFieldLine(parent,var_label,var_value,w_list,weight_str) { //,lista_texto
  var div = document.createElement('div');
  //div.id = parent.id+'_div';
  div.style = 'height:30px;margin:10px;';
  var_width = 900/var_label.length;
  for (var i=0; i<var_label.length; i++) {
    var sdv = document.createElement('span');
    sdv.style = 'margin:5px;width:'+w_list[i]+'px;height:20px;font-size:12px;border:solid 0px;display:inline-block;';
    var ipt = document.createElement('input');
    ipt.id = parent.id+'_'+var_label[i]+'_ipt';
    ipt.type = 'text';
    ipt.value = var_value[i];
    ipt.style = 'margin:5px;font-weight:'+weight_str+';';
    var lbl = document.createElement('label');
    lbl.id = parent.id+'_'+var_label[i]+'_lbl';
    lbl.for = ipt.id;
    lbl.innerHTML = var_label[i];
    lbl.style = 'margin:5px;font-weight:'+weight_str+';';
    //if (lbl_id=='proc_id_lbl1') { lbl.title = help[lbl_id]; }
    //lbl.onmouseover = labelHover(this);
    sdv.appendChild(lbl);
    sdv.appendChild(ipt);
    div.appendChild(sdv);
  }
  parent.appendChild(div);
}
function putTextArea(parent,title,text,id) {
  var div = document.createElement("div");
  div.id = id+"_ttl";
  div.style = "text-align:left;";
  var ttl = document.createElement("div");
  ttl.innerHTML = title;
  ttl.style = "margin:auto;font-size:14px;font-weight:bold;";
  var txa = document.createElement("textarea");
  txa.id = id+"_textarea";
  txa.value = text;
  txa.style = "margin:auto;margin-bottom:15px;font-size:12px;width:1200px;";
  div.appendChild(ttl);
  div.appendChild(txa);
  parent.appendChild(div);
}
function putTable(parent,head,mtx,style_str="border:solid 1px;margin:auto;padding:10px;") {
  var tab = document.createElement("table");
  tab.style = style_str;
  var tab_head = document.createElement("tr");
  for (var j=0; j<head.length; j++) {
    var hcell = document.createElement("th");
    hcell.style = "border:solid 1px;padding:5px;";
    var hcell_text = document.createTextNode(head[j]);
    hcell.appendChild(hcell_text);
    tab_head.appendChild(hcell);
  }
  tab.appendChild(tab_head);
  for (var i=0; i<mtx.length; i++) {
    var row = document.createElement("tr");
    var values = mtx[i];
    for (var j=0; j<values.length; j++) {
      var cell = document.createElement("td");
      if (j>0) {
        cell.style = "border:solid 1px;text-align:right;padding:5px;";
      }
      else {
        cell.style = "border:solid 1px;padding:5px;";
      }
      var cell_elmt = document.createTextNode(values[j]);
      cell.appendChild(cell_elmt);
      row.appendChild(cell);
    }
    tab.appendChild(row);
  };
  parent.appendChild(tab);
}
function putChkbox(parent,label_text) {
  var spn = document.createElement("span");
  spn.style = "margin-left:5px;font-size:12px;width:100px;";
  var chkbox = document.createElement("input");
  var lbl = document.createElement("label");
  chkbox.id = "tempestividade";
  chkbox.type = "checkbox";
  lbl.for = "tempestividade";
  lbl.innerHTML = label_text;
  spn.appendChild(lbl);
  spn.appendChild(chkbox);
  parent.appendChild(spn);
}
function putAutotextSelection(parent_div,autotexto_dic) {
  var option_list = Object.keys(autotexto_dic);
  var text_list = Object.values(autotexto_dic);
  var sel = document.createElement("select");
  sel.id = parent_div.id+"_sel";
  sel.style = "width:300px;";
  for (var i=0; i<option_list.length; i++) {
    var opt = document.createElement("option");
    opt.value = option_list[i];
    opt.innerHTML = option_list[i];
    //opt.onmouseover = function() { alert("OK"); };
    sel.appendChild(opt);
  }
  parent_div.appendChild(sel);
  var textarea = document.createElement("textarea");
  textarea.id = parent_div.id+"_textarea";
  textarea.style = "width:840px;";
  textarea.innerHTML = autotexto_dic[option_list[0]];
  parent_div.appendChild(textarea);
  var ins = document.createElement("button");
  ins.type = "button";
  ins.id = parent_div.id+"_ins";
  ins.innerHTML = "Inserir";
  ins.style = "";
  parent_div.appendChild(ins);
  var chosen_div = document.createElement("div");
  chosen_div.id = parent_div.id+"_chosen";
  chosen_div.style = "border:solid 1px;height:30px;";
  chosen_div.innerHTML = "";
  parent_div.appendChild(chosen_div);
}
**************************************************************************/