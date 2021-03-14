from django.shortcuts import render
from django.http import JsonResponse,HttpResponse
from .models import Project,Figure
from django.core.files import File

from lpscopmodelapp.modules import DWDj_DataImport as DI
from lpscopmodelapp.modules import DWDj_DescriptiveStats as DS
from lpscopmodelapp.modules import DWDj_MarginFitting as MF
from lpscopmodelapp.modules import DWDj_CopulaFitting as CF

import json
import re
import os
import pandas as pd
import tempfile as tf
import base64
import pickle as pk
from matplotlib import pyplot as plt
import numpy as np
import time
import sys
import multiprocessing as mpc
from multiprocessing import Process
from multiprocessing.queues import Queue
from threading import Thread
import mimetypes

######################################################################################################################
######          Linux Server LPS: line command for enablig port 8000 for access by Web browsers                 ######
###### sudo iptables -A IN_FedoraServer_allow -p tcp --dport 8000 -m conntrack --cstate NEW,UNTRACKED -j ACCEPT ######
###### NEVER FORGET: in TMUX specific session --> python manage.py runserver 0:8000                             ######
######################################################################################################################


##############################
###### GLOBAL VARIABLES ######
##############################

multiproc = False
proj_dir = os.path.abspath('.')
proj_static_dir = proj_dir+'/lpscopmodelapp/static/'
proj_data_dir = proj_static_dir+'data/'
img_dir = proj_static_dir+'images/'
map_dir = proj_static_dir+'maps/'
result_dir = proj_static_dir+'results/'
pkl_dir = proj_static_dir+'pkl/'
datasus_dbf_dir = proj_data_dir+'datasus/dbf/'
datasus_pkl_dir = proj_data_dir+'datasus/pkl/'
packs_dir = proj_dir+'/lpscopmodelapp/python_packs/'
task_output_fpath = result_dir+'task_output.pkl'
dataset_dir_dic = {'DATASUS':'datasus/','ForestFire':'forestfire/','OTHER':'other/'}
margin_mask = {'feature':'feature',\
              'var_type':'var_type',\
              'components':{'mtype':'empty','comps_nr':1,'params':[],'params_sd':[],'labels':[]},
              'mcmc':{'model_str':'empty','comps_nr':1,'samples_nr':200,'tune':100,'rounds_nr':0,\
                      'chains':2,'cores':2,'seed':20190415,'obs_mode':'full','obs_size':100000,'ppc_nr':2000,\
                      'trace':[],'mcmc_round':0,'round_trace':[],'round_summary':[],'round_accept_probs':[]}}
stage_dic = {'initial':0,'dataset_selection':0,
             'load_DATASUS':1,'load_toy_up':1,'load_toy_indep':1,'load_toy_down':1,'load_generic':1,
             'dataset_slicing':2,
             'descriptive_stats':2,
             'margin_modeling':3,
             'copula_modeling':4}
margin_fig_type_list = ['margin_histogram','margin_fitting','margin_conv']
cp = None
proj_list = None
proj_name = None
proj_name,fig_type_list = '',[]
fp = None
task_io,task_conn,exec_task = None,None,None

#######################################################################
############################## VIEWS ##################################
#######################################################################

###################
### INDEX PAGE ###
###################

def index(request):
    if (Project.objects.all().count()>0):
        proj_list = list(Project.objects.values_list('name', flat=True))
    else:
        proj_list = ['--no project stored--']
    context = {'proj_name':'--no project yet--','proj_list':proj_list,'proj_dir':proj_dir}
    return render(request, 'index.html', context)

def defineProj(request):
    global proj_name
    proj_name = request.POST['proj_name']
    session,proj_list = loadSession(proj_name)
    if ('stage' not in session.keys()):
        session['stage'] = 0
    saveSession(session)
    j_session = makeJSession(session)
    return JsonResponse({'proj_list':proj_list,'j_session':j_session})

def doModelingAction(request):
    global proj_name
    action = request.POST['action']
    if (action=='dataset_selection'): data = {}
    elif (action[:5]=='load_'):
        if (action=='load_DATASUS'): data = datasus_file_selection()
        elif (action=='load_toy_up'): data = load_toy_data('toy_up')
        elif (action=='load_toy_indep'): data = load_toy_data('toy_indep')
        elif (action=='load_toy_down'): data = load_toy_data('toy_down')
        else: data = {}
    elif (action=='dataset_slicing'): data = {}
    elif (action=='descriptive_stats'): data = descriptive_stats(request)
    elif (action=='margin_modeling'): data = {}
    elif (action=='copula_modeling'): data = {}
    else: data = {}
    '''
    if (action not in ['margin_modeling','copula_modeling']): # those depends on further processing to be completed
        session['stage'] = stage_dic[action]
    saveSession(session)
    '''
    session,_ = loadSession(proj_name)
    data['stage'] = session['stage']
    resp = data
    return JsonResponse(resp)


