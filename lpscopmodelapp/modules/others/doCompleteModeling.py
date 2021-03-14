#import re
import os
import pandas as pd
import pickle as pk
from matplotlib import pyplot as plt
import numpy as np
import DWDj_DataImport as DI
import DWDj_DescriptiveStats as DS
import DWDj_MarginFitting as MF
import DWDj_CopulaFitting as CF
import matplotlib as mpl
mpl.use('Agg')

# Create your views here.

##############################
###### GLOBAL VARIABLES ######
##############################

proj_dir = '/home/willian/Desktop/Doutorado_GDrive/Tese/Experimentos/Codigo/WebInterface/uspdarwin'
data_dir = proj_dir+'/uspdarwinapp/static/data/'
img_dir = proj_dir+'/uspdarwinapp/static/images/'
map_dir = proj_dir+'/uspdarwinapp/static/maps/'
result_dir = proj_dir+'/uspdarwinapp/static/results/'
pkl_dir = proj_dir+'/uspdarwinapp/static/pkl/'
packs_dir = proj_dir+'/uspdarwinapp/python_packs/'
margin_mask = {'feature':'feature',\
              'var_type':'var_type',\
              'components':{'mtype':'empty',\
                            'comps_nr':1,\
                            'params':[],\
                            'params_sd':[],\
                            'labels':[]
                            },
              'mcmc':{'model_str':'empty',\
                      'comps_nr':1,\
                      'samples_nr':200,\
                      'tune':100,\
                      'rounds_nr':0,\
                      'trace':[],
                      'mcmc_round':0,\
                      'round_trace':[],\
                      'round_summary':[],\
                      'round_accept_probs':[]
                      }
                }

# 'filter_text':'UF_ZI=120000; '
# 'year_list':['2008'],\#,'2009','2010','2011','2012','2013','2014','2015','2016','2017','2018'],\
# 'uf_list':['AC','AL','AM','AP','BA','CE','DF','ES','GO','MA','MG','MS','MT','PA','PB','PE','PI','PR','RJ','RN','RO','RR','RS','SC','SE','SP','TO'],\
proj_params = {'req':{'dataset_list':['datasus','forestfire'],\
                      'datatype_list':['dbf','pkl'],\
                      'dataset':'datasus',\
                      'datatype':'dbf',\
                      'time_feature':'MES_CMPT',\
                      'space_feature':'UF_ZI',\
                      'type_list':['RD'],\
                      'uf_list':['AC','AM','DF','ES','PB','SC','TO'],\
                      'year_list':['2008'],\
                      'month_list':['01','02','03','04','05','06','07','08','09','10','11','12']},\
               'filter_text':'',\
               'slicing_text':'UF_ZI;ANO_CMPT;SEXO;US_TOT;IDADE;DIAS_PERM;MORTE;',\
               'mcmc':{'US_TOT':\
                       {'model_str':'Beta',\
                       'comps_nr':1,\
                       'samples_nr':5000,\
                       'tune':2000,\
                       'chains':2,\
                       'cores':2,\
                       'seed':20190415,\
                       'obs_mode':'sample',\
                       'obs_size':10000,\
                       'ppc_nr':2000\
                       },
                       'IDADE':\
                       {'model_str':'Beta',\
                       'comps_nr':3,\
                       'samples_nr':5000,\
                       'tune':2000,\
                       'chains':2,\
                       'cores':2,\
                       'seed':20190415,\
                       'obs_mode':'sample',\
                       'obs_size':10000,\
                       'ppc_nr':2000\
                       },
                       'DIAS_PERM':\
                       {'model_str':'Beta',\
                       'comps_nr':1,\
                       'samples_nr':5000,\
                       'tune':2000,\
                       'chains':2,\
                       'cores':2,\
                       'seed':20190415,\
                       'obs_mode':'sample',\
                       'obs_size':10000,\
                       'ppc_nr':2000\
                       }}
               }


#################################
###### AUXILIARY FUNCTIONS ######
#################################

def saveSession(session,pkl_dir=pkl_dir):
    sname = session['sname']
    pkl_file = pkl_dir+sname+'_session.pkl'
    try:
        os.remove(pkl_file)
    except:
        pass
    with open(pkl_file,'wb') as f:
        pk.dump(session,f)
    return True

def saveResultFigure(sname,figname,fig,result_dir=result_dir):
    fig.savefig(result_dir+sname+'_'+figname+'.png')
    plt.close()
    return True

