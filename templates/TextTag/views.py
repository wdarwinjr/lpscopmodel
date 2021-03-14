from django.shortcuts import render
from django.http import JsonResponse#,HttpResponse
from .models import Processo,Lote,Documento,Autotexto,Rotulo
from .models import ProcToLot,ProcToDoc,ProcToRot
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from .modules import contencioso_utils as ctut
#from .modules import ia_rotuling as iar

import os
import shutil
import json
import numpy as np
import pandas as pd
from odf.opendocument import load,OpenDocumentText
from odf.style import Style,ParagraphProperties,TextProperties
from odf.text import H,P,Span
from odf import teletype
#import chardet
#import string
#import re


########################################################
### **************** GLOBAL VARIABLES ************** ###
########################################################

proj_dir = os.path.abspath('.')
app_dir = proj_dir+'/contencioso_app/'
data_dir = proj_dir+'/static/data/'
multa_comp_dir = data_dir+'multa_compensacao/'
fixed_comp_dir = multa_comp_dir+'compactados/'
fixed_descomp_dir = multa_comp_dir+'descompactados/'
fixed_done_dir = multa_comp_dir+'done/'
fixed_cred_comp_dir = multa_comp_dir+'cred_compactados/'
fixed_cred_descomp_dir = multa_comp_dir+'cred_descompactados/'
fixed_cred_done_dir = multa_comp_dir+'cred_done/'
acordao_modelo_odt = multa_comp_dir+'MultaCompIndevida_Acordao_teste - MODELO.odt'
acordao_produzido_odt = multa_comp_dir+'MultaCompIndevida_Acordao_teste.odt'
proc_feature_dic = {'proc_nr':'Nro Proc.','interessado':'Nome','act_origem':'ACT_Orig.',\
'act_tributo':'ACT_Trib.','act_tema':'ACT_Tema','infracao':'Infração','ni':'NI Contrib.',\
'unidade':'Unidade','equipe':'Equipe','apensado':'Proc. Apens.','situacao':'Situação',\
'confirmed':'Marca','he':'HE','protocolo_data':'Data Prot.','val_origin':'Valor Orig.',\
'val_proc':'Valor Proc.','drj_sessao_data':'Sessão DRJ','drj_relator':'Relator DRJ',\
'carf_sessao_data':'Sessão CARF','carf_relator':'Relator CARF',\
'julgamento_tipo':'Tipo Julg.','julgamento_dado':'Dados Julg.'}
proc_feature_header = list(proc_feature_dic.values())
# colunas do tabelão que importa processos
import_feature_list = ['proc_nr','unidade','act_tema','act_origem','act_tributo',\
                       'protocolo_data','drj_sessao_data','he','apensado','infracao',\
                       'ni','interessado','equipe','drj_relator','carf_relator','situacao',\
                       'val_origin','val_proc']
import_feature_header = [proc_feature_dic[f] for f in import_feature_list]
# fitros na lateral_div
filter_feature_list = ['proc_nr','act_origem','act_tributo','act_tema','infracao','ni',\
                       'unidade','equipe','apensado','situacao','confirmed']
filter_feature_header = [proc_feature_dic[f] for f in filter_feature_list]
processo_filtering_df = None
import_data_dic = None

gc_entraProcessos = 'Os processos apresentados são os que já estão na base de dados.\n\nEntrada de Processos pelo Julgador: O julgador deve gerar no e-Processo um relatório gerencial. 1. Entrar no e-processo>"Gerencial"... e criar um relatório com os seguintes campos: [Número Processo,...]. Esse relatório deve ser executado e salvo no formato csv para depois ser importado aqui na SCAI.';


########################################################
### ******************** VIEWS ********************* ###
########################################################


################################
### PORTAL/SUITE CONTENCIOSO ###
################################

def index(request):
    context = {}
    return render(request, 'portal.html', context)

def validateUser(request):
    user,password = request.POST['user'],request.POST['password']
    if (user=='contencioso' and password=='contencioso'):
        perfil = 'desenvolvimento'
    elif (user=='acervo' and password=='acervo123'):
        perfil = 'acervo'
    elif (user=='julgador' and password=='julgador123'):
        perfil = 'julgador'
    elif (user=='gestor' and password=='gestor123'):
        perfil = 'gerencial'
    elif (user=='divulga' and password=='divulga123'):
        perfil = 'divulgacao'
    elif (user=='asd' and password=='asd'):
        perfil = 'desenvolvimento'
    else:
        perfil = 'convidado'
    request.session['perfil'] = perfil
    resp = {'perfil':perfil}
    return JsonResponse(resp)

def doSuiteAction(request):
    data = request.POST
    genus = data['action_genus']
    species = data['action_species']
    global processo_filtering_df
    processo_filtering_df = pd.DataFrame.from_records(Processo.objects.all().values(*filter_feature_list))
    resp = {'action_genus':genus,'action_species':species}
    if (genus=='acervo'):
        if (species=='processo'): dados = {'gc_entraProcessos':gc_entraProcessos}
        if (species=='agrupamento'):
            tab_dic,items_nr = getProcessesDic({})
            dados = {'proc_tree_dic':getProcTreeFromFilter({}),'tab_dic':tab_dic,'items_nr':items_nr} #getProcessFeatureDic(processo_filtering_df)
        if (species=='dados'): dados = {'proc_tree_dic':getProcTreeFromFilter({})} #getProcessFeatureDic(processo_filtering_df) #dados = {'proc_tree_dic':getProcTreeFromFilter({})}
        if (species=='autotexto'): dados = {}
        if (species=='rotulo'): dados = getRotulesDB()
    if (genus=='julgamento'):
        if (species=='MultaCompNH'): dados = getPageInit_MultaCompNH(data)
        if (species=='COMEX'): dados = getPageInit_COMEX(data)
        if (species=='MalhaIRPF'): dados = getPageInit_MalhaIRPF(data)
        if (species=='MAED_DCTF'): dados = getPageInit_MAED_DCTF(data)
        if (species=='Simples'): dados = getPageInit_Simples(data)
    if (genus=='conhecimento'):
        if (species=='sisvin'): dados = {'link':'http://10.61.12.57/sisvin/consulta.php'} #resp['link']=
        if (species=='administrativo'): dados = {'link':'http://10.61.12.57/diaja/analise_pesquisa.php'} #resp['link']=
        if (species=='judicial'): dados = {'link':'http://10.61.12.57/diajubol/boletim_pesquisa.php'} #resp['link']=
        if (species=='gerencial'): dados = {'link':'http://10.61.12.57/temas/temas_pesquisa.php'} #resp['link']=
    if (genus=='gerencial'):
        if (species=='gerencial1'): dados = getPageInit_gerencial1(data)
        if (species=='gerencial2'): dados = getPageInit_gerencial2(data)
        if (species=='gerencial3'): dados = getPageInit_gerencial3(data)
        if (species=='gerencial4'): dados = getPageInit_gerencial4(data)
    for key,value in dados.items():
        resp[key] = value
    return JsonResponse(resp)


#####################################################################
###  Business Process Specific AJAX Functions (for implementing)  ###
#####################################################################

### ENTRADA PROCS ###

def showProcessesDB(request):
    #tipo = request.POST['tipo']
    tab_dic,items_nr = getProcessesDic({})
    resp = {'tab_dic':tab_dic,'items_nr':items_nr}
    return JsonResponse(resp)

def importCsvProcs(request):
    global import_data_dic
    inmemory_file = request.FILES['file']
    upfile = File(inmemory_file)
    import_data_dic,tab_dic,items_nr = ctut.getImportDic(upfile,import_feature_header)
    resp = {'tab_dic':tab_dic,'items_nr':items_nr}
    return JsonResponse(resp)

def importDataToDB(request):
    #tipo = request.POST['tipo']
    #qtt = request.POST['qtt']
    #if (qtt=='todos'): items_nr = len(dic['Número_Processo'])
    #else: items_nr = min(len(dic['Número_Processo']),int(qtt))
    dic = import_data_dic
    header = import_feature_header
    items_nr = len(dic[header[0]])
    for p_id in range(items_nr):
        proc_nr = dic[header[0]][p_id]
        if (Processo.objects.filter(proc_nr=proc_nr).count()==0):
            p = Processo(proc_nr=dic[header[0]][p_id],\
                unidade=dic[header[1]][p_id],\
                act_tema=dic[header[2]][p_id],\
                act_origem=dic[header[3]][p_id],\
                act_tributo=dic[header[4]][p_id],\
                protocolo_data=dic[header[5]][p_id],\
                drj_sessao_data=dic[header[6]][p_id],\
                he=dic[header[7]][p_id],\
                apensado=dic[header[8]][p_id],\
                infracao=dic[header[9]][p_id],\
                ni=dic[header[10]][p_id],\
                interessado=dic[header[11]][p_id],\
                equipe=dic[header[12]][p_id],\
                drj_relator=dic[header[13]][p_id],\
                carf_relator=dic[header[14]][p_id],\
                situacao=dic[header[15]][p_id],\
                val_origin=dic[header[16]][p_id],\
                val_proc=dic[header[17]][p_id])
                ##carf_sessao_data=dic[header[]][p_id],\
            p.save()
            if (Lote.objects.filter(nome='Sem_Lote').count()==0):
                l = Lote(nome='Sem_Lote')
                l.save()
            else: l = Lote.objects.get(nome='Sem_Lote')
            pl = ProcToLot(proc_id=p.id,lot_id=l.id)
            pl.save()
    global processo_filtering_df
    processo_filtering_df = pd.DataFrame.from_records(Processo.objects.all().values(*filter_feature_list))
    tab_dic,items_nr = getProcessesDic({})
    resp = {'tab_dic':tab_dic,'items_nr':items_nr}
    return JsonResponse(resp)


### AGRUPAMENTO PROCS ###

def getSelectedProcs(request):
    post_filter_dic = json.loads(request.POST.get('filter_dic'))
    filter_dic = {}
    for key,val in post_filter_dic.items():
        if (val!='todos'): filter_dic[key] = val
    tab_dic,items_nr = getProcessesDic(filter_dic)
    resp = {'tab_dic':tab_dic,'items_nr':items_nr}
    return JsonResponse(resp)