##############################
### TOYDATA SELECTION PAGE ###
##############################

def load_toy_data(dataset):
    global proj_name
    session,_ = loadSession(proj_name)
    space_feat = ['AC','AM','AP','BA','CE','DF','ES','GO','MA','MG','MS','MT','PA','PB','PE','PI,''PR','RO','RR','SC','SE','SP','TO']
    time_feat = ['2008','2009','2010']
    if (dataset=='toy_up'): x = [[i+1,3*(i+1),space_feat[np.random.randint(len(space_feat))],time_feat[np.random.randint(len(time_feat))]] for i in range(1000)]
    elif (dataset=='toy_indep'): x = [[np.random.choice(1000,replace=False),np.random.choice(1000,replace=False),space_feat[np.random.randint(len(space_feat))],time_feat[np.random.randint(len(time_feat))]] for i in range(1000)]
    elif (dataset=='toy_down'): x = [[i+1,3*(999-i),space_feat[np.random.randint(len(space_feat))],time_feat[np.random.randint(len(time_feat))]] for i in range(1000)]
    df = pd.DataFrame(x,columns=['feature_1','feature_2','space','time'])
    feature_list = list(df.columns)
    val_mtx_np = df.to_numpy()
    val_mtx = val_mtx_np.tolist()
    value_list = [list(set(val_mtx_np[:,i])) for i in range(val_mtx_np.shape[1])]
    session['feature_list'] = feature_list
    session['val_mtx'] = val_mtx
    session['value_list'] = value_list
    session['filter_text'] = ''
    margins = {}
    for f in feature_list:
        margin = margin_mask.copy()
        if (f in ['space','time']): margin['var_type'] = 'cat'
        else: margin['var_type'] = 'num'
        margins[f] = margin
    session['margins'] = margins
    session['df_pklfname'] = pkl_dir+'df.pkl'
    savePKL(df,session['df_pklfname'])
    session['stage'] = 1
    saveSession(session)
    return {}

##############################
### DATASUS SELECTION PAGE ###
##############################

def datasus_file_selection():
    global proj_name,fp
    session,_ = loadSession(proj_name)
    fp = DI.DW_Copula_DatasusImport(datasus_pkl_dir) #,fname_mask_pkl='DATASUS_REDUCED_YYYY_UF',fname_mask_dbf='TPUFYYMM'
    session['file_list'] = fp.file_list
    dataset_list = sorted(fp.dataset_list)
    datatype_list = ['pkl'] #sorted(list({'pkl','parquet','dbf'}.intersection(set(fp.datatype_list))),reverse=True)
    type_list = sorted(fp.type_list)
    uf_list = sorted(fp.uf_list)
    year_list = sorted(fp.year_list)
    month_list = sorted(fp.month_list)
    saveSession(session)
    data = {
        'proj_name':session['proj_name'],
        'dataset_list':dataset_list,
        'datatype_list':datatype_list,
        'type_list':type_list,
        'year_list':year_list,
        'uf_list':uf_list,
        'month_list':month_list,
    }
    return data

def selectDataFileOptions(request):
    global proj_name,fp
    session,_ = loadSession(proj_name)
    dataset = request.POST['dataset']
    datatype = request.POST['datatype']
    data_dir = proj_data_dir+dataset_dir_dic[dataset]
    if (datatype=='dbf'): data_dir = data_dir+'dbf/'
    else: data_dir = data_dir+'pkl/'
    session['data_dir'] = data_dir
    fp = DI.DW_Copula_DatasusImport(data_dir)
    session['file_list'] = fp.file_list
    dataset_list = sorted(fp.dataset_list)
    datatype_list = sorted(fp.datatype_list)
    type_list = sorted(fp.type_list)
    uf_list = sorted(fp.uf_list)
    year_list = sorted(fp.year_list)
    month_list = sorted(fp.month_list)
    saveSession(session)
    resp = {
        'proj_name':session['proj_name'],
        'dataset_list':dataset_list,
        'datatype_list':datatype_list,
        'type_list':type_list,
        'year_list':year_list,
        'uf_list':uf_list,
        'month_list':month_list,
        }
    return JsonResponse(resp)


########################
### DATA ACQUISITION ###
########################

