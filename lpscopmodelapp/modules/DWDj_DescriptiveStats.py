#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 10:11:53 2018

@author: willian
"""
import numpy as np
import collections
import geopandas as gpd
import scipy.stats as stc
import matplotlib as mpl
from matplotlib import pyplot as plt
mpl.use('Agg')
map_dir = 'maps/'

def makeBoxplot(x_list=[],feature='',ftype='cat',filter_text=''):
    fig, ax = plt.subplots()
    ax.clear()
    if (ftype=='num'):
        x_str = list(x_list)
        x = [float(s) for s in x_str]
        ax.boxplot(x)
    else:
        #ax.plot(range(10))
        #ax.plot(range(9,-1,-1))
        ax.plot([0,0,0,0,0,0,0,0,10],'.')
        ax.text(2,5,'NO BOXPLOT: Categorical feature!')
    ax.set_title("BOXPLOT - "+feature)
    ax.set_xlabel(feature+" - "+filter_text)
    ax.set_ylabel('Frequency')
    return fig

def makeHistogram(x_list=[],feature='',ftype='cat',filter_text=''):
    fig,ax = plt.subplots()
    ax.clear()
    if (ftype=='cat'):
        x = dict(collections.Counter(x_list))
        names = list(x.keys())
        values = np.array(list(x.values()))/float(len(x_list))
        ax.bar(names, values)
    else:
        x_str = x_list
        x = [float(s) for s in x_str]
        ax.hist(x,bins=50,density=True)
    ax.set_title("HISTOGRAM - "+feature)
    ax.set_xlabel(feature+" - "+filter_text)
    ax.set_ylabel('Frequency')
    return fig

def makeTimeSerie(time_dict={},feature='',ftype='cat',filter_text=''):
    fig, ax = plt.subplots()
    ax.clear()
    if (ftype!='cat'):
        ax.boxplot(time_dict.values())
        ax.set_xticklabels(time_dict.keys())
    else:
        names = list(time_dict.keys())
        values = np.array([len(time_dict[names[i]]) for i in range(len(names))])
        ax.bar(names, values)
        '''
        ax.plot(range(10))
        ax.plot(range(9,-1,-1))
        ax.text(2,5,'NO BOXPLOT: Categorical feature!')
        '''
    ax.set_title("TIME SERIE - "+feature)
    ax.set_xlabel(feature+" - "+filter_text)
    return fig

def makeSpaceMap(df=None,feature='',ftype='cat',filter_text='',space_col='',map_dir=''):
    geo_df = gpd.read_file(map_dir+'lim_unidade_federacao_a.shp')
    geo_df['val'] = 0.
    for idx in geo_df.index:
        uf = geo_df.at[idx,'sigla']
        subset_df = df[df[space_col]==uf]
        if (len(subset_df)>0):
            vals = subset_df[feature]
            if (ftype!='cat'):
                val = vals.mean()
            else:
                val = vals.count()
        else: val = 0.
        geo_df.at[idx,'val'] = val
    fig,ax =plt.subplots()#figsize =(10,10))
    geo_df.plot(ax=ax, column='val', legend=True, legend_kwds={'shrink':0.9}, cmap='viridis', edgecolor='grey')
    ax.set_title("SPACE MAP - "+feature)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    #ax.legend(title='Estados',loc='upper left',bbox_to_anchor=(1.0, 1.0),ncol=1)
    return fig

def makeConcordances(df=None):
    D = len(df.columns)
    for col in df.columns:
        if (df[col].dtype.name not in ['float64','int64']):
            df[col] = df[col].astype('category').cat.codes
    tau_c, tau_p = [], []
    for d1 in range(D):
        col1 = df.columns[d1]
        t_c, t_p = [], []
        for d2 in range(D):
            col2 = df.columns[d2]
            c, p = stc.kendalltau(np.array(df[col1]),np.array(df[col2]), nan_policy='omit')
            t_c.append(np.round(c,4)), t_p.append(np.round(p,4))
        tau_c.append(t_c), tau_p.append(t_p)
    tau_c, tau_p = np.array(tau_c), np.array(tau_p)
    rho_c, rho_p = stc.spearmanr(np.array(df))
    if (D==2):
        rho_c = np.array([[1.,rho_c],[rho_c,1.]])
        rho_p = np.array([[1.,rho_p],[rho_p,1.]])
    rho_c = np.array([[np.round(rho_c[i][j],4) for j in range(len(rho_c[i]))] for i in range(len(rho_c))])
    rho_p = np.array([[np.round(rho_p[i][j],4) for j in range(len(rho_p[i]))] for i in range(len(rho_p))])
    rho_tau_dic = {'rho_c':rho_c,'rho_p':rho_p,'tau_c':tau_c,'tau_p':tau_p}
    conc_mtx = []
    for i in range(D):
        row = []
        for j in range(D):
            if (i>j):
                val = rho_tau_dic['rho_c'][i][j]
            else:
                val = rho_tau_dic['tau_c'][i][j]
            row.append(val)
        conc_mtx.append(row)
    return conc_mtx

def doTotalDescription(in_df,feature,var_type,filter_text,sname,map_dir,time_col,space_col):
    df = in_df.copy()
    x_list=list(df[feature])
    fig_hist = makeHistogram(x_list=x_list,feature=feature,ftype=var_type,filter_text=filter_text)
    fig_boxplot = makeBoxplot(x_list=x_list,feature=feature,ftype=var_type,filter_text=filter_text)
    if (time_col!='no_time'):
        time,time_dict = sorted(list(set(df[time_col]))),{}
        for t in time: time_dict[t]=list(df[df[time_col]==t][feature])
        fig_timeserie = makeTimeSerie(time_dict=time_dict,feature=feature,ftype=var_type,filter_text=filter_text)
    else:
        fig_timeserie, ax = plt.subplots()
    if (space_col!='no_space'):
        fig_spacemap = makeSpaceMap(df=df,feature=feature,ftype=var_type,filter_text=filter_text,space_col=space_col,map_dir=map_dir)
    else:
        fig_spacemap, ax = plt.subplots()
    fig_list = [fig_hist,fig_boxplot,fig_timeserie,fig_spacemap]
    fig_type_list = ['histogram','boxplot','timeseries','spacemap']
    conc_mtx = makeConcordances(df=df)
    return fig_list,fig_type_list,conc_mtx