def makeProcessLot(request):
    lot_proc_list = json.loads(request.POST.get('lot_proc_list'))
    lot_name = request.POST['lot_name']
    l = Lote(nome=lot_name)
    l.save()
    for p_nr in lot_proc_list:
        p = Processo.objects.get(proc_nr=p_nr)
        pl = ProcToLot(lot_id=l.id,proc_id=p.id)
        pl.save()
    resp = {'proc_tree_dic':getProcTreeFromFilter({})}
    return JsonResponse(resp)    


### COLETA DADOS ###

def getSelectedProcLots(request):
    post_filter_dic = json.loads(request.POST.get('filter_dic'))
    proc_tree_dic = getProcTreeFromFilter(post_filter_dic)
    resp = {'proc_tree_dic':proc_tree_dic}
    return JsonResponse(resp)

def getProcTreeFromFilter(post_filter_dic):
    filter_dic = {}
    for key,val in post_filter_dic.items():
        if (val!='todos'): filter_dic[key] = val
    complete_tab_dic,items_nr = getProcessesDic(filter_dic)
    proc_nr_list = complete_tab_dic[proc_feature_dic['proc_nr']]
    proc_tree_dic = getProcTreeFromProcList(proc_nr_list)
    return proc_tree_dic

def makeProcList(request):
    if (request.POST['tipo']=='lote'):
        lot_name = request.POST['dado']
        l = Lote.objects.get(nome=lot_name)
        pls = ProcToLot.objects.filter(lot_id=l.id)
        proc_nr_list = []
        for pl in pls:
            p = Processo.objects.get(id=pl.proc_id)
            proc_nr_list.append(p.proc_nr)
    else: proc_nr_list = [request.POST['dado']]
    df = pd.DataFrame(data={'proc_nr_list': proc_nr_list})
    df.to_csv('proc_nr_list.txt', sep='\n',index=False)
    resp = {}
    return JsonResponse(resp)

def getProcListData(request):
    proc_tipo = 'MultaCompNH' ### GENERALIZAR!!!!
    if (request.POST['tipo']=='lote'):
        lot_name = request.POST['dado']
        l = Lote.objects.get(nome=lot_name)
        pls = ProcToLot.objects.filter(lot_id=l.id)
        proc_nr_list = []
        for pl in pls:
            p = Processo.objects.get(id=pl.proc_id)
            proc_nr_list.append(p.proc_nr)
    else: proc_nr_list = [request.POST['dado']]
    proc_cred_list = []
    for proc_nr in proc_nr_list:
        julgamento_dado = getProcData(proc_tipo,proc_nr)
        proc_cred_list.append(julgamento_dado['dados']['proc_credito'])
        p = Processo.objects.get(proc_nr=proc_nr)
        p.julgamento_dado = json.dumps(julgamento_dado)
        p.save()
    df = pd.DataFrame(data={'proc_cred_list': proc_cred_list})
    df.to_csv('proc_cred_list.txt', sep='\n',index=False)
    resp = {'julgamento_dado':julgamento_dado,'proc_nr_list':proc_nr_list,'proc_cred_list': proc_cred_list} ### GENERALIZAR!!!!
    return JsonResponse(resp)

def getProcCredListData(request):
    proc_tipo = 'ProcCred' ### GENERALIZAR!!!!
    proc_dic = json.loads(request.POST['proc_dic'])
    for proc_nr,proc_cred in proc_dic.items():
        try:
            p = Processo.objects.get(proc_nr=proc_cred)
        except ObjectDoesNotExist:
            p = Processo(proc_nr=proc_cred)
            p.save()
        cred_julgamento_dado = getProcData(proc_tipo,proc_cred)
        p.julgamento_dado = json.dumps(cred_julgamento_dado)
        p.save()
        p = Processo.objects.get(proc_nr=proc_nr)
        main_julgamento_dado = json.loads(p.julgamento_dado)
        main_julgamento_dado['proc_cred_dado'] = cred_julgamento_dado
        p.julgamento_dado = json.dumps(main_julgamento_dado)
        p.save()
    resp = {'proc_cred_dado':cred_julgamento_dado}
    return JsonResponse(resp)

### CARGA AUTOTEXTOS ###

def importAutotextos(request):
    inmemory_file = request.FILES['file']
    upfile = File(inmemory_file)
    txt_upfile = upfile.open(mode='r')
    text = txt_upfile.read()
    text = text.decode(encoding='utf-8') #.encode('iso-8859-1')
    atxs = Autotexto.objects.all()
    antes_nr = atxs.count()
    #atx_file = multa_comp_dir+'Autotextos.txt'
    autotextos = ctut.getAutotextos(text)
    atxs = Autotexto.objects.all()
    for a in autotextos:
        if (Autotexto.objects.filter(nome=a['nome']).count()==0):
            atx = Autotexto(nome=a['nome'], texto=a['texto'], capitulo=a['capitulo'], tema=a['tema'] ,autor=a['autor'])
            atx.save()
    atxs = Autotexto.objects.all()
    depois_nr = atxs.count()
    resp = {'antes_nr':antes_nr,'depois_nr':depois_nr,'texto':atxs[0].texto}
    return JsonResponse(resp) 


### ROTULAGEM E APRENDIZADO ATIVO ###

def importRotules(request):
    inmemory_file = request.FILES['file']
    upfile = File(inmemory_file)
    txt_upfile = upfile.open(mode='r')
    text = txt_upfile.read()
    text = text.decode(encoding='iso-8859-1').encode('utf-8')
    dados = populateRotuloDB()
    prob_dados = getRotuleProbList()
    dados.update(prob_dados)
    resp = dados
    return JsonResponse(resp)

def makeRotule(request):
    rot_name = request.POST['rot_name']
    dados = insertRotule(rot_name)
    resp = dados
    return JsonResponse(resp)
    

def loadRotuleProcessView(request):
    rot_text = request.POST['rot_text']
    dados = getRotuleProcessView(rot_text)
    resp = dados
    return JsonResponse(resp)

def selectProc(request):
    req = json.loads(request.POST['jreq'])
    proc_now_nr = req['proc_now']
    processo_df = pd.DataFrame.from_records(Processo.objects.all().values('id','proc_nr','confirmed'))
    proc_rot_df = pd.DataFrame.from_records(ProcToRot.objects.all().values('proc_id','rot_id','prob','confirmed','user'))
    rotulo_df = pd.DataFrame.from_records(Rotulo.objects.all().values('id','nome'))
    proc_now_id = processo_df[processo_df['nr']==proc_now_nr].iloc[0]['id']
    p_r_id_list,p_r_text_list,p_r_prob_list,p_r_state_list = ctut.getProcRotules(proc_now_id,rotulo_df,proc_rot_df)
    resp = {
      'proc_now_id':proc_now_id,
      'proc_now_nr':proc_now_nr,
      'p_r_id_list':p_r_id_list,
      'p_r_text_list':p_r_text_list,
      'p_r_prob_list':p_r_prob_list,
      'p_r_state_list':p_r_state_list,
    }
    return JsonResponse(resp)

def saveProc(request):
    req = json.loads(request.POST['jreq'])
    proc_now = req['proc_now']
    rot_okk_list = req['rot_okk_list']
    rot_nok_list = req['rot_nok_list']
    user = request.session['user']
    confirmRotules(proc_now,rot_okk_list,rot_nok_list,user)
    resp = {}
    return JsonResponse(resp)


### FORM JAP "MultaCompNH" ###

def getProcForm_MultaCompNH(request):
    proc_nr = request.POST['proc_nr']
    p = Processo.objects.get(proc_nr=proc_nr)
    julgamento_dado = p.julgamento_dado
    resp = {'julgamento_dado':json.loads(julgamento_dado)}
    return JsonResponse(resp)



###########################################################################
###  Business Process Specific Processing Functions (for implementing)  ###
###########################################################################

def getProcessFeatureDic(processo_df):
    feature_dic = {}
    for c in processo_df.columns:
        col = list(set(processo_df[c]))[:5]
        feature_dic[c] = ['todos']+sorted(col)
    dados = {'feature_dic':feature_dic}
    return dados

def getProcData(proc_tipo,proc_nr):
    #if (proc_tipo=='MultaCompNH'): julgamento_dado = getProcData_MultaCompNH(proc_main)
    #elif (proc_tipo=='ProcCred'): julgamento_dado = getProcCredData_MultaCompNH(proc_main,proc_vinc)
    if (proc_tipo=='MultaCompNH'): comp_dir,descomp_dir,done_dir = fixed_comp_dir,fixed_descomp_dir,fixed_done_dir
    elif (proc_tipo=='ProcCred'): comp_dir,descomp_dir,done_dir = fixed_cred_comp_dir,fixed_cred_descomp_dir,fixed_cred_done_dir
    loadDocsToDB(proc_nr,comp_dir,descomp_dir,done_dir)
    julgamento_dado = treatProcText(proc_tipo,proc_nr)
    return julgamento_dado

def getRotulesDB():
    tab_dic,items_nr = getRotulesDic()
    dados = {'tab_dic':tab_dic,'items_nr':items_nr}
    return dados

def insertRotule(rot_name):
    r = Rotulo(nome=rot_name)
    r.save()
    tab_dic,items_nr = getRotulesDic()
    dados = {'tab_dic':tab_dic,'items_nr':items_nr}
    return dados

def populateRotuloDB(origin='csv'):
    rs = Rotulo.objects.all()
    antes = rs.count()
    rs.delete()
    if (origin=='csv'): importRotulingFromCsv()
    #elif (origin=='ia'): iar.runIARotuling()
    #elif (origin=='toy'): populateProcRotuleDB_Toy()
    depois = Rotulo.objects.all().count()
    dados = {'antes':antes,'depois':depois}
    return dados