def data_acquisition(request):
    global proj_name,fp,task_io,task_conn,exec_task
    session,_ = loadSession(proj_name)
    file_list = session['file_list']
    req = json.loads(request.POST['jreq'])
    if (multiproc):
        task_io,task_conn,exec_task = controlTask(fp.loadDatasusFromFiles,{'req':req,'file_list':file_list})
    else:
        df = fp.loadDatasusFromFiles(req=req,file_list=file_list)
        with open(task_output_fpath,'wb') as f:
            pk.dump(df.to_dict(),f)
    resp = {}
    return JsonResponse(resp)

def data_acquisition_end(request):
    global proj_name
    session,_ = loadSession(proj_name)
    if (multiproc):
        out_dic = task_conn.recv()
        if out_dic['out_type']=='pandas_df':
            with open(out_dic['out'],'rb') as f:
                df_dic = pk.load(f)
            df = pd.DataFrame.from_dict(df_dic)
        else: df = pd.DataFrame()
    else:
        with open(task_output_fpath,'rb') as f:
            df_dic = pk.load(f)
        df = pd.DataFrame.from_dict(df_dic)
    feature_list,val_mtx,value_list = readDataFromDf(session,df)
    session['feature_list'] = feature_list
    session['val_mtx'] = val_mtx
    session['value_list'] = value_list
    session['df_pklfname'] = pkl_dir+'df.pkl'
    session['stage'] = 1
    savePKL(df,session['df_pklfname'])
    saveSession(session)
    return JsonResponse({})


#############################
##### DATA SLICING PAGE #####
#############################

def load_data_slicing(request):
    global proj_name
    session,_ = loadSession(proj_name)
    df = loadPKL(session['df_pklfname'])
    feature_list = session['feature_list']
    filter_list = feature_list
    val_mtx = session['val_mtx']
    value_list = session['value_list']
    val_mtx_str,value_list_str = ListMtxToStr(val_mtx),ListMtxToStr(value_list)
    example_raw = df[0:5].to_string().replace('\n', '<br>')
    pattern = re.compile(r' +')
    example = re.sub(pattern, ' ', example_raw)
    resp = {
        'proj_name':session['proj_name'],
        'proj_list':proj_list,
        'feature_list':feature_list,
        'filter_list':filter_list,
        'val_mtx':val_mtx_str,
        'value_list':value_list_str,
        'example':example,
        }
    return JsonResponse(resp)

def selectData(request):
    global proj_name
    session,_ = loadSession(proj_name)
    filter_text = request.POST['filter_text']
    slicing_text = request.POST['slicing_text']
    time_col = request.POST['time_col']
    space_col = request.POST['space_col']
    session['time_col'],session['space_col'] = time_col,space_col
    in_df = loadPKL(session['df_pklfname'])
    df,var_type_dic,val_mtx,feature_list = DI.selectData(in_df,filter_text,slicing_text,time_col,space_col)
    margins = {}
    for f in feature_list:
        margin = margin_mask.copy()
        margin['feature'] = f
        margin['var_type'] = var_type_dic[f]
        margins[f] = margin
    session['filter_text'] = filter_text
    session['feature_list'] = feature_list
    session['val_mtx'] = val_mtx
    session['margins'] = margins
    savePKL(df,session['df_pklfname'])
    session['stage'] = 2
    saveSession(session)
    resp = {'proj_list':proj_list,'feature_list':feature_list,'val_mtx':val_mtx}
    return JsonResponse(resp)


### FOREST IMPORT PAGE ###
def forest_import(request):
    df = pd.DataFrame([[11,22],[33,44]])
    #df = df.from_csv('static/data/ForestFire/forestfires.csv')
    data_tab = df.to_numpy()
    resp = {'data_tab':data_tab}
    return JsonResponse(resp)


###################################
### DESCRIPTIVE STATISTICS PAGE ###
###################################
    
def descriptive_stats(request):
    global proj_name
    session,_ = loadSession(proj_name)
    proj_name = session['proj_name']
    feature_list,margins = session['feature_list'],session['margins']
    data = {'proj_name':proj_name,'feature_list':feature_list,'proj_list':proj_list,'margins':margins}
    return data