def doSaveFigures(fig_list,fig_type_list,feature,sname):
    for fig_id in range(len(fig_list)):
        fig,fig_type = fig_list[fig_id],fig_type_list[fig_id]
        saveResultFigure(sname,feature+'_'+fig_type,fig)
    return True

def makeTrace(comps):
    c_nr = comps['comps_nr']
    trace_df = pd.DataFrame(comps['trace'])
    trace = trace_df.to_numpy()
    p_nr = int(trace.shape[1]/c_nr)
    fig,axes = plt.subplots(c_nr,p_nr)
    if (c_nr)>1:
        for c_id in range(c_nr):
            c_ax = axes[c_id]
            if (p_nr>1):
                for p_id in range(p_nr):
                    cptrace = trace[:,p_id*c_nr+c_id]
                    c_ax[p_id].plot(cptrace)
            else: c_ax.plot(trace[c_id])
    else:
        c_ax = axes
        if (p_nr>1):
            for p_id in range(p_nr):
                cp_ax = c_ax[p_id]
                cptrace = trace[:,p_id*c_nr]
                cp_ax.plot(cptrace)
        else: c_ax.plot(trace[0])
    return fig

def fillMCMC(feature,proj_mcmc,comps_nr):
    mcmc = {'feature':feature,'model_str':'Beta','comps_nr':1,'samples_nr':2000,'tune':1000,'chains':2,'cores':2,'seed':20190415,'obs_mode':'full','obs_size':100000,'ppc_nr':2000}
    mcmc['model_str'] = proj_mcmc[feature]['model_str']
    mcmc['comps_nr'] = min(proj_mcmc[feature]['comps_nr'],comps_nr)
    mcmc['samples_nr'] = proj_mcmc[feature]['samples_nr']
    mcmc['tune'] = proj_mcmc[feature]['tune']
    mcmc['mcmc_round'],mcmc['rounds_nr'] = 0,1
    return mcmc


################################
########## EXECUTION ###########
################################

def doMCMCFigures(obs,margin,filter_text,sname):
    feature,var_type,traces,c_nr = margin['feature'],margin['var_type'],margin['components']['trace'],margin['components']['comps_nr']
    fig_hist = DS.makeHistogram(x_list=list(obs),feature=feature,ftype=var_type,filter_text=filter_text)
    fig_fitting = MF.plotMarginFitting(feature,obs,margin)
    fig_traces = MF.plotTraces(traces,c_nr)
    fig_list = [fig_hist,fig_fitting,fig_traces]
    fig_type_list = ['histogram','fitting','traces']
    doSaveFigures(fig_list,fig_type_list,feature,sname)
    return True

def doModel(proj_name,proj_params):

    print("*********\nCopula Modelling Initiating...\nGetting DATASUS")
    sname = proj_name
    session = {'sname':sname}
    req = proj_params['req']
    filter_text,slicing_text = proj_params['filter_text'],proj_params['slicing_text']
    proj_mcmc = proj_params['mcmc']
    req['dataset'],req['datatype'] = 'datasus','dbf'
    df = DI.loadDatasusFromFiles(req,data_dir)
    df,var_type_dic,val_mtx,feature_list = DI.selectData(df,filter_text,slicing_text)
    var_type_dic['MORTE'] = 'cat'
    session['df'] = df
    saveSession(session)

    print("Making DESCRIPTION")
    for feature in feature_list:
        var_type = var_type_dic[feature]
        fig_list,fig_type_list,conc_mtx = DS.doTotalDescription(df,feature,var_type,filter_text,sname,map_dir)
        doSaveFigures(fig_list,fig_type_list,feature,sname)
        plt.close('all')

    print("Estimating MARGINS")
    margins = {}
    for feature in feature_list:
        var_type = var_type_dic[feature]
        margin = margin_mask.copy()
        margin['feature'],margin['var_type'] = feature,var_type
        obs = np.array(df[feature])
        if var_type=='num':
            auto_comps_nr = MF.computeModes(obs)
            margin['mcmc'] = fillMCMC(feature,proj_mcmc,auto_comps_nr)
            margin = MF.estimateNumMargin(obs=obs,margin=margin)
            doMCMCFigures(obs,margin,filter_text,sname)
        else:
            margin = MF.estimateCatMargin(obs,margin)
        margins[feature] = margin
    session['margins'] = margins
    saveSession(session)

    print("Estimating COPULA")
    ms = session['margins']
    dtypes = [m['components']['mtype'] for f,m in ms.items()]
    params = [m['components']['params'] for f,m in ms.items()]
    copula = CF.modelCopula(mvsample=df.to_numpy(copy=True),dtypes=dtypes,params=params,features=feature_list)
    for d in range(len(ms)-1):
        x_2 = [copula.margins[i].vals[-1] for i in range(len(ms)) if i not in [d,d+1]]
        fig = copula.plot(x_2,d,d+1)
        saveResultFigure(sname,'copula'+str(d)+str(d+1),fig)
    #session['copula'] = copula
    #saveSession(session)
    print("Copula modelling DONE!\n*********")
    return [session,copula]