def importRotulingFromCsv():
    rotulos_legenda_fname = '2000_Processos_com_Rotulos_legenda.csv'
    proc_rot_fname = '2000_Processos_com_Rotulos.csv'
    proc_rot_cols = ['proc_nr','r0','r1','r2','r3','r4','r5','r6']
    rot_cols = ['rot_id','rot_text']
    proc_rot_df = pd.read_csv(data_dir+proc_rot_fname,header=None,names=proc_rot_cols,dtype=str)
    rotulo_df = pd.read_csv(data_dir+rotulos_legenda_fname,names=rot_cols,header=0,usecols=[0,1],dtype=str)
    proc_rot_df.fillna('')
    rotulo_df.fillna('')
    rot_dic = {}
    for i in range(len(rotulo_df)):
        rot = rotulo_df.iloc[i]
        try:
            r = Rotulo.objects.get(nome=rot['rot_text'])
        except ObjectDoesNotExist:
            r = Rotulo(nome=rot['rot_text'])
            r.save()
            rot_dic[rot['rot_id']] = r.id
    for index,row in proc_rot_df.iterrows():
        proc_nr = row['proc_nr']
        try:
            p = Processo.objects.get(proc_nr=proc_nr)
            proc_id = p.id
        except ObjectDoesNotExist:
            p = Processo(proc_nr=proc_nr)
            p.save()
            proc_id = p.id
        for col in proc_rot_cols[1:]:
            rot_id_str = row[col]
            if not pd.isna(rot_id_str):
                rot_id = rot_dic[rot_id_str]
                prob = np.random.randint(1,99)
                try:
                    q = ProcToRot.objects.get(proc_id=proc_id, rot_id=rot_id)
                    q.prob = prob
                    q.confirmed = 0
                    q.save()
                except ObjectDoesNotExist:
                    q = ProcToRot(proc_id=proc_id, rot_id=int(rot_id), prob=prob, confirmed=0)
                    q.save()
    return True

def getRotuleProbList():
    rotulos = Rotulo.objects.all()
    rotulo_name_list,rotulo_qtde_ia_list,rotulo_qtde_ia_int_list,rotulo_qtde_pessoa_list = [],[],[],[]
    for r in rotulos:
        rotulo_name_list.append(str(r.nome))
        qtde_ia = ProcToRot.objects.filter(rot_id=r.id).count()
        qtde_pessoa = ProcToRot.objects.filter(rot_id=r.id,confirmed=1).count()
        rotulo_qtde_ia_int_list.append(qtde_ia)
        rotulo_qtde_ia_list.append(str(qtde_ia))
        rotulo_qtde_pessoa_list.append(str(qtde_pessoa))
    rotulo_idx_int_list = list(np.argsort(rotulo_qtde_ia_int_list))
    rotulo_idx_int_list.reverse()
    rotulo_idx_list = [str(idx) for idx in rotulo_idx_int_list]
    dados = {'rotulo_text_list':rotulo_name_list,
               'rotulo_qtde_ia_list':rotulo_qtde_ia_list,
               'rotulo_qtde_pessoa_list':rotulo_qtde_pessoa_list,
               'rotulo_idx_list':rotulo_idx_list}
    return dados



def getPageInit_MultaCompNH(data):
    proc_tipo = 'MultaCompNH'
    proc_nr_list = getProcByTipo(proc_tipo)
    proc_tree_dic = getProcTreeFromProcList(proc_nr_list)
    dados = {'proc_tree_dic':proc_tree_dic}
    return dados

def getPageInit_COMEX(data):
    dados = {}
    return dados

def getPageInit_MalhaIRPF(data):
    dados = {}
    return dados

def getPageInit_MAED_DCTF(data):
    dados = {}
    return dados

def getPageInit_Simples(data):
    dados = {}
    return dados

def getPageInit_gerencial1(data):
    dados = {}
    return dados

def getPageInit_gerencial2(data):
    dados = {}
    return dados

def getPageInit_gerencial3(data):
    dados = {}
    return dados

def getPageInit_gerencial4(data):
    dados = {}
    return dados


############################
###   JAP - Form Geral   ###
############################

###-----------------------------###
### Functions for filling data  ###
###   for each process type     ###
###-----------------------------###

def getDataFromProc(proc_tipo,proc_nr):
    proc_dados = {'data_ciencia':'doc_nao_loc','data_impugnacao':'doc_nao_loc'}
    p = Processo.objects.get(proc_nr=proc_nr)
    pds = ProcToDoc.objects.filter(proc_id=p.id)
    for p_d in pds:
        d = Documento.objects.get(id=p_d.doc_id)
        proc_dados = ctut.treatDocument(proc_tipo,d,proc_dados)
    return proc_dados

def getAtxsForProc(proc_tipo):
    if (proc_tipo=='MultaCompNH'): atxs = getAtxs_MultaCompNH()
    elif (proc_tipo=='MalhaIRPF'): atxs = getAtxs_MalhaIRPF()
    elif (proc_tipo=='ProcCred'): atxs = getAtxs_MultaCompNH()
    return atxs

def make_decision(request):
    atx_str_dic = request.POST
    atx_dic = {'tempestividade':[],'processo_credito':[],'impugnacao':[],\
               'preliminares':[],'merito':[],'outras':[]}
    for key,atx_str in atx_str_dic.items():
        atx_nome_list = atx_str.split(',')
        for atx_nome in atx_nome_list[1:]:
            atx = Autotexto.objects.get(nome=atx_nome)
            atx_dic[key].append(atx.texto)
    if os.path.exists(acordao_produzido_odt):
        os.remove(acordao_produzido_odt)
    shutil.copyfile(acordao_modelo_odt, acordao_produzido_odt)
    textdoc = load(acordao_produzido_odt)
    paragraph_style = {'marginleft':"0cm", 'marginright':'0cm', 'textalign':'justify'}
    text_style = {'color':'#DDD', 'fontsize':'12pt','fontweight':'normal', 'fontname':'Calibri', 'fontfamily':'Calibri', 'fontsize':'12pt'}
    p_style = Style(name="p_style", family="paragraph")
    p_style.addElement(ParagraphProperties(attributes=paragraph_style))
    p_style.addElement(TextProperties(attributes=text_style))
    s = textdoc.styles
    s.addElement(p_style)
    paragraphs = textdoc.getElementsByType(P)
    text_ps = []
    for p in paragraphs:
        text = teletype.extractText(p)
        text_ps.append(text)
        if text=='É o relatório.':
            for key,atx_text in atx_dic.items():
                if (key in ['tempestividade','processo_credito','impugnacao']):
                    new_P = P(stylename=p_style)
                    new_P.addText(atx_text[0].encode('iso-8859-1').decode('utf-8'))
                    p.parentNode.insertBefore(new_P,p)
        elif text=='Conclusão':
            for key,atx_text in atx_dic.items():
                if (key in ['preliminares','merito','alegacao']):
                    new_P = P(stylename=p_style)
                    new_P.addText(atx_text[0].encode('iso-8859-1').decode('utf-8'))
                    p.parentNode.insertBefore(new_P,p)
    ### textdoc.text.addElement(p)
    textdoc.save(acordao_produzido_odt)
    context = {'ps':text_ps}
    return render(request, 'make_decision.html', context)


def makeToyDecision():
    textdoc = OpenDocumentText()
    # Styles
    s = textdoc.styles
    h1style = Style(name="Heading 1", family="paragraph")
    h1style.addElement(TextProperties(attributes={'fontsize':"24pt",'fontweight':"bold" }))
    s.addElement(h1style)
    # An automatic style
    boldstyle = Style(name="Bold", family="text")
    boldprop = TextProperties(fontweight="bold")
    boldstyle.addElement(boldprop)
    textdoc.automaticstyles.addElement(boldstyle)
    # Text
    h=H(outlinelevel=1, stylename=h1style, text="My first text")
    textdoc.text.addElement(h)
    p = P(text="Hello world. ")
    boldpart = Span(stylename=boldstyle, text="This part is bold. ")
    p.addElement(boldpart)
    p.addText("This is after bold.")
    textdoc.text.addElement(p)
    textdoc.save("myfirstdocument.odt")
    return True



#########################################
### P2 - JAP PILOTO 1 - MultaCompNHom ###
#########################################

'''
def getProcData_MultaCompNH(proc_nr):
    loadDocsToDB_MultaCompNH(proc_nr,fixed_comp_dir,fixed_descomp_dir,fixed_done_dir)
    julgamento_dado = treatMultaCompNH('MultaCompNH',proc_nr)
    return julgamento_dado
'''

def loadDocsToDB(proc_nr,comp_dir,descomp_dir,done_dir):
    try:
        p = Processo.objects.get(proc_nr=proc_nr)
        pds = ProcToDoc.objects.filter(proc_id=p.id)
        if len(pds)==0:
            if (len(os.listdir(comp_dir))>0):
                ctut.unzipProcs(comp_dir,descomp_dir,done_dir,proc_nr)
            doc_dic_list = ctut.getDocsFromUnzips(descomp_dir,proc_nr)
            print('doc_dic_list = ',doc_dic_list)
            for doc_dic in doc_dic_list:
                fpath,dic_proc_nr,doc_tipo,doc_nome,doc_fls = doc_dic['fpath'],doc_dic['proc_nr'],doc_dic['doc_tipo'],doc_dic['doc_nome'],doc_dic['doc_fls']
                '''
                try:
                    p = Processo.objects.get(proc_nr=dic_proc_nr)
                except ObjectDoesNotExist:
                    break
                '''
                doc = Documento(tipo=doc_tipo,nome=doc_nome,arquivo=fpath,fls=doc_fls)
                #text = fulltext.get(fpath,'no_text', backend='pdf')
                text = ctut.extract_text_from_pdf(fpath)
                doc.texto = text
                doc.save()
                p_d = ProcToDoc(proc_id=p.id,doc_id=doc.id)
                p_d.save()
    except ObjectDoesNotExist: pass
    return True

def treatProcText(proc_tipo,proc_nr):
    dados = getDataFromProc(proc_tipo,proc_nr)
    autotextos = getAtxsForProc(proc_tipo)
    rotulagem_ia = ctut.tagProcByIA(proc_tipo)
    julgamento_dado = {'proc_nr':proc_nr,'dados':dados,'autotextos':autotextos,'rotulagem_ia':rotulagem_ia}
    return julgamento_dado