def make_description(request):
    global proj_name,fig_type_list
    session,_ = loadSession(proj_name)
    feature = request.POST['feature']
    proj_name = session['proj_name']
    feature_list = session['feature_list']
    df = loadPKL(session['df_pklfname'])
    filter_text = session['filter_text']
    margins = session['margins']
    margin = margins[feature]
    var_type = margin['var_type']
    time_col,space_col = session['time_col'],session['space_col']
    fig_list,fig_type_list,conc_mtx = DS.doTotalDescription(df,feature,var_type,filter_text,proj_name,map_dir,time_col,space_col)
    doSaveFigures(fig_list,fig_type_list,feature,proj_name)
    fig_type_list = fig_type_list
    conc_mtx = [[str(conc_mtx[i][j]) for j in range(len(conc_mtx[i]))] for i in range(len(conc_mtx))]
    describe = df[feature].describe()
    x,y = list(describe.keys()),list(describe.values)
    if (var_type=='num'): val_mtx = [[x[i],str(round(y[i],2))] for i in range(len(x))]
    else: val_mtx = [[x[i],str(y[i])] for i in range(len(x))]
    session['conc_mtx'] = conc_mtx
    saveSession(session)
    resp = {'val_mtx':val_mtx,'feature_list':feature_list,'conc_mtx':conc_mtx,'fig_type_list':fig_type_list}
    return JsonResponse(resp)

def sendFigure(request):
    global proj_name,fig_type_list
    session,_ = loadSession(proj_name)
    feature = request.POST['feature']
    proj_name = session['proj_name']
    fig_type = fig_type_list[int(request.POST['fig_id'])]
    img_data = loadResultFigure(proj_name,feature+'_'+fig_type+'.png')
    img_data_uri = base64.b64encode(img_data).decode('ascii')
    response = HttpResponse(content_type="application/octet-stream")
    response['Content-Disposition'] = 'attachment; filename=hist.zip'
    response.write(img_data_uri)
    return response


############################
### MARGIN MODELING PAGE ###    
############################

def loadMarginStartData(request):
    global proj_name
    session,_ = loadSession(proj_name)
    feature = request.POST['feature']
    session['feature'] = feature
    margin = session['margins'][feature]
    if margin['var_type']=='num':
        mcmc_go = 1
        df = loadPKL(session['df_pklfname'])
        obs = np.array(df[feature])
        auto_comps_nr = MF.computeModes(obs)
    else:
        mcmc_go = 0
        auto_comps_nr = 1
    saveSession(session)
    resp = {'mcmc_go':mcmc_go,'auto_comps_nr':auto_comps_nr}
    return JsonResponse(resp)
    
def loadMCMCParams(request):
    global proj_name
    session,_ = loadSession(proj_name)
    feature = session['feature']
    margin = session['margins'][feature]
    margin['mcmc']['model_str'] = request.POST['model_str']
    if (request.POST['comps_nr']=='auto'): margin['mcmc']['comps_nr'] = session['auto_comps_nr']
    else: margin['mcmc']['comps_nr'] = int(request.POST['comps_nr'])
    margin['mcmc']['rounds_nr'] = int(request.POST['rounds_nr'])
    margin['mcmc']['samples_nr'] = int(request.POST['samples_nr'])
    margin['mcmc']['tune'] = int(request.POST['tune'])
    margin['mcmc']['mcmc_round'] = int(request.POST['mcmc_round'])
    session['margins'][feature] = margin
    saveSession(session)
    resp = {}
    return JsonResponse(resp)

def makeMCMCMargin(request):
    global proj_name,task_io,task_conn,exec_task,next_task
    session,_ = loadSession(proj_name)
    feature = session['feature']
    margin = session['margins'][feature]
    df = loadPKL(session['df_pklfname'])
    obs = np.array(df[feature])
    if (multiproc):
        task_io,task_conn,exec_task = controlTask(MF.estimateNumMargin,{'obs':obs,'margin':margin})
    else:
        margin = MF.estimateNumMargin(obs=obs,margin=margin)
        with open(task_output_fpath,'wb') as f:
            pk.dump(margin,f)
    resp = {}
    return JsonResponse(resp)

def makeMCMCMargin_end(request):
    global proj_name,task_conn
    session,_ = loadSession(proj_name)
    feature = session['feature']
    if (multiproc):
        margin_pkl_fpath = task_conn.recv()['out']
        with open(margin_pkl_fpath,'rb') as f:
            margin = pk.load(f)
        #margin = task_conn.recv()['out']
    else:
        with open(task_output_fpath,'rb') as f:
            margin = pk.load(f)
    session['margins'][feature] = margin
    session['stage'] = 3
    saveSession(session)
    return JsonResponse({})

