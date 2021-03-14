#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 10:11:53 2018

@author: willian
"""
import os
from dbfread import DBF
import pickle as pk
import pandas as pd
import re
import numpy as np

years = ['2008','2009','2010','2011','2012','2013','2014','2015','2016','2017','2018','2019']
noSP_ufs = ['AC','AL','AM','AP','BA','CE','DF','ES','GO','MA',\
       'MG','MS','MT','PA','PB','PE','PI','PR','RJ','RN',\
       'RO','RR','RS','SC','SE','TO']
ufs = noSP_ufs + ['SP']
reduced_cols = ['MES_CMPT','ESPEC','MUNIC_RES',\
                'SEXO','US_TOT','DIAG_PRINC','IDADE','DIAS_PERM',\
                'MORTE','CAR_INT','INSTRU','RACA_COR']
reduced_cols1 = ['UF_ZI','ANO_CMPT','MES_CMPT','ESPEC','CEP','MUNIC_RES','NASC',\
                'SEXO','DIAR_ACOM','QT_DIARIAS','VAL_SH','VAL_SP','VAL_TOT',\
                'VAL_UTI','US_TOT','DT_INTER','DT_SAIDA','DIAG_PRINC',\
                'DIAG_SECUN','NATUREZA','GESTAO','COD_IDADE','IDADE','DIAS_PERM',\
                'MORTE','CAR_INT','NUM_FILHOS','INSTRU','CID_NOTIF','GESTRISCO',\
                'INFEHOSP','CID_ASSO','CID_MORTE','COMPLEX','FINANC','RACA_COR','ETNIA']
#extdrive = '/media/willian/Seagate Expansion Drive/'
#pk_dir = extdrive+'DATASUS/PKL/last_version/'
#proj_dir = extdrive+'GoogleDrive/USP_SCarlos/Doutorado/Tese/Experimentos/Codigo/WebInterface/'
#pkr_dir = proj_dir+'uspdarwin/uspdarwinapp/static/data/datasus/other_pkl/reduced/'

class DW_Copula_DatasusImport:
    def __init__(self,data_dir):
        fname_mask_dbf = 'TPUFYYMM'
        fname_mask_pkl = self.getFnameMask(data_dir)
        self.mask_pkl = {'tp':fname_mask_pkl.find('TP'),'uf':fname_mask_pkl.find('UF'),'year':fname_mask_pkl.find('YYYY'),'month':fname_mask_pkl.find('MM')}
        self.mask_dbf = {'tp':fname_mask_dbf.find('TP'),'uf':fname_mask_dbf.find('UF'),'year':fname_mask_dbf.find('YY'),'month':fname_mask_dbf.find('MM')}
        self.data_dir = data_dir
        self.file_list,self.dataset_list,self.datatype_list,self.type_list,self.uf_list,self.year_list,self.month_list = self.getDatasusFilesProfile(self.data_dir)
        return None
    def getDatasusFilesProfile(self, data_dir):
        dataset_list,datatype_list = ['datasus'],['dbf','pkl','parquet']
        file_list,type_list,uf_list,years,month_list = [],[],[],[],[]
        for root,dirs,files in os.walk(data_dir):
            for fname in files:
                if '.dbf' in fname:
                    tp = fname[self.mask_dbf['tp']:self.mask_dbf['tp']+2]
                    uf = fname[self.mask_dbf['uf']:self.mask_dbf['uf']+2]
                    year = fname[self.mask_dbf['year']:self.mask_dbf['year']+2]
                    month = fname[self.mask_dbf['month']:self.mask_dbf['month']+2]
                    file_list.append([root,fname])
                    type_list.append(tp)
                    uf_list.append(uf)
                    years.append(year)
                    month_list.append(month)
                elif ('.pkl' in fname) or ('.parquet' in fname):
                    year = fname[self.mask_pkl['year']+2:self.mask_pkl['year']+4]
                    uf = fname[self.mask_pkl['uf']:self.mask_pkl['uf']+2]
                    file_list.append([root,fname])
                    type_list.append('RD')
                    uf_list.append(uf)
                    years.append(year)
                    month_list.append('all')
        type_list,uf_list,years,month_list = list(set(type_list)),list(set(uf_list)),list(set(years)),list(set(month_list))
        year_list = ['20'+y for y in years]
        return file_list,dataset_list,datatype_list,type_list,uf_list,year_list,month_list
    def loadDatasusFromFiles(self,req=None,file_list=[]):
        datatype = req['datatype']
        print('DATATYPE = ',datatype)
        df = pd.DataFrame()
        if (datatype=='dbf'):
            for [fdir,fname] in file_list:
                uf = fname[self.mask_dbf['uf']:self.mask_dbf['uf']+2]
                year = '20'+fname[self.mask_dbf['year']:self.mask_dbf['year']+2]
                month = fname[self.mask_dbf['month']:self.mask_dbf['month']+2]
                if checkFileInSelection(fname,req):
                    print(year+' - '+uf)
                    dbf = DBF(fdir+fname)
                    db_df = pd.DataFrame(iter(dbf))
                    db_df['ANO'] = year # fixed
                    db_df['UF'] = uf # fixed
                    db_df['MES'] = month # fixed
                    df = df.append(db_df)
            df['id'] = range(len(df))
            df = df.set_index('id')
        elif (datatype=='pkl'):
            for [fdir,fname] in file_list:
                print(fname)
                if '.pkl' in fname:
                    year = fname[self.mask_pkl['year']:self.mask_pkl['year']+4]
                    uf = fname[self.mask_pkl['uf']:self.mask_pkl['uf']+2]
                    print(year,uf)
                    if (year in req['year_list']): #and (fname[4:6] in req['uf_list'])):
                        print(year+' - '+uf)
                        db_df = pd.read_pickle(fdir+fname)
                        db_df['ANO'] = year
                        db_df['UF'] = uf
                        df = df.append(db_df)
        elif (datatype=='parquet'):
            for [fdir,fname] in file_list:
                if '.parquet' in fname:
                    year = fname[self.mask_pkl['year']+2:self.mask_pkl['year']+4]
                    uf = fname[self.mask_pkl['uf']:self.mask_pkl['uf']+2]
                    if (year in req['year_list']): #and (fname[4:6] in req['uf_list'])):
                        print(year+' - '+uf)
                        db_df = pd.read_parquet(fdir+fname)
                        db_df['ANO'] = year
                        db_df['UF'] = uf
                        df = df.append(db_df)
        return df
    def getFnameMask(self,mask_dir):
        fname = os.listdir(mask_dir)[0]
        uf_str = re.findall('_[A-Z]{2}[_|\.]',fname)[0][1:-1]
        yr_str = re.findall('(_\d{2}[_|\.])|((_\d{4}[_|\.]))',fname)[0][2][1:-1]
        yr_ref = 'YYYY'
        mask_uf = fname.replace(uf_str,'UF')
        mask = mask_uf.replace(yr_str,yr_ref[:len(yr_str)])
        return mask

def checkFileInSelection(fname,req):
    t,y,u,m = False,False,False,False
    if (fname[0:2] in req['type_list']): t=True
    if (fname[2:4] in req['uf_list']): u=True
    if ('20'+fname[4:6] in req['year_list']): y=True
    if (fname[6:8] in req['month_list']): m=True
    if (t and u and y and m): check=True
    else: check=False
    return check

def selectData(df,filter_text,slicing_text,time_col,space_col):
    filter_list = re.split(r';',filter_text)[:-1]
    raw_slicing_list = re.split(r';',slicing_text)[:-1]
    slicing_list = raw_slicing_list
    for f in filter_list:
        col,vals_str = re.split(r'=',f)
        vals = re.split(r',',vals_str)
        df = df.loc[df[col].isin(vals)].copy()
    out_df = df[slicing_list].copy()
    feature_list = list(out_df.columns)
    var_type_dic = {}
    for f in feature_list:
        if (out_df[f].dtype=='O' or len(out_df[f].unique())<10): var_type_dic[f] = 'cat'
        else: var_type_dic[f] = 'num'
    val_mtx_np = out_df.to_numpy()
    val_mtx = val_mtx_np.tolist()
    return out_df,var_type_dic,val_mtx,feature_list

def makeReducedZipData(years,ufs,reduced_cols,pk_dir,pkr_dir,pk_base_fname='DATASUS_BASE_YYYY_UF.pkl'):
    for year in years:
        makeReducedYearZipData(year,ufs,reduced_cols,pk_dir,pkr_dir,pk_base_fname)
    return True

def makeReducedYearZipData(year,ufs,reduced_cols,pk_dir,pkr_dir,pk_base_fname):
    pk_fname = pk_base_fname[:13]+year+pk_base_fname[17:]
    for uf in ufs:
        fname = pk_fname[:18]+uf+pk_fname[20:]
        with open(pk_dir+fname,'rb') as f_in:
            df = pk.load(f_in)
        dfc = df[reduced_cols].copy()
        frname = pk_fname[:8]+'REDUCED'+pk_fname[12:18]+uf+pk_fname[20:]
        with open(pkr_dir+frname,'wb') as f_out:
            pk.dump(dfc,f_out)
    return True

def appendFractionedZipData(uf,years,fracs,pkr_dir):
    for year in years:
        frname_out = 'DATASUS_REDUCED_'+year+'_'+uf+'.pkl'
        df = pd.DataFrame()
        for frac in fracs:
            frname_in = frname_out[:23]+frac+frname_out[23:]
            with open(pkr_dir+frname_in,'rb') as f_in:
                dff = pk.load(f_in)
            df = df.append(dff)
        with open(pkr_dir+frname_out,'wb') as f_out:
            pk.dump(df,f_out)
    return True

def sampleZipData(years,ufs,pk_dir,pks_dir,sample_ratio=.01):
    for year in years:
        for uf in ufs:
            frname = 'DATASUS_REDUCED_'+year+'_'+uf+'.pkl'
            with open(pk_dir+frname,'rb') as f_in:
                df = pk.load(f_in)
            sample_nr = int(len(df)*sample_ratio)
            sample_idxs = list(np.random.randint(0,high=len(df),size=sample_nr))
            sdf = df.iloc[sample_idxs].copy()
            df = None # free memory
            fsname = 'DATASUS_SAMPLED_'+year+'_'+uf+'.pkl'
            with open(pks_dir+fsname,'wb') as f:
                pk.dump(sdf,f)
    return sdf

'''
### ZIP FILES for unique http interaction ###
files = [{'fname':'fig_boxplot.png','body':img_data_uri}]
outfile = io.BytesIO()
with zipfile.ZipFile(outfile, 'w') as zf:
    for f in files:
        zf.writestr(f['fname'], f['body'])
zipped_file = outfile.getvalue()
data_uri = base64.b64encode(zipped_file).decode('ascii')
'''