'''
def getProcCredData_MultaCompNH(proc_cred,proc_nr):
    try:
        p = Processo.objects.get(proc_nr=proc_cred)
    except ObjectDoesNotExist:
        p = Processo(proc_nr=proc_cred)
        p.save()
    loadDocsToDB_MultaCompNH(proc_cred,fixed_cred_comp_dir,fixed_cred_descomp_dir,fixed_cred_done_dir)
    proc_cred_dado = treatMultaCompNH_Cred(proc_cred,proc_nr)
    return proc_cred_dado

def treatMultaCompNH_Cred(proc_cred,proc_nr):
    proc_cred_dado = getDataFromProc('ProcCred',proc_cred,proc_nr)
    return proc_cred_dado
'''

def getAtxs_MultaCompNH():
        atxs = {'tempestividade':{},'proc_compensacao':{},'impugnacao':{},\
                      'preliminares':{},'merito':{},'outras':{}}
        atx_set = Autotexto.objects.filter(tema='multa_compensacao_nao_homologada') #'MultaCompNH'
        for a in atx_set:
            if (a.capitulo=='acordao'):
                atxs['tempestividade'][a.nome] = a.texto
            elif (a.capitulo=='relatorio'):
                atxs['proc_compensacao'][a.nome] = a.texto
                atxs['impugnacao'][a.nome] = a.texto
            elif (a.capitulo=='voto'):
                atxs['preliminares'][a.nome] = a.texto
                atxs['merito'][a.nome] = a.texto
                atxs['outras'][a.nome] = a.texto
        return atxs


####################################
###  P3 - JAP REPLICA MalhaIRPF  ###
####################################

def getAtxs_MalhaIRPF():
        atxs = {'tempestividade':{},'impugnacao':{},\
                      'preliminares':{},'merito':{},'outras':{}}
        atx_set = Autotexto.objects.filter(tema='MalhaIRPF')
        for a in atx_set:
            if (a.capitulo=='acordao'):
                atxs['tempestividade'][a.nome] = a.texto
            elif (a.capitulo=='relatorio'):
                atxs['impugnacao'][a.nome] = a.texto
            elif (a.capitulo=='voto'):
                atxs['preliminares'][a.nome] = a.texto
                atxs['merito'][a.nome] = a.texto
                atxs['outras'][a.nome] = a.texto
        return atxs


################################
###     ROTULAGEM ATIVA      ###
################################

def getRotuleProcessView(rot_now_text):
    rotulo_df = pd.DataFrame.from_records(Rotulo.objects.all().values('id','nome'))
    processo_df = pd.DataFrame.from_records(Processo.objects.all().values('id','proc_nr','confirmed'))
    proc_rot_df = pd.DataFrame.from_records(ProcToRot.objects.all().values('proc_id','rot_id','prob','confirmed','user'))
    rot_df = rotulo_df[rotulo_df['nome']==rot_now_text]
    print(rot_now_text,rot_df)
    rot_now_id = rot_df.iloc[0]['id']
    r_p_df = proc_rot_df[proc_rot_df['rot_id']==rot_now_id]
    r_p_df.sort_values('prob',ascending=False,inplace=True)
    r_p_id_list = list(r_p_df['proc_id'])
    r_p_prob_list = list(r_p_df['prob'])
    r_p_state_list = list(r_p_df['confirmed'])
    r_p_nr_list = [processo_df[processo_df['id']==idx].iloc[0]['proc_nr'] for idx in r_p_id_list]
    r_p_prob_50_array = np.array(r_p_prob_list) - 50
    r_p_prob_50abs_array = np.array([abs(pb) for pb in r_p_prob_50_array])
    r_p_50_idx = r_p_prob_50abs_array.argmin()
    r_p_50_nr = r_p_nr_list[r_p_50_idx]
    proc_now_nr,proc_now_idx = r_p_50_nr,r_p_50_idx
    proc_now_id = processo_df[processo_df['proc_nr']==proc_now_nr].iloc[0]['id']
    p_r_id_list,p_r_text_list,p_r_prob_list,p_r_state_list = ctut.getProcRotules(proc_now_id,rotulo_df,proc_rot_df)
    dados = {
      'rot_now_id':str(rot_now_id),
      'rot_now_text':rot_now_text,
      'r_p_id_list':r_p_id_list,
      'r_p_nr_list':r_p_nr_list,
      'r_p_prob_list':r_p_prob_list,
      'r_p_state_list':r_p_state_list,
      'proc_now_idx':str(proc_now_idx),
      'proc_now_id':str(proc_now_id),
      'proc_now_nr':proc_now_nr,
      'p_r_id_list':p_r_id_list,
      'p_r_text_list':p_r_text_list,
      'p_r_prob_list':p_r_prob_list,
      'p_r_state_list':p_r_state_list,
    }
    return dados

def loadProcListsFromDB():
    proc_id_list,proc_list,proc_state_list = [],[],[]
    for p in Processo.objects.all():
        proc_id_list.append(str(p.id))
        proc_list.append(str(p.proc_nr))
        proc_state_list.append(p.confirmed) #np.random.randint(0,2)
    proc_prob_list = [np.random.randint(1,99) for p in proc_list]
    return proc_id_list,proc_list,proc_prob_list,proc_state_list


def getConfirmedRotules(proc_now):
    p = Processo.objects.get(proc_nr=proc_now)
    pr_okk_db = ProcToRot.objects.filter(proc_id=p.id,confirmed=1)
    rot_okk_list = [Rotulo.objects.get(id=pr.rot_id).rot_text for pr in pr_okk_db]
    #rot_state_list = [pr.state for pr in pr_okk_db]
    rot_user_list = [pr.user for pr in pr_okk_db]
    return rot_okk_list,rot_user_list

def confirmRotules(proc_now,rot_okk_list,rot_nok_list,user):
    p = Processo.objects.get(proc_nr=proc_now)
    proc_id = p.id
    for rot in rot_okk_list:
        r = Rotulo.objects.get(nome=rot)
        rot_id = r.id
        pr = ProcToRot.objects.get(proc_id=proc_id,rot_id=rot_id)
        pr.confirmed = 1
        pr.user = user
        pr.save()
    for rot in rot_nok_list:
        r = Rotulo.objects.get(nome=rot)
        rot_id = r.id
        pr = ProcToRot.objects.get(proc_id=proc_id,rot_id=rot_id)
        pr.confirmed = 0
        pr.user = user
        pr.save()
    p.proc_confirmed = 1
    p.save()
    return True


################################
###   Funcoes Auxiliares     ###
################################

def getProcByTipo(proc_tipo):
    tema_dic = {'MultaCompNH':'2066'} # DELETE!!!! forcing '2066' only for development!!!
    tema = tema_dic[proc_tipo]
    ps = Processo.objects.filter(act_tema=tema)
    proc_nr_list = [p.proc_nr for p in ps]
    return proc_nr_list

def getProcTreeFromProcList(proc_nr_list):
    proc_tree_dic = {}
    for p_nr in proc_nr_list:
        p = Processo.objects.get(proc_nr=p_nr)
        try:
            pl = ProcToLot.objects.get(proc_id=p.id)
            l = Lote.objects.get(id=pl.lot_id)
            if (l.nome not in proc_tree_dic.keys()): proc_tree_dic[l.nome] = [p_nr]
            else: proc_tree_dic[l.nome].append(p_nr)
        except ObjectDoesNotExist:
            pass
    return proc_tree_dic

def getProcessesDic(filter_dic):
    if (filter_dic!={}): ps = Processo.objects.filter(**filter_dic) # ...qs = Processo.objects.filter(tipo=tipo)
    else: ps = Processo.objects.all()
    df = pd.DataFrame.from_records(ps.values(*filter_feature_list))
    if len(df)>0: df.columns = filter_feature_header
    items_nr = len(df)
    df1 = df[:100].copy() # DELETE!!!! limiting to 100 only for development!!!
    tab_dic = {}
    for c in df1.columns:
        tab_dic[c] = list(df1[c])
    return tab_dic,items_nr

def getRotulesDic():
    rs = Rotulo.objects.all()
    df = pd.DataFrame.from_records(rs.values())
    df['proc_qtt'] = 0
    for idx in df.index:
        reg = df.loc[idx]
        prs = ProcToRot.objects.filter(rot_id=reg['id'])
        reg['proc_qtt'] = len(prs)
    #df.columns = df.columns
    items_nr = len(df)
    tab_dic = {}
    for c in df.columns:
        tab_dic[c] = list(df[c])
    return tab_dic,items_nr