def makeMargin_end(request):
    global proj_name
    session,_ = loadSession(proj_name)
    df = loadPKL(session['df_pklfname'])
    feature = session['feature']
    obs = np.array(df[feature])
    margin = session['margins'][feature]
    var_type = margin['var_type']
    if var_type=='cat': margin = MF.estimateCatMargin(obs,margin) #comps=
    proj_name = session['proj_name']
    filter_text = session['filter_text']
    x_list=list(df[feature])
    fig_hist = DS.makeHistogram(x_list=x_list,feature=feature,ftype=var_type,filter_text=filter_text)
    fig_fitting = MF.plotMarginFitting(feature,obs,margin)
    if margin['var_type']=='num':
        trace,c_nr = margin['components']['trace'],margin['components']['comps_nr']
        fig_traces = MF.plotTraces(trace,c_nr)
    else: fig_traces = fig_fitting
    fig_list = [fig_hist,fig_fitting,fig_traces]
    doSaveFigures(fig_list,margin_fig_type_list,feature,proj_name)
    session['margins'][feature] = margin
    feature_list = list(df.columns) + ['space','time']
    if (len(session['margins'])==len(feature_list)): session['stage'] = stage_dic['margin_modeling']
    saveSession(session)
    components = margin['components']
    labels = components['labels']
    params,params_sd = [],[]
    for c_id in range(components['comps_nr']):
        params.append([str(round(x,5)) for x in components['params'][c_id]])
        params_sd.append([str(round(x,5)) for x in components['params_sd'][c_id]])
    resp = {'figs_nr':len(margin_fig_type_list),'labels':labels,'params':params,'params_std':params_sd}
    return JsonResponse(resp)

def sendMarginFigure(request):
    global proj_name
    session,_ = loadSession(proj_name)
    fig_id = int(request.POST['fig_id'])
    proj_name = session['proj_name']
    feature = session['feature']
    #fig_type = session['fig_type_list'][fig_id]
    fig_type = margin_fig_type_list[fig_id]
    img_data = loadResultFigure(proj_name,feature+'_'+fig_type+'.png')
    img_data_uri = base64.b64encode(img_data).decode('ascii')
    response = HttpResponse(content_type="application/octet-stream")
    response['Content-Disposition'] = 'attachment; filename=hist.zip'
    response.write(img_data_uri)
    return response


############################
### COPULA MODELING PAGE ###    
############################

def copula_modeling(request):
    global proj_name
    session,_ = loadSession(proj_name)
    margins = session['margins']
    status = 'all'
    for f,margin in margins.items():
        if margin['components']['mtype']=='empty':
            status = 'incomplete'
            break
    if status=='all':
        feature_list,ctype = modelCopula()
    else:
        feature_list,ctype = [],''
    resp = {'margin_status':status,'feature_list':feature_list,'ctype':ctype}
    return JsonResponse(resp)

def modelCopula():
    print('modelCopula')
    global proj_name
    session,_ = loadSession(proj_name)
    proj_name = session['proj_name']
    feature_list = session['feature_list']
    df = loadPKL(session['df_pklfname'])
    print('df loaded')
    dtypes = [m['components']['mtype'] for f,m in session['margins'].items()]
    params = [m['components']['params'] for f,m in session['margins'].items()]
    copula = CF.modelCopula(mvsample=df.to_numpy(copy=True),dtypes=dtypes,params=params,features=feature_list)
    #with open(pkl_dir+proj_name+'_copula.pkl','wb') as f: --- not working because of pymc3/stats local classes (not pickable)
    #    pk.dump(copula,f)
    session['margins_tab'] = copula.margins_tab.tolist()
    session['copula_tab'] = copula.copula_tab.tolist()
    session['stage'] = stage_dic['copula_modeling']
    session['stage'] = 4
    saveSession(session)
    for d1 in range(copula.D):
        for d2 in range(copula.D):
            for fig_type in ['surface','levels']:
                fig_partial_fname = 'copula_'+fig_type+'_'+str(d1)+'_'+str(d2)+'.png'
                fpath = result_dir+proj_name+'_'+fig_partial_fname
                if (os.path.exists(fpath)):
                    os.remove(fpath)
    for i in range(min(copula.D-1,3)): # initial figures: first (at most) 3 features
        d1,d2 = i,i+1
        makeCopulaFigs(proj_name,d1,d2,copula)
        print('fig'+str(i))
    return feature_list,copula.ctype

def sendCopulaFigure(request):
    global proj_name
    session,_ = loadSession(proj_name)
    d_lim = len(session['feature_list'])-1
    #proj_name = session['proj_name']
    d1,d2,fig_type = int(request.POST['d1']),int(request.POST['d2']),request.POST['fig_type']
    d1,d2 = validate2DChoice(d1,d2,d_lim)
    fig_partial_fname = 'copula_'+fig_type+'_'+str(d1)+'_'+str(d2)+'.png'
    if not (os.path.exists(result_dir+proj_name+'_'+fig_partial_fname)):
        mvsample,ms,margins_tab,copula_tab = makeCopulaParams(session)
        copula = CF.Copula(sample=mvsample, margins=ms, margins_tab=margins_tab, copula_tab=copula_tab)
        makeCopulaFigs(proj_name,d1,d2,copula)
    img_data = loadResultFigure(proj_name,fig_partial_fname)
    img_data_uri = base64.b64encode(img_data).decode('ascii')
    http_response = HttpResponse(content_type="application/octet-stream")
    http_response['Content-Disposition'] = 'attachment; filename=hist.zip'
    http_response.write(img_data_uri)
    return http_response

