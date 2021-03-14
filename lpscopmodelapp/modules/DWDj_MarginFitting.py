#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 10:11:53 2018

@author: willian
"""
import numpy as np
import scipy.stats as stt
import scipy.signal as sgn
import matplotlib as mpl
import pymc3 as pm
import collections
import pandas as pd
#import pickle as pk
import copy
from matplotlib import pyplot as plt
mpl.use('Agg')

'''
import logging
logger = logging.getLogger('pymc3')
stderr = logger.handlers[0]
#stderr.setLevel(logging.CRITICAL)
fh = logging.FileHandler('pymc3.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(logging.Formatter(fmt='%(asctime)-15s %(message)s'))
logger.addHandler(fh)
'''

models = ['Beta', 'Weibull']
dfs = ['all', 'elderly']
model_dic = {'Beta':pm.Beta, 'Weibull':pm.Weibull, 'Uniform':pm.Uniform}
mcmc_params_std = {'model_str':'Beta','comps_nr':1,'samples_nr':2000,'tune':1000,'obs_size':'full'}
mcmc_init_std = {'alpha_range':[0.001,1000.],'beta_range':[0.001,1000.],'alpha_ini':[1.],'beta_ini':[1.]}
mcmc_proc_std = {'chains':2,'cores':2,'seed':20190415,'obs_mode':'full','obs_size':100000,'ppc_nr':2000}

def estimateCatMargin(obs,margin):
    margin = copy.deepcopy(margin)
    unique = np.unique(obs,return_counts=True) 
    probs = unique[1]/float(len(obs))
    labels = [str(x) for x in unique[0]]+['weight']
    params = [[p for p in probs] + [1.0]] # w=1.0 to be compatible to numeric features
    margin['components'] = {'mtype':'Multinomial','comps_nr':1,'params':params,'params_sd':[[0. for i in range(len(labels))]],'labels':labels,'trace':[p for p in params]}
    return margin

def estimateNumMargin(obs=np.array([]),margin={}):
    mcmc_params = margin['mcmc']
    mcmc_state = computeStateMCMC(mcmc_params=mcmc_params)
    mcmc_trace,mcmc_summary,mcmc_accept_probs = runMCMCMargin(obs=obs,mcmc_params=mcmc_params,mcmc_state=mcmc_state)
    mcmc_params['round_trace'] = aggregateTraces({},mcmc_trace)
    if (mcmc_params['mcmc_round']>0): trace_stored = mcmc_params['trace']
    else: trace_stored = {}
    mcmc_params['trace'] = aggregateTraces(trace_stored,mcmc_trace)
    mcmc_params['round_summary'],mcmc_params['round_accept_probs'] = mcmc_summary.to_dict(),mcmc_accept_probs
    margin['mcmc'] = mcmc_params
    margin['components'] = makeComponents(mcmc_params)
    return margin

def computeStateMCMC(mcmc_params=None):
    comps_nr = mcmc_params['comps_nr']
    if mcmc_params['mcmc_round']>0:
        lb,mn,sd = mcmc_params['labels'],mcmc_params['params'],mcmc_params['params_sd']
        alpha_ids,beta_ids,w_ids = [l_id for l_id in range(len(lb)) if 'alpha' in lb[l_id]],[l_id for l_id in range(len(lb)) if 'beta' in lb[l_id]],[l_id for l_id in range(len(lb)) if 'w' in lb[l_id]]
        alpha_mean,beta_mean,w_mean = [mn[i] for i in alpha_ids],[mn[i] for i in beta_ids],[mn[i] for i in w_ids]
        alpha_sd,beta_sd = [sd[i] for i in alpha_ids],[sd[i] for i in beta_ids]
        alpha_ini = [round(alpha_mean[i],2) for i in range(comps_nr)]
        beta_ini = [round(beta_mean[i],2) for i in range(comps_nr)]
        w_ini = [round(w_mean[i],2) for i in range(comps_nr)]
        alpha_range = [max([min(alpha_mean)-2*max(alpha_sd),0]),max(alpha_mean)+2*max(alpha_sd)]
        beta_range = [max([min(beta_mean)-2*max(beta_sd),0]),max(beta_mean)+2*max(beta_sd)]
        print("alpha_range=%s,beta_range=%s,alpha_ini=%s,beta_ini%s" % (alpha_range,beta_range,alpha_ini,beta_ini))
    else:
        mu,sigma = [round((i+.5)/comps_nr,2) for i in range(comps_nr)],[.2 for i in range(comps_nr)]
        alpha_range = mcmc_init_std['alpha_range']
        beta_range  = mcmc_init_std['beta_range']
        alpha_ini = [round(mu[i]**2*(((1.-mu[i])/sigma[i]**2)-(1./mu[i])),2) for i in range(comps_nr)]
        beta_ini = [round(alpha_ini[i]*((1./mu[i])-1.),2) for i in range(comps_nr)]
        w_ini = [round((1./comps_nr),2) for i in range(comps_nr)]
    mcmc_state = {'alpha_range':alpha_range,'beta_range':beta_range,'alpha_ini':alpha_ini,'beta_ini':beta_ini,'w_ini':w_ini}
    return mcmc_state

def runMCMCMargin(obs=np.array([]),mcmc_params=mcmc_params_std,mcmc_state=mcmc_init_std,mcmc_proc=mcmc_proc_std):
    #print('Running MCMC for '+mcmc_params['feature'])
    if (mcmc_params['obs_size']=='sample'):
        obs = np.array([obs[i] for i in np.random.randint(0,len(obs),size=mcmc_params['obs_size'])])
    chains,cores,seed = mcmc_proc['chains'],mcmc_proc['cores'],mcmc_proc['seed']
    comps_nr,samples,tunes,model_str = mcmc_params['comps_nr'],mcmc_params['samples_nr'],mcmc_params['tune'],mcmc_params['model_str']
    dist = model_dic[model_str]
    obs_norm,precision,scale = normObs(obs)
    if (comps_nr>1):
        alpha_range,beta_range,alpha_ini,beta_ini,w_ini = mcmc_state['alpha_range'],mcmc_state['beta_range'],mcmc_state['alpha_ini'],mcmc_state['beta_ini'],mcmc_state['w_ini']
        with pm.Model() as model:
            alpha = pm.Uniform('alpha', alpha_range[0], alpha_range[1], shape=(comps_nr,), testval=alpha_ini)
            beta = pm.Uniform('beta', beta_range[0], beta_range[1], shape=(comps_nr,), testval=beta_ini)
            comps = [dist.dist(alpha=alpha[i], beta=beta[i]) for i in range(comps_nr)]
            w = pm.Dirichlet('w', a=np.array([1 for i in range(comps_nr)]), testval=w_ini)
            pm.Mixture('dist', comp_dists=comps, w=w, observed=obs_norm)
    else:
        alpha_range,beta_range,alpha_ini,beta_ini = mcmc_state['alpha_range'],mcmc_state['beta_range'],mcmc_state['alpha_ini'],mcmc_state['beta_ini']
        print(alpha_range,alpha_ini)
        with pm.Model() as model:
            alpha = pm.Uniform('alpha', alpha_range[0], alpha_range[1], testval=alpha_ini[0])
            beta = pm.Uniform('beta', beta_range[0], beta_range[1], testval=beta_ini[0])
            dist('dist', alpha=alpha, beta=beta, observed=obs_norm)
    trace = pm.sample(samples, model=model, chains=chains, cores=cores, tune=tunes, random_seed=seed) #, progressbar=False) #max_treedepth=15,
    accept_tree = trace.get_sampler_stats('mean_tree_accept',combine=False)
    accept_probs = [np.mean(accept_tree[i]) for i in range(len(accept_tree))]
    #ppc = pm.sample_ppc(trace, samples=mcmc['ppc_nr'], model=model)
    summary = pm.summary(trace)
    return trace,summary,accept_probs

def aggregateTraces(trace_dic_stored,trace_new):
    #with open('trace.pkl','wb') as f:
    #    pk.dump(trace_dic_stored,f)
    #    pk.dump(trace_new,f)
    df = pd.DataFrame(trace_dic_stored)
    ydf = pd.DataFrame()
    for c_id in trace_new.chains:
        xdf = pm.backends.tracetab.trace_to_dataframe(trace_new,chains=c_id)
        xdf['chain'] = c_id
        xdf.reset_index(inplace=True)
        ydf = ydf.append(xdf.copy())
    ydf.reset_index(drop=True,inplace=True)
    df = df.append(ydf.copy())
    df_dic = df.to_dict()
    #with open('df_dic.pkl','wb') as f:
    #    pk.dump(df_dic,f)
    return df_dic

def makeComponents(mcmc):
    summary = mcmc['round_summary']
    labels_linear = list(summary['mean'].keys())
    c_nr,p_nr = mcmc['comps_nr'],int(len(labels_linear)/mcmc['comps_nr'])
    params = [[summary['mean'][labels_linear[p*c_nr+c]] for p in range(p_nr)] for c in range(c_nr)]
    params_sd = [[summary['sd'][labels_linear[p*c_nr+c]] for p in range(p_nr)] for c in range(c_nr)]
    if (mcmc['comps_nr']==1):
        labels_linear.append('w')
        params[0].append(1.)
        params_sd[0].append(0.)
    labels = [labels_linear[i] for i in range(len(labels_linear)) if i%c_nr==0]
    comps = {'mtype':mcmc['model_str'],'comps_nr':mcmc['comps_nr'],'params':params,'params_sd':params_sd,'labels':labels,'trace':mcmc['trace']}
    return comps

def computeModes(obs):
    u = np.unique(obs)
    bins_nr = min(len(u),int(np.sqrt(len(obs))))
    d = bins_nr/10
    hist,_ = np.histogram(obs,bins=bins_nr)
    peaks,_ = sgn.find_peaks(hist,distance=d)
    return len(peaks)

def getMargin(comps):
    # this implementation: only Beta, Weibull and Multinomial (cat)
    mtype = comps['mtype']
    params = comps['params']
    c_nr = comps['comps_nr']
    if mtype=='Beta':
        dists = []
        for c_id in range(c_nr):
            #labels = ['a','b']
            param = params[c_id][:2]
            dist = stt.beta(a=param[0],b=param[1])
            dists.append(dist)
    elif mtype=='Weibull':
        dists = []
        for c_id in range(comps['comps_nr']):
            #labels = ['c','scale']
            param = [params[(p_id*c_nr)+c_id] for p_id in range(2)]
            dist = stt.weibull_min(param[0],0.,param[1])
            dists.append(dist)
    elif mtype=='Multinomial':
            # IMPLEMENTAR
            dists = [stt.multinomial(1,params)]
    try:
        dists[0].interval(1.)
    except:
        domain = []
    else:
        domains = np.array([dists[d_id].interval(1.) for d_id in range(len(dists))])
        domain_raw = [domains[:,0].max(),domains[:,1].min()]
        delta = 0.001*(domain_raw[1]-domain_raw[0])
        domain = [domain_raw[0]+delta,domain_raw[1]-delta]
    return dists,domain

def transformQuantity(x,domain):
    x_np = np.array(x)
    x_norm = (x_np-x_np.min())/(x_np.max()-x_np.min())
    x_domain = x_norm*(domain[1]-domain[0])+domain[0]
    return x_domain

def makeXValues(obs_t):
    lim_inf,lim_sup = min(obs_t),max(obs_t)
    obs_range = lim_sup-lim_inf
    x_inf,x_sup = lim_inf-0.1*obs_range,lim_sup+0.1*obs_range
    x_nr = min(len(np.unique(obs_t)),50)
    x = np.linspace(x_inf, x_sup, x_nr)
    bin_size = float(x.max()-x.min())/(len(x)-1)
    bins = np.append(x-(bin_size/2.),x.max()+(bin_size/2.))
    return x,bins

def normObs(obs):
    # observations must be fitted in ( 0.01/N, 1-(0.01/N) ) interval
    inf,sup = obs.min(),obs.max()
    precision = 1./(100*len(obs))
    scale = (sup-inf)*(1.+2*precision)
    obs_norm = ((obs-inf)/scale) + precision
    return obs_norm,precision,scale

def computeGraphicQuantities(obs,comps):
    c_nr,params = comps['comps_nr'],comps['params']
    dists,domain = getMargin(comps)
    obs_t = transformQuantity(obs,domain)
    x,bins = makeXValues(obs_t)
    y = []
    for c_id in range(c_nr):
        [a,b,w] = params[c_id]
        y.append(w*dists[c_id].pdf(x))
    y = np.array(y)
    yt = np.array([sum(y[:,i]) for i in range(y.shape[1])])
    hist,_ = np.histogram(obs_t,bins=bins,density=True)
    aic = 1.
    return x,y,yt,hist,aic

def computeNumPlotParams(comps):
    c_nr = comps['comps_nr']
    params = comps['params']
    labels_linear = comps['labels']
    p_nr = int(len(labels_linear)/c_nr)
    labels = [labels_linear[l_id*c_nr][:-3] for l_id in range(p_nr)]
    params_mtx = params
    return params_mtx,labels

def plotTraces(trace,c_nr):
    trace_df = pd.DataFrame(trace)
    param_labels = list(trace_df.columns[1:-1])
    p_nr = int(len(param_labels)/c_nr)
    fig,axes = plt.subplots(c_nr,p_nr)
    #plt.subplots_adjust(wspace=0.1, hspace=0.1)
    for c_id in range(c_nr):
        for p_id in range(p_nr):
            idx = p_id*c_nr+c_id
            if (c_nr>1): ax = axes[c_id,p_id]
            else: ax = axes[p_id]
            param = param_labels[idx]
            y = list(trace_df[param])
            ax.set_title(param),ax.set_xlabel('sample nr'),ax.set_ylabel('param value')
            ax.set_ylim([0.,2*max(y)])
            ax.plot(y)
    plt.tight_layout()
    return fig

def plotNumMarginFitting(feature,obs,comps):
    x,y,yt,hist,aic = computeGraphicQuantities(obs,comps)
    params_mtx,labels = computeNumPlotParams(comps)
    dcolors = ['k','g','b']
    fig,ax = plt.subplots()
    #ax.set_title('Fitting of distributions - AIC=%s' % '{:,.2f}'.format(aic),fontdict={'fontsize':8,'fontweight':'medium'})
    ax.set_title('Fitting of distributions',fontdict={'fontsize':8,'fontweight':'medium'})
    ax.set_xlabel(feature+' (normalized)',fontdict={'fontsize':8,'fontweight':'medium'})
    ax.set_ylabel('frequency',fontdict={'fontsize':8,'fontweight':'medium'})
    ax.tick_params(axis='both',labelsize=8)
    for c_id in range(len(y)):
        ax.plot(x, y[c_id], dcolors[np.mod(c_id,len(dcolors))]+'-', lw=1, label='comp'+str(c_id))
    ax.plot(x, yt,'r-', lw=1, label='comp_sum')
    ax.plot(x, hist, alpha=0.5, label='hist')
    ax.legend()
    ax.set_xlim(left=ax.get_xlim()[0],right=1.2*ax.get_xlim()[1])
    ax.set_ylim(bottom=ax.get_ylim()[0],top=1.2*ax.get_ylim()[1])
    x_dim,y_dim = ax.get_xlim()[1],ax.get_ylim()[1]
    ax.text(-.02*x_dim,.95*y_dim,'comp#='+str(labels),fontsize=8)
    for i in range(len(y)):
        params_str = str([round(p,4) for p in params_mtx[i]])
        ax.text(-.02*x_dim,(.95-.05*(i+1))*y_dim,'comp'+str(i+1)+'='+params_str,fontsize=8)
    return fig

def plotCatMarginFitting(feature,obs,comps):
    fig,ax = plt.subplots()
    #fig.suptitle('Fitting of categorical distribution - %s' % feature)
    ax.set_title('Fitting of categorical distribution - %s' % feature)
    x = dict(collections.Counter(obs))
    names = list(x.keys())
    values = np.array(list(x.values()))/float(len(obs))
    ax.bar(names, values, color='b')
    ax.bar(comps['labels'][:-1], comps['params'][0][:-1], color='grey', width=0.1)
    return fig

def plotMarginFitting(feature,obs,margin):
    if margin['var_type']=='num': fig = plotNumMarginFitting(feature,obs,margin['components'])
    else: fig = plotCatMarginFitting(feature,obs,margin['components'])
    return fig