''' ******************************** LIXO *****************************

#import shutil
#import io
#import zipfile
#import pickle as pk
#import odf
#import fulltext
#from pdfminer.converter import TextConverter
#from pdfminer.pdfinterp import PDFPageInterpreter
#from pdfminer.pdfinterp import PDFResourceManager
#from pdfminer.pdfpage import PDFPage


#global variables

std_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. In vitae fringilla est, ac luctus turpis. Duis fermentum, magna nec porttitor fermentum, magna mi facilisis tellus, id iaculis velit ante ut odio. Duis dapibus enim non ex pharetra, et rutrum lacus ullamcorper. Mauris ultricies nisi sit amet risus auctor, pellentesque efficitur diam placerat. Etiam suscipit elit commodo aliquet pharetra. Cras viverra, turpis a blandit egestas, elit sem aliquet turpis, quis rhoncus libero turpis id risus. Nunc aliquam, ante lobortis ullamcorper aliquam, metus elit pellentesque metus, ac varius lectus ex vel odio. Ut luctus, tortor facilisis cursus fermentum, nulla neque aliquet mi, sed sagittis tellus felis in mi. Vivamus ut tellus ut nulla malesuada interdum sit amet id nisi. Aenean nisl ex, varius non accumsan sed, finibus et enim. Donec malesuada magna in tincidunt luctus. Morbi malesuada dictum elit, a tincidunt dolor pretium eget. Ut ante purus, lobortis sit amet hendrerit quis, consequat et elit. In non ornare turpis, eget laoreet ipsum. Nunc gravida ac ipsum et suscipit. Donec ultrices, tortor in ullamcorper porta, eros nunc sagittis est, a sodales dui tellus sed erat. Curabitur non massa ut turpis molestie pulvinar. Nunc nec tortor tellus. Curabitur tristique auctor luctus. Pellentesque auctor elit eu aliquam placerat. Nullam pretium dictum laoreet. Fusce vitae libero nisl. Vestibulum mollis in tortor et tempor. Vestibulum nec volutpat nulla, non tempor mi. Curabitur mollis lacus ac rhoncus porta. Nullam sollicitudin metus a massa condimentum, eget ultricies mi faucibus. Sed molestie, dolor in tempus maximus, ante lorem tempor sem, sed dignissim diam est quis quam. Vestibulum ullamcorper lacinia eleifend. Sed nec arcu libero. Sed venenatis sit amet enim vitae semper. Curabitur ornare massa sed enim pretium pharetra. Nam laoreet vitae quam nec elementum. Quisque at pretium lacus, eget varius leo. Suspendisse vehicula nibh libero, non laoreet arcu gravida eleifend. Vivamus eget leo congue, consectetur magna a, convallis erat. Etiam efficitur aliquam dolor, eget vestibulum ligula semper at. Nunc cursus a magna eget rhoncus. Nulla eget lectus fermentum, accumsan neque in, tristique arcu. Donec feugiat lectus id ullamcorper varius. Vivamus eget convallis augue, vitae luctus massa. Nunc imperdiet nisi id dolor sagittis consectetur. Donec et ex eu orci pulvinar laoreet. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Integer nec dapibus dui. Proin gravida, dui vitae scelerisque sagittis, est tortor accumsan augue, quis rhoncus erat felis ac purus. Sed eu mi id risus tincidunt congue. Quisque blandit sodales nisl. Integer tortor orci, pulvinar et orci at, ultricies faucibus magna. Sed rhoncus libero ut lectus sagittis rutrum. Nunc neque dolor, euismod ut sagittis in, condimentum eu ipsum. Pellentesque nunc arcu, commodo ut gravida in, vehicula sit amet nisl. Mauris elementum dignissim turpis, tincidunt lobortis tellus fringilla vitae. Cras lacinia facilisis massa, a consequat nunc ornare vitae. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Fusce tempus placerat enim, vitae accumsan ipsum mollis non. Nam rhoncus erat ac magna pellentesque, ut semper enim pellentesque. Sed mattis rhoncus diam quis efficitur. Integer dictum quam non pulvinar accumsan."

procs_MultaCompNH_fname = 'IAC_processosMultaCompNH.txt'

header_MultaCompNH = ['Unidade','Número_Processo','ACT_tema','ACT_origem','ACT_tributo',\
          'protocolo_data','sessao_drj_data','he_decimal','he','apensado',\
          'infracao','ni','nome','equipe','relator_drj','relator_carf',\
          'situacao','valor_origin','valor_processo']
processo_feature_list = ['proc_id','proc_nr','interessado','ni','act_origem','act_tributo',\
                         'act_tema','infracao','protocolo_data','val_origin','val_proc',\
                         'unidade','equipe','he','apensado','drj_sessao_data','drj_relator',\
                         'carf_sessao_data','carf_relator','situacao','confirmed']

import_params_dic = {'processo':\
                  {'todos':{'fname':'acervo_Total.txt','header':header},\
                  'MultaCompNH':{'fname':'acervo_MultaCompNH.txt','header':header_MultaCompNH},\
                  'MalhaIRPF':{'fname':'acervo_MultaCompNH.txt','header':header_MultaCompNH},
                  },
              'autotexto':{'todos':''},
              'rotulo':{'todos':''},
              'documento':{'todos':''},
}


# provisorialy fixed models
proc_data_structure = {
    'MultaCompNH':{
            'proc_nr':'',\
            'nome':'',\
            'ni':'',\
            'link_processo':'',\
            'data_extracao':'',\
            'ciencia_data':'',\
            'ciencia_fls':'',\
            'impugnacao_data':'',\
            'impugnacao_fls':'',\
            'tempestivo':'',\
            'nl_nr':'',\
            'nl_data':'',\
            'nl_fls':'',\
            'cred_tipo':'',\
            'cred_proc_nr':'',\
            'dcomp_mtx':'',\
            'nl_descricao':'',\
            'nl_enquadramento':'',\
    }
}

# provisorialy fixed variables
lote_MultaCompNH = {'LoteA':['11080729156201887','11080729304201863','11080729020201877','11080729033201846'],\
                    'LoteB':['11080729040201848','11080729042201837','11080729164201823','11080729236201832'],\
                    'LoteC':['11080729242201890','11080729335201814','11080729451201833','11080729461201879',\
                             '11080729586201807','11080729618201866','11080729810201852','11080729076201821',\
                             '11080729425201813','11080729660201887','11080729797201831','11080728897201841'],\
                    'LoteD':['11080728903201860','11080728963201882','11080728964201827','11080729071201807'],\
                    'LoteE':['11080729072201843','11080729155201832','11080729187201838','11080729232201854'],\
                    'LoteF':['11080729326201823','11080729504201816','11080729589201832','11080729656201819',\
                             '11080729875201806','11080738398201861','11080736841201860','11080732735201815',\
                             '11080735909201893','11080736083201880','11080733019201847','11080732480201882',\
                             '11080732834201899','11080735966201872','11080733199201867','11080733962201850'],\
                    'LoteG':['11080735099201875','11080734087201823','11080733170201885','11080737249201885'],\
                    'LoteH':['11080729906201811','11080733382201862','11080732469201812','11080738997201885',\
                             '11080736030201869','11080733307201800','11080733410201841','11080737205201855'],\
                    'LoteI':['11080732494201804','11080734987201871','11080738973201826','11080737481201813',\
                             '11080738274201886','11080732750201855','11080734277201841','11080731160201813',\
                             '11080736290201834','11080737485201800','11080734573201841','11080737941201811',\
                             '11080738374201811','11080737375201830','11080738007201817','11080737624201897',\
                             '11080737807201811','11080738379201835','11080739038201887','11080733004201889',\
                             '11080732557201814','11080734163201809','11080734874201875','11080729766201708',\
                             '11080739021201820','11080728569201844','11080732959201819','11080733335201819',\
                             '11080730856201814','11080730860201882','11080733919201894','11080736295201867',\
                             '11080738458201846','11080732600201841','11080732914201844','11080733866201810',\
                             '11080732402201888','11080732404201877','11080732411201879','11080732420201860',\
                             '11080732439201814','11080732452201865','11080732453201818','11080732457201898',\
                             '11080732499201829','11080732522201885','11080732594201822','11080732818201804',\
                             '11080732827201897','11080732893201867','11080732929201811','11080732934201815',\
                             '11080732962201832','11080733285201870','11080734421201849','11080734421201849',\
                             '11080734483201851','11080734973201857','11080736059201841','11080736172201826',\
                             '11080736415201826','11080738293201811','11080738656201818','11080738761201849']}
lote_MalhaIRPF = lote_MultaCompNH

#########

def showDataToImport(request):
    resp = {}
    return JsonResponse(resp)


###########################################################################
###  Business Process Specific Processing Functions (for implementing)  ###
###########################################################################

def getProcData(proc_nr):
    julgamento_dado = getProcData_MultaCompNH(proc_nr)
    return julgamento_dado


############################
###  Modelo de Processo  ###
###    PONTA-A-PONTA     ###
############################

def modelo_processos(request):
    context = {}
    return render(request, 'modelo_processos.html', context)


def acervo_RFB(request):
    fname,header = '',''
    tab_dic = ctut.getImportDic(data_dir+fname,header)
    context = {'tab_dic':tab_dic}
    return render(request, 'acervo_RFB.html', context)
    

def acervo_MultaCompNH(request):
    fname,header = '',''
    tab_dic = ctut.getImportDic(data_dir+fname,header)
    context = {'tab_dic':tab_dic}
    return render(request, 'acervo_MultaCompNH.html', context)
 

def lotes_MultaCompNH(request):
    fname,header = '',''
    tab_dic = ctut.getImportDic(data_dir+fname,header)
    context = {'tab_dic':tab_dic}
    return render(request, 'lotes_MultaCompNH.html', context)


def tema_tabulacao(request):
    context = {}
    return render(request, 'tema_tabulacao.html', context)


def lotes_tabulacao(request):
    context = {}
    return render(request, 'lotes_tabulacao.html', context)


def rotulagem(request):
    proc_list = lote_MultaCompNH
    if (Documento.objects.all().count()==0): populateDocumentoDB(fixed_comp_dir,fixed_descomp_dir,fixed_done_dir)
    dados = {}
    dados = getDataFromTexts(dados)
    ds = Documento.objects.all()
    doc_name_list = []
    for i in range(ds.count()):
        d = ds[i]
        doc_name_list.append(d.nome_arquivo)
    text = ''
    rotulos = {}
    rotulos = tagTextsUsingPLN(rotulos)
    context = {'text':text,'proc_nr_list':proc_list,'doc_name_list':doc_name_list,'result':str(rotulos)}
    return render(request, 'rotulagem.html', context)

def selectPLNText(request):
    #proc_nr = request.POST['proc_nr']
    doc_nome = request.POST['doc_nome']
    d = Documento.objects.get(nome_arquivo=doc_nome)
    text = d.texto
    resp = {'text':text}
    return JsonResponse(resp)

def lotes_rotulados(request):
    context = {}
    return render(request, 'lotes_rotulados.html', context)


def lotes_distribuidos(request):
    context = {}
    return render(request, 'lotes_distribuidos.html', context)


def relatoria(request):
    context = {}
    return render(request, 'relatoria.html', context)


def lotes_relatados(request):
    context = {}
    return render(request, 'lotes_relatados.html', context)


def julgamento(request):
    context = {}
    return render(request, 'julgamento.html', context)


def lotes_julgados(request):
    context = {}
    return render(request, 'lotes_julgados.html', context)

###--------------------------------------------###
### Auiliary functions for Modelo de Processos ###
###--------------------------------------------###

def sendFigure(request):
    import base64
    fig_id = request.POST['fig_id']
    img_dir = 'static/images/'
    fig_file = img_dir+fig_id #+'.png'
    with open(fig_file,'rb') as f:
        img_data = f.read()
    img_data_uri = base64.b64encode(img_data).decode('ascii')
    response = HttpResponse(content_type="application/octet-stream")
    response['Content-Disposition'] = 'attachment; filename=hist.zip'
    response.write(img_data_uri)
    return response


############################
###   JAP - Form Geral   ###
############################

def openProcess(proc_tipo,proc_nr):
    dados = getDataFromProc(proc_tipo,proc_nr)
    autotextos = getAtxsForProc(proc_tipo)
    rotulagem_ia = ctut.tagProcByIA(proc_tipo)
    return dados,autotextos,rotulagem_ia

###-----------------------------###
### Functions for filling data  ###
###   for each process type     ###
###-----------------------------###






################################
###      TEXT TAGGING        ###
################################
    
def ManTextTag(request):
    file_list = getFileList()
    context = {
        'file_list':file_list,
        }
    return render(request, 'ManTextTag.html', context)

def selTextUpFile(request):
    inmemory_file = request.FILES['file']
    txt_upfile = File(inmemory_file)
    text,txt_fname,file_list = uploadTextFile(txt_upfile)
    resp = {'text':text,'txt_fname':txt_fname,'file_list':file_list}
    return JsonResponse(resp)

def selTextDownFile(request):
    txt_fname = request.POST['txt_fname']
    text,tag_list,link_list = downloadTextFile(txt_fname)
    resp = {'text':text,'tag_list':tag_list,'link_list':link_list}
    return JsonResponse(resp)

def saveTextTagging(request):
    req = json.loads(request.POST['jreq'])
    txt_fname = req['txt_fname']
    tag_list = req['tag_list']
    link_list = req['link_list']
    ok = tagTextFile(txt_fname,tag_list,link_list)
    resp = {'ok':ok}
    return JsonResponse(resp)


################################
###      IA TEXT ROTULING    ###
################################
    
def IATextRotuling(request):
    import IATextRotuling as IAT
    NB_prediction_list,SVC_prediction_list,LR_prediction_list = IAT.runIARotuling()
    context = {
        'NB_prediction_list':NB_prediction_list,
        'SVC_prediction_list':SVC_prediction_list,
        'LR_prediction_list':LR_prediction_list,
    }
    return render(request, 'IATextRotuling.html', context)


################################
###   Funcoes Auxiliares     ###
################################


def tagTextsUsingPLN(rotulos):
    ds = Documento.objects.filter(tipo='impugnacao') # fazer OR para 'mi'
    for d in ds[0:1]:
        text = d.texto
        pattern = 'IMPUGNAÇÃO([\S\s]*)'
        text = re.findall(pattern,text)[0]
        text.encode('utf-8')
        pattern = 'Fl\. \d{2}SP SAO PAULO DEINFDocumento nato-digitalDocumento de 13 página\(s\) confirmado digitalmente. Pode ser consultado no endereço https://cav\.receita\.fazenda\.gov\.br/eCAC/publico/login\.aspxpelo código de localização EP12\.0520\.11072\.Y2MA\.\\x0c'
        text = re.sub(pattern,'&&&&&&&&&&&&&&&&&&',text)
        #pattern = 'SP SAO PAULO DEINFDocumento nato-digitalDocumento de 13 página(s) confirmado digitalmente. Pode ser consultado no endereço https://cav.receita.fazenda.gov.br/eCAC/publico/login.aspxpelo código de localização EP12.0520.11072.Y2MA.'
        #text.replace(pattern,' ')
    rotulos['nome'] = text
    return rotulos

def getDataFromTexts(dados):
    ds = Documento.objects.all()
    for d in ds[0:1]: #<---- TIRAR URGENTE!!!!!
        pd = ProcToDoc.objects.get(doc_id=d.id)
        proc_id = pd.proc_id
        p = Processo.objects.get(id=proc_id)
        proc_nr = p.proc_nr
        proc_dados = {}
        if d.tipo=='nl':
            proc_dados = ctut.treatNotificacao(proc_dados,d.texto)
        elif d.tipo=='ciencia':
            proc_dados = ctut.treatCiencia(proc_dados,d.texto)
        elif d.tipo=='juntada':
            proc_dados = ctut.treatJuntada(proc_dados,d.texto)
        dados[proc_nr] = proc_dados
    return dados



####################################
### ACERVO: Populating Functions ###
####################################

def populateProcessoDB(data):
    ps = Processo.objects.all()
    antes = ps.count()
    ps.delete()
    #populateMalhaIRPF()
    populateMultaCompNH()
    depois = Processo.objects.all().count()
    dados = {'antes':antes,'depois':depois}
    return dados

def populateDocumentoDB(comp_dir,descomp_dir,done_dir):
    ds = Documento.objects.all()
    antes = ds.count()
    ds.delete()
    ps = Processo.objects.all()
    proc_list = [p.proc_nr for p in ps]
    if (len(os.listdir(comp_dir))>0):
        ctut.unzipProcs(comp_dir,descomp_dir,done_dir,proc_list)
    docs_list = ctut.getDocsFromUnzips(descomp_dir,proc_list)
    loadDocsToDB_MultaCompNH(docs_list)
    depois = Documento.objects.all().count()
    dados = {'antes':antes,'depois':depois}
    return dados


def populateMultaCompNH():
    df = pd.read_csv(multa_comp_dir+procs_MultaCompNH_fname,header=None,names=['proc_nr'])
    proc_nr_list = list(df['proc_nr'])
    for i in range(len(proc_nr_list)):
        p = Processo(proc_nr=proc_nr_list[i],confirmed=1)
        p.save()
    return True

def populateProcRotuleDB_Toy():
    proc_dim,rot_dim = 10,8
    for i in range(proc_dim):
        q = Processo(proc_nr="12345."+str(100001+i)+"/2000-00")
        q.save()
    for i in range(rot_dim):
        rot_text = 20*string.ascii_lowercase[i]
        q = Rotulo(rot_text=rot_text)
        q.save()
    proc_count = Processo.objects.all().count()
    rot_count = Rotulo.objects.all().count()
    for p_id in range(proc_count):
        r_count = np.random.randint(1,rot_count)
        rot_choice = np.random.choice(range(rot_count), r_count, replace=False)
        for r_id in rot_choice:
            q = ProcToRot(proc_id=p_id, rot_id=r_id, confirmed=0)
            q.save()


    

def getFileList():
    docs = Documento.objects.all()
    fname_list = [doc.nome_arquivo for doc in docs]
    return fname_list

def uploadTextFile(txt_upfile):
    txt_fname = txt_upfile.name
    ftext = ctut.extractTextFromFile(txt_upfile,ftype='pdf')
    text = ctut.cleanString(ftext)
    doc = Documento.objects.filter(nome_arquivo=txt_fname)
    if (doc.exists()): doc.delete()
    last_id = Documento.objects.all().count()
    doc = Documento(id=last_id,nome_arquivo=txt_fname,nome=txt_fname)
    doc.texto = text
    doc.tags = json.dumps([])
    doc.links = json.dumps([])
    doc.save()
    file_list = getFileList()
    return text,txt_fname,file_list

def downloadTextFile(txt_fname):
    doc = Documento.objects.get(nome_arquivo=txt_fname)
    if (doc==None): return '',[],[]
    text = doc.texto
    tag_list = json.loads(doc.tags)
    link_list = json.loads(doc.links)
    return text,tag_list,link_list

def tagTextFile(txt_fname, tag_list, link_list):
    doc = Documento.objects.get(nome_arquivo=txt_fname)
    if (doc==None): return False
    doc.tags = json.dumps(tag_list)
    doc.links = json.dumps(link_list)
    doc.save()
    return True

'''