def validate2DChoice(d1, d2, d_lim):
    if (d1>d2):
        d0 = d1
        d1,d2 = d2,d0
    elif (d1==d2): d2 = d1+1
    if d2>d_lim:
        d1, d2 = d_lim-1, d_lim
    return d1,d2

def makeCopulaParams(session):
    feature_list,margins,margins_tab,copula_tab = session['feature_list'],session['margins'],np.array(session['margins_tab']),np.array(session['copula_tab'])
    df = loadPKL(session['df_pklfname'])
    mvsample=df.to_numpy(copy=True)
    dtypes = [m['components']['mtype'] for f,m in margins.items()]
    params = [m['components']['params'] for f,m in margins.items()]
    ms = [CF.Margin(sample=mvsample[:,i],dtype=dtypes[i],params=params[i],feature=feature_list[i]) for i in range(mvsample.shape[1])]
    return mvsample,ms,margins_tab,copula_tab

def makeCopulaFigs(proj_name,d1,d2,copula):
    fig_partial_fname1,fig_partial_fname2 = 'copula_surface_'+str(d1)+'_'+str(d2)+'.png','copula_levels_'+str(d1)+'_'+str(d2)+'.png'
    fig1,fig2 = copula.plotGraphics(d1,d2)
    saveResultFigure(proj_name,fig_partial_fname1,fig1)
    saveResultFigure(proj_name,fig_partial_fname2,fig2)
    return True


#################################
######## DOWNLOAD/UPLOAD ########
#################################

def doUploadDataset(request):
    global proj_name
    session,_ = loadSession(proj_name)
    inmemory_file = request.FILES['file']
    upfile = File(inmemory_file)
    with open('upfile','wb+') as ftemp:
        for chunk in upfile.chunks():
            ftemp.write(chunk)
    if (upfile.name[-3:]=='pkl'):
        df = pd.read_pickle('upfile')
    else:
        df = pd.read_csv('upfile',sep=';',thousands='.', decimal=',')
    for i in range(len(df.columns)):
        col = df.columns[i]
        if (df[col].dtype in [np.dtype('float64'),np.dtype('int64')]): df[col].fillna(0,inplace=True)
    feature_list,val_mtx,value_list = readDataFromDf(session,df)
    session['feature_list'] = feature_list
    session['val_mtx'] = val_mtx
    session['value_list'] = value_list
    session['df_pklfname'] = pkl_dir+'df.pkl'
    session['stage'] = 1
    savePKL(df,session['df_pklfname'])
    saveSession(session)
    return JsonResponse({})

def doDownloadResults(request): #,filepath
    downloaded_fname = proj_name+'_session.pkl'
    fpath_to_download = pkl_dir+downloaded_fname
    with open(fpath_to_download, 'rb') as f:
        mime_type,_ = mimetypes.guess_type(fpath_to_download)
        response = HttpResponse(f, content_type='application/octet-stream') #mime_type)
    response['Content-Disposition'] = 'attachment; filename=%s' % downloaded_fname
    return response

def doClearProjects(request):
    fs = Figure.objects.all()
    fs.delete()
    ps = Project.objects.all()
    ps.delete()
    proj_list = ['--no project stored--']
    resp = {'proj_name':'--no project yet--','proj_list':proj_list}
    return JsonResponse(resp)


#################################
###### AUXILIARY FUNCTIONS ######
#################################