#[session,copula] = doModel('DATASUS_Test',proj_params)

year_list = ['2008','2009','2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018']
uf_list=['AC','AL','AM','AP','BA','CE','DF','ES','GO','MA','MG','MS','MT','PA','PB','PE','PI','PR','RJ','RN','RO','RR','RS','SC','SE','SP','TO']
#year_list,uf_list = ['2008'],['RJ']
def makeDatasus_Pkl(year_list=['2008'],uf_list=['AC','AP']):
    from datetime import datetime as dt
    source_data_dir = '/media/willian/SAMSUNG/DATASUS/'
    dbf_dir = source_data_dir + 'DBF/'
    pkl_dir = source_data_dir + 'PKL/'
    month_list = ['01','02','03','04','05','06','07','08','09','10','11','12']
    req = {'dataset':'DATASUS_BASE','datatype':'dbf','type_list':['RD'],'month_list':month_list}
    for year in year_list:
        print('*** ',year,' ***')
        for uf in uf_list:
            print(uf)
            ti = dt.now()
            fdir = dbf_dir+year+'/'
            req['year_list'],req['uf_list'] = [year],uf
            if (uf not in ['RJ','SP']):
                df=DI.loadDatasusFromFiles(req,fdir)
                with open(pkl_dir+'DATASUS_BASE_'+year+'_'+uf+'.pkl','wb') as f:
                    pk.dump(df,f)
            else: # RJ,SP in 2,3 or 4 files for avoiding memory overflow
                req['month_list'] = month_list[:3]
                df=DI.loadDatasusFromFiles(req,fdir)
                with open(pkl_dir+'DATASUS_BASE_'+year+'_'+uf+'_1T.pkl','wb') as f:
                    pk.dump(df,f)
                req['month_list'] = month_list[3:6]
                df=DI.loadDatasusFromFiles(req,fdir)
                with open(pkl_dir+'DATASUS_BASE_'+year+'_'+uf+'_2T.pkl','wb') as f:
                    pk.dump(df,f)
                req['month_list'] = month_list[6:9]
                df=DI.loadDatasusFromFiles(req,fdir)
                with open(pkl_dir+'DATASUS_BASE_'+year+'_'+uf+'_3T.pkl','wb') as f:
                    pk.dump(df,f)
                req['month_list'] = month_list[9:]
                df=DI.loadDatasusFromFiles(req,fdir)
                with open(pkl_dir+'DATASUS_BASE_'+year+'_'+uf+'_4T.pkl','wb') as f:
                    pk.dump(df,f)
            tf = dt.now()
            td = tf-ti
            print('%s - %s = %s sec' % (ti.strftime('%H:%M:%S'),tf.strftime('%H:%M:%S'),td.seconds))
    return True

#makeDatasus_Pkl(year_list=year_list,uf_list=uf_list)
makeDatasus_Pkl(year_list=['2016'],uf_list=['PR'])

def aggregateFile(year_list,uf_list):
    source_data_dir = '/media/willian/SAMSUNG/DATASUS/'
    pkl_dir = source_data_dir + 'PKL/'
    for y in year_list:
        for uf in uf_list:
            print(y,uf)
            df = pd.DataFrame()
            for t in range(1,5):
                fname_read = pkl_dir+'DATASUS_BASE_'+str(y)+'_'+str(uf)+'_'+str(t)+'T.pkl'
                with open(fname_read,'rb') as f:
                    dfx = pk.load(f)
                df = df.append(dfx)
            fname_write = pkl_dir+'DATASUS_BASE_'+str(y)+'_'+str(uf)+'.pkl'
            with open(fname_write,'wb') as f:
                pk.dump(df,f)
    return True

#aggregateFile(year_list[3:4],['SP'])