################################
###           LIXO           ###
################################    

'''
def getProcTreeFromLote(lote_nome):
    proc_lote_dic = {'MultaCompNH':lote_MultaCompNH,'MalhaIRPF':lote_MalhaIRPF}
    proc_tree_dic = proc_lote_dic[lote_nome]
    return proc_tree_dic

def getProcesses(proc_tipo):
    proc_tree_dic = getProcTreeFromLote(proc_tipo)
    return proc_tree_dic

def goDBImportPage(data):
    dados = {}
    return dados

def unzipProcs(comp_dir,descomp_dir,done_dir,proc_list):
    for root, dirs, files in os.walk(comp_dir):
        for fname in files:
            proc_nr = fname[:17]
            if (proc_nr in proc_list):
                os.mkdir(descomp_dir+proc_nr)
                with zipfile.ZipFile(root+fname, 'r') as zip_ref:
                    zip_ref.extractall(descomp_dir+proc_nr) #dir Django!!!
                shutil.move(root+fname,done_dir)
    return True

def getDocsFromUnzips(unzip_dir,proc_list):
    doc_tipos = {'nl':'Notific','ciencia':'Abertura','juntada':'Juntada',\
                 'impugnacao':'Impug','mi':'Manifest'}
    doc_list = []
    dirs = os.listdir(unzip_dir)
    for dname in dirs:
        proc_doc_count=0
        if dname in proc_list:
            proc_nr = dname
            fname_list = os.listdir(unzip_dir+'/'+dname)
            for fname in fname_list:
                for tipo,trecho in doc_tipos.items():
                    if (trecho in fname):
                        new_fpath = unzip_dir+'/'+dname+'/'+dname+'_'+tipo+str(proc_doc_count)+'.pdf'
                        os.rename(unzip_dir+'/'+dname+'/'+fname,new_fpath)
                        doc_tipo = tipo
                        doc_list.append({'fpath':new_fpath,'proc_nr':proc_nr,'doc_tipo':doc_tipo})
                        proc_doc_count=proc_doc_count+1
    return doc_list

def extract_text_from_pdf(pdf_path):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh, 
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()
    # close open handles
    converter.close()
    fake_file_handle.close()
    if text: return text

def getAutotextos(text):
    #''
    with open(atx_file,'r',encoding='utf-8') as f:
        text = f.read()
    #''
    split_text = text.split('#')[1:]
    autotextos = []
    state = 0
    for tx in split_text:
        if state==0: # initial or after text
            if tx=='O': state=1
            elif tx=='S': state=2
            elif tx=='N': state=3
            elif tx=='T': state=4
        elif state==1: # found 'O'
            tema = tx.replace('\n','')
            state=0
        elif state==2: # found 'S'
            capitulo = tx.replace('\n','')
            state=0
        elif state==3: # found 'N'
            nome = tx.replace('\n','')
            state=0
        elif state==4: # found 'T'
            texto = tx
            atx = {'tema':tema,'capitulo':capitulo,'nome':nome,'texto':texto,'autor':'RFB'}
            autotextos.append(atx)
            state=0
    return autotextos

def getDataFromPdf_MultaCompNHom(nl_text,ciencia_text,juntada_text,impugnacao_text):
    data = {}
    campos1_pattern = 'Secretaria da Receita Federal do Brasil\nFl. (.*)\nNOTIFICAÇÃO DE LANÇAMENTO Nº NLMIC - (.*)\nMULTA POR COMPENSAÇÃO NÃO HOMOLOGADA\n1 - SUJEITO PASSIVO\nCNPJ\nNOME EMPRESARIAL\n(.*)\n(.*)\n.*\n.*\n.*\n2 - LAVRATURA\nLOCAL\nDATA / HORA\nPROCESSO DE AUTUAÇÃO\n(\d\d/\d\d/\d\d\d\d)\n\d\d:\d\d:\d\d\n(.+)\n'
    campos1 = list(re.findall(campos1_pattern, nl_text)[0])
    data['notificacao'] = campos1[1:3]+campos1[:1]
    data['proc'] = campos1[3:]
    campos2_pattern = '3 - DESCRIÇÃO DOS FATOS E FUNDAMENTAÇÃO LEGAL\nDESCRIÇÃO DOS FATOS\n([\s\S]*)\nENQUADRAMENTO LEGAL\n([\s\S]*)\n4 - DADOS DO DESPACHO DECISÓRIO\nNº DO RASTREAMENTO\nTIPO DE CRÉDITO\n\d*\n(.*)\nPROCESSO DE CRÉDITO\n(.*)\nDETENTOR DO CRÉDITO\n'
    campos2 = list(re.findall(campos2_pattern, nl_text)[0])
    data['credito_proc'] = campos2[2:]
    data['notif_descricao_text'] = cleanBreak(campos2[0])
    data['notif_fundleg_text'] = cleanBreak(campos2[1])
    campos3_pattern = 'DETALHAMENTO DA APURAÇÃO DA MULTA POR COMPENSAÇÃO NÃO HOMOLOGADA\nCPF/CNPJ\nNOME/NOME EMPRESARIAL\nPROCESSO DE AUTUAÇÃO\n06.995.362/0001-46 COMPANHIA PAULISTA DE PARCERIAS - CPP\nDCOMP\n\d{24}\n(\d{17})\nValor não homologado \(R\$\)\n(.*)\n'
    campos3 = list(re.findall(campos3_pattern, nl_text)[0])
    data['perdcomps'] = [[campos3[i*2],campos3[i*2+1]] for i in range(int(len(campos3)/2))]
    campos_pattern = 'DF COREC RFB\nFl\. (.*)\nMINISTÉRIO DA FAZENDA\n[\s\S]*na data de\n(\d\d/\d\d/\d\d\d\d)'
    campos = list(re.findall(campos_pattern, ciencia_text)[0])
    data['ciencia'] = [campos[1],campos[0]]
    campos_pattern = '\nFl. (.*)\nMINISTÉRIO DA FAZENDA\nSP SAO PAULO DERAT\nPROCESSO/PROCEDIMENTO: 11080.734483/2018-51\nINTERESSADO:06995362000146 - COMPANHIA PAULISTA DE PARCERIAS - CPP\nTERMO DE ANÁLISE DE SOLICITAÇÃO DE JUNTADA\nEm (\d\d/\d\d/\d\d\d\d) 15:28:46 foi registrada a Solicitação de Juntada de Documentos ao processo citado acima.\n'
    campos = list(re.findall(campos_pattern, juntada_text)[0])
    data['impugnacao'] = [campos[1],campos[0]]
    return data
'''