def saveSession(session,pkl_dir=pkl_dir):
    proj_name = session['proj_name']
    pkl_file = pkl_dir+proj_name+'_session.pkl'
    ss = Project.objects.filter(name=proj_name)
    if (ss.count()>0):
        s = ss[0]
    else:
        s = Project(name=proj_name)
    if ('df_pklfname' in session.keys()): s.df_pklfname = session['df_pklfname']
    if ('file_list' in session.keys()): s.file_list = json.dumps(session['file_list'])
    if ('filter_text' in session.keys()): s.filter_text = json.dumps(session['filter_text'])
    if ('feature_list' in session.keys()): s.feature_list = json.dumps(session['feature_list'])
    if ('value_list' in session.keys()): s.value_list = json.dumps(session['value_list'])
    if ('val_mtx' in session.keys()): s.val_mtx = json.dumps(session['val_mtx'])
    if ('conc_mtx' in session.keys()): s.conc_mtx = json.dumps(session['conc_mtx'])
    if ('margins' in session.keys()): s.margins = json.dumps(session['margins'])
    if ('feature' in session.keys()): s.feature = json.dumps(session['feature'])
    if ('space_col' in session.keys()): s.space_col = session['space_col']
    if ('time_col' in session.keys()): s.time_col = session['time_col']
    if ('margins_tab' in session.keys()): s.margins_tab = json.dumps(session['margins_tab'])
    if ('copula_tab' in session.keys()): s.copula_tab = json.dumps(session['copula_tab'])
    if ('stage' in session.keys()): s.stage = session['stage']
    s.save()
    try:
        os.remove(pkl_file)
    except:
        pass
    #copula_fpath = pkl_dir+proj_name+'_copula.pkl' --- not working because of pymc3/stats local classes (not pickable)
    #if (os.path.exists(copula_fpath)):
    #    with open(copula_fpath,'rb') as f:
    #        copula = pk.load(f)
    #        session['copula'] = copula
    with open(pkl_file,'wb') as f:
        pk.dump(session,f)
    proj_list = list(Project.objects.values_list('name', flat=True))
    return proj_list

def loadSession(proj_name):
    ss = Project.objects.filter(name=proj_name)
    if (ss.count()>0):
        s = ss[0]
        ssn = {'proj_name':s.name}
        ssn['df_pklfname'] = s.df_pklfname
        ssn['file_list'] = json.loads(s.file_list)
        ssn['filter_text'] = json.loads(s.filter_text)
        ssn['feature_list'] = json.loads(s.feature_list)
        ssn['value_list'] = json.loads(s.value_list)
        ssn['val_mtx'] = json.loads(s.val_mtx)
        ssn['conc_mtx'] = json.loads(s.conc_mtx)
        ssn['margins'] = json.loads(s.margins)
        ssn['feature'] = json.loads(s.feature)
        ssn['space_col'] = s.space_col
        ssn['time_col'] = s.time_col
        ssn['margins_tab'] = json.loads(s.margins_tab)
        ssn['copula_tab'] = json.loads(s.copula_tab)
        ssn['stage'] = s.stage
    else:
        ssn = {'proj_name':proj_name}
    proj_list = list(Project.objects.values_list('name', flat=True))
    return ssn,proj_list

def makeJSession(session):
    s = {'proj_name':'','filter_text':'','feature_list':[],'value_list':[],'val_mtx':[],'feature':'','space_col':'','time_col':'','stage':0,'margins_modeled':[]}
    for v in s.keys():
        if (v in session.keys()): s[v] = session[v]
    if ('margins' in session.keys()):
        margins = session['margins']
        for f in margins.keys():
            if margins[f]['components']['mtype']!='empty':
                s['margins_modeled'].append(f)
    j_session = json.dumps(s)
    return j_session

def saveResultFigure(proj_name,figname,fig,result_dir=result_dir):
    q = Figure.objects.filter(proj_name=proj_name,fname=figname)
    if (q.count()>0):
        f = q.first()
    else:
        f = Figure(proj_name=proj_name,fname=figname)
    ftemp = tf.TemporaryFile()
    fig.savefig(ftemp)
    fig.savefig(result_dir+proj_name+'_'+figname)
    plt.close()
    ftemp.seek(0)
    f.fbody = ftemp.read()
    ftemp.close()
    f.save()
    return True

def loadResultFigure(proj_name,figname):
    q = Figure.objects.filter(proj_name=proj_name,fname=figname)
    if (q.count()>0):
        f = q.first()
        img_data = f.fbody
    else:
        img_data = None
    return img_data

def doSaveFigures(fig_list,fig_type_list,feature,proj_name):
    for fig_id in range(len(fig_list)):
        fig,fig_type = fig_list[fig_id],fig_type_list[fig_id]
        saveResultFigure(proj_name,feature+'_'+fig_type+'.png',fig)
    return True

def savePKL(x, pklfname):
    try:
        os.remove(pklfname)
    except:
        pass
    with open(pklfname,'wb') as f:
        pk.dump(x,f)
    return True

def loadPKL(pklfname):
    with open(pklfname,'rb') as f:
        x = pk.load(f)
    return x

