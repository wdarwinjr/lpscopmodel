// ***** FUNCTIONS *****

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

$body = $("body");
//var wait_icon = document.geElementById("waiting");
$(document).on({
    ajaxStart: function() { startWaiting(); },//$body.addClass("loading"); },
     ajaxStop: function() { endWaiting(); },//$body.removeClass("loading"); }    
});
function startWaiting() {
  var wait_icon = document.createElement('div');
  document.body.appendChild(wait_icon);
  wait_icon.id = 'wait_icon';
  wait_icon.classList.add('modal');
  //$body.addClass("loading");//document.geElementById("waiting").style.display='block';
}
function endWaiting() {
  var wait_icon = document.getElementById('wait_icon');
  document.body.removeChild(wait_icon);
  //$body.removeClass("loading");//document.geElementById("waiting").style.display='hidden';
}

function putLoader(div_id) {
  var loader = document.createElement('div');
  loader.innerHTML = 'XXXXXXXXXXXXX';//loader.classList.add('loader');
  loader.style = 'position:absolute;top:200px;left:550px;';
  var frame = document.getElementById('frame');
  frame.appendChild(loader);
}

function killLoader() {
  $('.loader').remove();
}

function addTable(parent_id,head_list,value_mtx) {
  var parent = document.getElementById(parent_id)
  parent.innerHTML = "";
  var tab = document.createElement("table");
  parent.appendChild(tab);
  tab.border = 1;
  tab.style = "font-size:10px;margin-left:auto;margin-right:auto;";
  var tr = document.createElement("tr");
  for (var j=0; j<head_list.length; j++) {
    var th = document.createElement("th");
    th.style = "text-align:center;padding:2px;background-color:#DDD;";
    th.innerHTML = head_list[j];
    tr.appendChild(th);
  }
  tab.appendChild(tr);
  for (var i=0; i<value_mtx.length; i++) {
    var tr = document.createElement("tr");
    for (var j=0; j<value_mtx[i].length; j++) {
      var td = document.createElement("td");
      tr.appendChild(td);
      td.id = parent_id+'_tab_'+i+'_'+j;
      td.style = "text-align:center;padding:2px;";
      td.innerHTML = value_mtx[i][j];
    }
    tab.appendChild(tr);
  }
}

function addMatrix(obj_id,head_list,value_mtx) {
  var mtx_head = [''];
  var new_mtx = [];
  for (var i=0; i<head_list.length; i++) {
    mtx_head.push(head_list[i]);
    var row = [head_list[i]];
    for (var j=0; j<value_mtx[i].length; j++) {
      row.push(value_mtx[i][j]);
    }
    new_mtx.push(row);
  }
  addTable(obj_id,mtx_head,new_mtx);
}

function addOptions(select_id,opt_list) {
  var select = document.getElementById(select_id);
  for (opt_text of opt_list) {
    var opt = document.createElement("option");
    opt.text = opt_text;
    opt.value = opt_text;
    select.appendChild(opt);
  }
}

function addChkBoxes(list,divboxes_id,chk_status='checked') {
  var cols_nr = 3;
  var divboxes = document.getElementById(divboxes_id);
  divboxes.innerHTML = '';
  for (var i=0; i<cols_nr; i++) {
    var div = document.createElement("div");
    div.id = divboxes_id+"_divbox"+i;
    div.classList.add("col-md-4");
    div.innerHTML = "";
    div.style="margin:0px;padding:0px;";
    divboxes.appendChild(div);
  }
  for (i=0; i<list.length; i++) {
    var cdv = document.createElement("div");
    cdv.style = "";
    var ipt = document.createElement("input");
    ipt.id = divboxes_id+"_chkbox"+i;
    ipt.type = "checkbox";
    ipt.style = "";
    ipt.value = list[i];
    if (chk_status=='checked') {ipt.checked=true;}
    var lbl = document.createElement("label");
    lbl.htmlFor = ipt.id;
    lbl.style = "font-size:8px;";
    lbl.innerHTML = list[i];
    cdv.appendChild(ipt);
    cdv.appendChild(lbl);
    var chk_div = document.getElementById(divboxes_id+"_divbox"+i%cols_nr);
    chk_div.appendChild(cdv);
  }
}

function addFigure(src,figwidth,figheight,obj_id) {
  var img = document.createElement('img');
  img.src = src;
  img.style = 'width:'+figwidth+'px;height:'+figheight+'px;text-align:center;cursor:pointer;';
  img.onclick = function () { window.open(src,'Image','width=600px,height=400px,resizable=1'); };
  var obj = document.getElementById(obj_id);
  obj.innerHTML = "";
  obj.appendChild(img);
}

function waitProcessing(exec_window,msg,task_id,waiting_function) {
  if (exec_window!=null) {
    var new_msg = 'Process id '+task_id+': ongoing processing, please wait.<br>'+msg;
    if (msg!='...') { exec_window.document.body.innerHTML = ''; }
    exec_window.document.write('<div style="font-size:10px;">'+new_msg+'</div>');
  }
  data = {};
  $.ajax({
    headers: { 'X-CSRFToken': csrftoken },
    method : 'POST',
    url: 'waitProcessing',
    data: data,
    success: function(data) {
      if (data['exec_status']=='done') {
        if (exec_window!=null) { exec_window.close(); }
        window[waiting_function]();
      }
      else {
        waitProcessing(exec_window,data['msg'],data['task_id'],waiting_function);
      }
    }
  });
  return true;
}