## Text auxiliary functions ###

'''
def cleanBreak(text):
    text = text.replace('\n',' ')
    return text

def tagProcByIA_MalhaIRPF():
    ia_rotuling = {'tempestividade':[0],
                   'impugnacao':[3,4,5],
                   'preliminares':[0,1],
                   'merito':[2,3,4],
                   'outras':[5]}
    return ia_rotuling

def tagProcByIA_MultaCompNH():
    ia_rotuling = {'tempestividade':[0],
                   'proc_compensacao':[1,2],
                   'impugnacao':[3,4,5],
                   'preliminares':[0,1],
                   'merito':[2,3,4],
                   'outras':[5]}
    return ia_rotuling

def getProcRotules(proc_now_id,rot_df,p_rot_df):
    p_r_df = rot_df.copy()
    p_r_df['prob'],p_r_df['state'],p_r_df['user'] = 0,-1,''
    for _,pr in p_r_df.iterrows():
        r = pr['rot_id']
        for _,x in p_rot_df.iterrows():
            xp,xr = x['proc_id'],x['rot_id']
            if ((xp==proc_now_id) and (xr==r)):
                pr['prob'] = x['prob']
                pr['state'] = x['confirmed']
                pr['user'] = x['user']
    p_r_df.sort_values('prob',ascending=False,inplace=True)
    p_r_id_list = list(p_r_df['rot_id'])
    p_r_text_list = list(p_r_df['texto'])
    p_r_prob_list = list(p_r_df['prob'])
    p_r_state_list = list(p_r_df['state'])
    return p_r_id_list,p_r_text_list,p_r_prob_list,p_r_state_list

def treatDocument(proc_tipo,proc_dados,d):
    if (proc_tipo=='MultaCompNH'):
        if d.tipo=='nl':
            proc_dados = treatNotificacao(proc_dados,d.texto)
        elif d.tipo=='ciencia':
            proc_dados = treatCiencia(proc_dados,d.texto)
        elif d.tipo=='juntada':
            proc_dados = treatJuntada(proc_dados,d.texto)
    elif (proc_tipo=='MalhaIRPF'):
        if d.tipo=='ciencia':
            proc_dados = treatCiencia(proc_dados,d.texto)
        elif d.tipo=='juntada':
            proc_dados = treatJuntada(proc_dados,d.texto)
    return proc_dados

def treatJuntada(proc_dados,texto):
    pattern = '\d{2}/\d{2}/\d{4}'
    if (re.search('IMPUGNAÇÃO',texto) or re.search('MANIFESTAÇÃO DE INCONFORMIDADE',texto)):
        data_impugnacao = re.findall(pattern,texto)
        proc_dados['data_impugnacao'] = data_impugnacao[0]
    return proc_dados

def treatCiencia(proc_dados,texto):
    # documento como imagem -> pulamos
    pattern = '\d{2}/\d{2}/\d{4}'
    if (re.search('ABERTURA',texto)):
        data_ciencia = re.findall(pattern,texto)
        proc_dados['data_ciencia'] = data_ciencia[0]
    return proc_dados

def treatNotificacao(proc_dados,texto):
    #fls_pattern = 'do Brasil\nFl. (.*)'
    nl_pattern = 'LANÇAMENTO Nº NLMIC - (\d+/\d{4})'
    nome_pattern = 'NOME EMPRESARIAL (.*)ENDER' # \n(.*)\n'
    data_pattern = '(\d{2}/\d{2}/\d{4})'#\n\d{2}:\d{2}:\d{2}\n(.+)\n'
    descricao_pattern = 'LEGAL DESCRIÇÃO DOS FATOS([\s\S]*)ENQUADRA'
    enquadramento_pattern = 'ENQUADRAMENTO LEGAL([\s\S]*)4 - DADOS'
    tipo_credito_pattern = 'TIPO DE CRÉDITO(.*)PROCESSO DE CRÉDITO'
    proc_credito_pattern = 'PROCESSO DE CRÉDITO(.*)DETENTOR'
    dcomp_pattern = '(\d{24})'
    valor_pattern = '([1-9]\d{0,2}(\.\d{0,3})*,\d{2})'
    #valor_pattern = '(\d{24})'
    #fls = list(re.findall(fls_pattern, nl_text))
    nl = re.findall(nl_pattern, texto)[0]
    nome = re.findall(nome_pattern, texto)[0]
    data = re.findall(data_pattern, texto)[0]
    descricao = re.findall(descricao_pattern, texto)[0]
    enquadramento = re.findall(enquadramento_pattern, texto)[0]
    tipo_credito = re.findall(tipo_credito_pattern, texto)[0]
    proc_credito = re.findall(proc_credito_pattern, texto)[0]
    dcomp = re.findall(dcomp_pattern, texto)[0]
    valor = re.findall(valor_pattern, texto)[0]
    #dados[proc_nr]['fls'] = fls
    proc_dados['nl'] = nl
    proc_dados['nome'] = nome
    proc_dados['data'] = data
    proc_dados['descricao'] = descricao
    proc_dados['enquadramento'] = enquadramento
    proc_dados['tipo_credito'] = tipo_credito
    proc_dados['proc_credito'] = proc_credito
    proc_dados['dcomp'] = [[dcomp,valor]]
    return proc_dados

def treatImpugnacao(proc_dados,texto):
    return True

def getImportDic(fpath,header):
    #''
    non_na_cols = ['unidade','proc_nr','ACT_tema','ACT_origem','ACT_tributo',\
                   'protocolo_data','he_decimal','he','apensado','ni','nome',\
                   'valor_origin','valor_processo']
    #''
    df = pd.read_csv(fpath,sep=';',header=0,names=header,na_filter=False,dtype='str')
    items_nr = len(df)
    import_data_dic = {}
    for c in df.columns:
        import_data_dic[c] = list(df[c])
    df1 = df[:100].copy() #df[non_na_cols]
    tab_dic = {}
    for c in df1.columns:
        tab_dic[c] = list(df1[c])
    return import_data_dic,tab_dic,items_nr

def tagProcByIA(proc_tipo):
    if (proc_tipo=='MultaCompNH'): ia_rotuling = tagProcByIA_MultaCompNH()
    elif (proc_tipo=='MalhaIRPF'): ia_rotuling = tagProcByIA_MalhaIRPF()
    return ia_rotuling

def getPageUrl(proc_tipo):
    if (proc_tipo=='MultaCompNH'): page = 'julga_MultaCompNH.html'
    elif (proc_tipo=='MalhaIRPF'): page = 'julga_MalhaIRPF.html'
    else: page = 'index.html'
    return page
'''