def ListMtxToStr(mtx):
    signif_digs = 5 # significative digits wanted
    mtx_str = []
    for l in mtx:
        if (type(l) is list):
            l_str = []
            for ll in l:
                if type(ll) in [int,float]:
                    ll_rounded = roundToSignif(ll,signif_digs)
                    l_str.append(str(ll_rounded))
                else: l_str.append(ll)
            mtx_str.append(l_str)
        else:
            if type(l) in [int,float]:
                l_rounded = roundToSignif(l,signif_digs)
                mtx_str.append(str(l_rounded))
            else: mtx_str.append(l)
    return mtx_str

def roundToSignif(x,signif_digs):
    import math
    x = float(x)
    if x==0: x_round=0.0
    else: x_round = round(x, signif_digs-int(math.floor(math.log10(abs(x))))-1)
    return x_round

def doDescription(df,feature,var_type,filter_text,sname):
    x_list=list(df[feature])
    fig_hist = DS.makeHistogram(x_list=x_list,feature=feature,ftype=var_type,filter_text=filter_text)
    fig_boxplot = DS.makeBoxplot(x_list=x_list,feature=feature,ftype=var_type,filter_text=filter_text)
    time_list,time_dict = sorted(list(set(df['time']))),{}
    for t in time_list: time_dict[t]=list(df[df['time']==t][feature])
    fig_timeserie = DS.makeTimeSerie(time_dict=time_dict,feature=feature,ftype=var_type,filter_text=filter_text)
    fig_spacemap = DS.makeSpaceMap(df=df,feature=feature,ftype=var_type,filter_text=filter_text,map_dir=map_dir)
    fig_list = [fig_hist,fig_boxplot,fig_timeserie,fig_spacemap]
    conc_mtx = DS.makeConcordances(df=df)
    return fig_list,conc_mtx

def readDataFromDf(session,df):
    feature_list = list(df.columns)
    val_mtx_np = df.to_numpy()
    val_mtx = val_mtx_np.tolist()
    value_list = [sorted(list(set(val_mtx_np[:,i]))) for i in range(val_mtx_np.shape[1])]
    return feature_list,val_mtx,value_list

### ------------------------------------------ ###
### multiprocessing and communicating progress ###
### ------------------------------------------ ###

# This is a Queue that behaves like stdout
class StdoutQueue(Queue):
    def __init__(self, maxsize=-1, block=True, timeout=None):
        self.block = block
        self.timeout = timeout
        super().__init__(maxsize, ctx=mpc.get_context())
    def write(self,msg):
        self.put(msg)
    def flush(self):
        sys.__stdout__.flush()

def text_catcher(text_storage,queue,exec_task):
    while exec_task.is_alive():
        msg = queue.get()
        if (len(msg)>0 and msg!='\n'):
            text_storage.append({'io':msg})

def childTask(q,task_conn,task,task_kwargs):
    stdout_std,stderr_std = sys.stdout,sys.stderr
    sys.stdout,sys.stderr = q,q
    task_output = task(**task_kwargs)
    sys.stdout,sys.stderr = stdout_std,stderr_std
    time.sleep(1)
    if (type(task_output)==pd.core.frame.DataFrame):
        with open(task_output_fpath,'wb') as f:
            pk.dump(task_output.to_dict(),f)
        output_dic = {'out_type':'pandas_df','out':task_output_fpath}
        task_conn.send(output_dic)
    else:
        with open(task_output_fpath,'wb') as f:
            pk.dump(task_output,f)
        output_dic = {'out_type':'general','out':task_output_fpath}
        task_conn.send(output_dic)
    print('CONN SEND')
    task_conn.close()

def parentTask(q,task,task_kwargs):
    parent_conn, child_conn = mpc.Pipe()
    exec_task = Process(target=childTask,args=(q,child_conn,task,task_kwargs),daemon=False)
    return parent_conn,exec_task

def controlTask(task,task_kwargs):
    task_io = []
    q = StdoutQueue()
    parent_conn,exec_task = parentTask(q,task,task_kwargs)
    monitor = Thread(target=text_catcher,args=(task_io,q,exec_task))
    monitor.daemon = True
    exec_task.start()
    monitor.start()
    return task_io,parent_conn,exec_task

def waitProcessing(request):
    if (multiproc):
        global session,task_io,task_conn,exec_task
        time.sleep(1)
        if (task_io!=None and len(task_io)>0):
            msg = task_io[-1]['io']
        else:
            msg = '...'
        if exec_task.is_alive():
            resp = {'exec_status':'ongoing','msg':msg,'task_id':str(exec_task.ident)}
        else:
            resp = {'exec_status':'done','msg':''}
        print(resp['exec_status'],': ',msg)
    else:
        resp = {'exec_status':'done','msg':''}
    return JsonResponse(resp)