'''

def index(request):
    if Processo.objects.all().count()==0:
        populated_state = 0
        atxs = Autotexto.objects.all()
        atxs.delete()
        prs = ProcToRot.objects.all()
        prs.delete()
        rs = Rotulo.objects.all()
        rs.delete()
        pds = ProcToDoc.objects.all()
        pds.delete()
        ds = Documento.objects.all()
        ds.delete()
    elif Autotexto.objects.all().count()==0:
        populated_state = 1
        prs = ProcToRot.objects.all()
        prs.delete()
        rs = Rotulo.objects.all()
        rs.delete()
        pds = ProcToDoc.objects.all()
        pds.delete()
        ds = Documento.objects.all()
        ds.delete()
    elif Rotulo.objects.all().count()==0:
        populated_state = 2
        prs = ProcToRot.objects.all()
        prs.delete()
        pds = ProcToDoc.objects.all()
        pds.delete()
        ds = Documento.objects.all()
        ds.delete()
    elif Documento.objects.all().count()==0:
        populated_state = 3
        pds = ProcToDoc.objects.all()
        pds.delete()
    else:
        populated_state = 4
    print('Populated_State = ',populated_state)
    context = {'state':populated_state}
    return render(request, 'index.html', context)

def populateDB(request):
    state = int(request.POST['state'])
    print('State = ',state)
    if (state==0): populateProcessoDB()
    elif (state==1): populateAutotextoDB()
    elif (state==2): populateRotuloDB()
    elif (state==3): populateDocumentoDB(comp_dir,descomp_dir,done_dir)
    state = state + 1
    print('State = ',state)
    resp = {'state':state}
    return JsonResponse(resp)


def processos_MultaCompNH(request):
    proc_nr_list = ['11111.900111/2020-01','22222.900222/2020-02','33333.900333/2020-03']
    context = {'proc_nr_list':proc_nr_list}
    return render(request, 'processos_MultaCompNH.html', context)

def julga_MultaCompNH(request):
    nl_file = multa_comp_dir+'11080734483201851_000002_000003_COPIA_Notificação de Lançamento_20200402121043502.PDF'
    ciencia_file = multa_comp_dir+'11080734483201851_000006_000006_COPIA_Termo de Ciência por Abertura de Mensagem_20200402121043907.PDF'
    impugnacao_juntada_file = multa_comp_dir+'11080734483201851_000008_000009_COPIA_Termo de Análise de Solicitação de Juntada_20200402121044407.pdf'
    impugnacao_texto_file = multa_comp_dir+'11080734483201851_000010_000016_COPIA_Manifestação de Inconformidade_20200402121044529.PDF'
    nl_text,ciencia_text,juntada_text,impugnacao_text = '','','',''
    nl_text,ciencia_text,juntada_text,impugnacao_text = extract_text_from_pdf(nl_file),extract_text_from_pdf(ciencia_file),extract_text_from_pdf(impugnacao_juntada_file),extract_text_from_pdf(impugnacao_texto_file)
    data = getDataFromPdf_MultaCompNHom(nl_text,ciencia_text,juntada_text,impugnacao_text)
    atx_set = Autotexto.objects.all()
    tempestividade_atx_nome_list,tempestividade_atx_texto_list = [],[]
    proc_compensacao_atx_nome_list,proc_compensacao_atx_texto_list = [],[]
    impugnacao_atx_nome_list,impugnacao_atx_texto_list = [],[]
    preliminares_atx_nome_list,preliminares_atx_texto_list = [],[]
    merito_atx_nome_list,merito_atx_texto_list = [],[]
    outras_atx_nome_list,outras_atx_texto_list = [],[]
    for a in atx_set:
        if (a.secao_acordao_atx=='acordao'):
            tempestividade_atx_nome_list.append(a.nome_atx)
            tempestividade_atx_texto_list.append(a.texto_atx)    
        elif (a.secao_acordao_atx=='relatorio'):
            proc_compensacao_atx_nome_list.append(a.nome_atx)
            proc_compensacao_atx_texto_list.append(a.texto_atx)
            impugnacao_atx_nome_list.append(a.nome_atx)
            impugnacao_atx_texto_list.append(a.texto_atx)
        elif (a.secao_acordao_atx=='voto'):
            preliminares_atx_nome_list.append(a.nome_atx)
            preliminares_atx_texto_list.append(a.texto_atx)
            merito_atx_nome_list.append(a.nome_atx)
            merito_atx_texto_list.append(a.texto_atx)
            outras_atx_nome_list.append(a.nome_atx)
            outras_atx_texto_list.append(a.texto_atx)
    context = {'proc':data['proc'],\
               'ciencia':data['ciencia'],\
               'impugnacao':data['impugnacao'],\
               'notificacao':data['notificacao'],\
               'credito_proc':data['credito_proc'],\
               'perdcomps':data['perdcomps'],\
               'notif_descricao_text':data['notif_descricao_text'],\
               'notif_fundleg_text':data['notif_fundleg_text'],\
               'tempestividade_atx_nome_list':tempestividade_atx_nome_list,'tempestividade_atx_texto_list':tempestividade_atx_texto_list,\
               'proc_compensacao_atx_nome_list':proc_compensacao_atx_nome_list,'proc_compensacao_atx_texto_list':proc_compensacao_atx_texto_list,\
               'impugnacao_atx_nome_list':impugnacao_atx_nome_list,'impugnacao_atx_texto_list':impugnacao_atx_texto_list,\
               'preliminares_atx_nome_list':preliminares_atx_nome_list,'preliminares_atx_texto_list':preliminares_atx_texto_list,\
               'merito_atx_nome_list':merito_atx_nome_list,'merito_atx_texto_list':merito_atx_texto_list,\
               'outras_atx_nome_list':outras_atx_nome_list,'outras_atx_texto_list':outras_atx_texto_list,\
               'multa_dir':multa_comp_dir}
    return render(request, 'julga_MultaCompNH.html', context)



def processos_MalhaIRPF(request):
    proc_nr_list = ['11111.900111/2020-01','22222.900222/2020-02','33333.900333/2020-03']
    context = {'proc_nr_list':proc_nr_list}
    return render(request, 'processos_MalhaIRPF.html', context)

def julga_MalhaIRPF(request):
    #''
    proc_nr = request.POST['proc_nr']
    s = Processo.objects.get(proc_nr=p_nr)
    proc_nr = s.proc_nr
    #''
    proc_nr = '11111.900111/2020-01'
    atx_set = Autotexto.objects.all()
    tempestividade_atx_nome_list,tempestividade_atx_texto_list = [],[]
    impugnacao_atx_nome_list,impugnacao_atx_texto_list = [],[]
    preliminares_atx_nome_list,preliminares_atx_texto_list = [],[]
    merito_atx_nome_list,merito_atx_texto_list = [],[]
    outras_atx_nome_list,outras_atx_texto_list = [],[]
    for a in atx_set:
        if (a.capitulo=='acordao'):
            tempestividade_atx_nome_list.append(a.nome)
            tempestividade_atx_texto_list.append(a.texto)    
        elif (a.capitulo=='relatorio'):
            impugnacao_atx_nome_list.append(a.nome)
            impugnacao_atx_texto_list.append(a.texto)
        elif (a.capitulo=='voto'):
            preliminares_atx_nome_list.append(a.nome)
            preliminares_atx_texto_list.append(a.texto)
            merito_atx_nome_list.append(a.nome)
            merito_atx_texto_list.append(a.texto)
            outras_atx_nome_list.append(a.nome)
            outras_atx_texto_list.append(a.texto)
    context = {'proc_nr':proc_nr,\
               'tempestividade_atx_nome_list':tempestividade_atx_nome_list,'tempestividade_atx_texto_list':tempestividade_atx_texto_list,\
               'impugnacao_atx_nome_list':impugnacao_atx_nome_list,'impugnacao_atx_texto_list':impugnacao_atx_texto_list,\
               'preliminares_atx_nome_list':preliminares_atx_nome_list,'preliminares_atx_texto_list':preliminares_atx_texto_list,\
               'merito_atx_nome_list':merito_atx_nome_list,'merito_atx_texto_list':merito_atx_texto_list,\
               'outras_atx_nome_list':outras_atx_nome_list,'outras_atx_texto_list':outras_atx_texto_list,\
               }
    return render(request, 'julga_MalhaIRPF.html', context)

def xgetProcesses(request):
    proc_tipo = request.POST['proc_tipo']
    proc_list = getProcTreeFromLote(proc_tipo)
    resp = {'proc_list':proc_list}
    return JsonResponse(resp)

def xopenProcess(request):
    proc_tipo,proc_nr = request.GET['proc_tipo'],request.GET['proc_nr']
    dados = {}
    dados = getDataFromProc(proc_tipo,proc_nr,dados)
    print(proc_tipo,proc_nr)
    autotextos = getAtxsForProc(proc_tipo)
    rotulagem_ia = tagProcByIA(proc_tipo)
    page = getPageUrl(proc_tipo)
    context = {'proc_nr':proc_nr,'dados':dados,'autotextos':autotextos,'rotulagem_ia':rotulagem_ia}
    return render(request, page, context)


'''

