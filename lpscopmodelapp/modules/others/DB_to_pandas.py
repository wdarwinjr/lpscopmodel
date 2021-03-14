#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 22:15:22 2020

@author: willian
"""

import os
import pandas as pd
from dbfread import DBF
import pickle as pk

datasus_dir = '/media/willian/SAMSUNG/DATASUS/'
data_dir = datasus_dir + 'DBF/'
pkl_dir = datasus_dir + 'PKL/'
years = ['20'+str(i) for i in range(8,19)]
ufs = ['AC','AL','AM','AP','BA','CE','DF','ES','GO','MA',\
       'MG','MS','MT','PA','PB','PE','PI','PR','RJ','RN',\
       'RO','RR','RS','SC','SE','SP','TO']
years = ['2008']
ufs = ['AM','AP','BA']
rd_cols = ['UF_ZI','ANO_CMPT','MES_CMPT','ESPEC','MUNIC_RES',\
           'SEXO','UTI_MES_TO','UTI_INT_TO','QT_DIARIAS','VAL_SH',\
           'VAL_SP','VAL_TOT','VAL_UTI','US_TOT','DT_INTER',\
           'DT_SAIDA','DIAG_PRINC','DIAG_SECUN','GESTAO','IDADE',\
           'DIAS_PERM','MORTE','NACIONAL','CAR_INT','NUM_FILHOS',\
           'INSTRU','CBOR','CID_MORTE','RACA_COR','ETNIA']

def loadDataFromFiles(data_dir,pkl_dir,years,ufs):
    df = pd.DataFrame()
    for y in years:
        for uf in ufs:
            for r,ds,fs in os.walk(data_dir+y+'/'): # r=root, d=directories, f=files
                for fname in fs:
                    if (('.dbf' in fname) and ('RD' in fname) and(uf in fname)):
                        print(fname)
                        dbf = DBF(r+fname)
                        db_df = pd.DataFrame(iter(dbf))
                        sdb_df = db_df[rd_cols].copy()
                        sdb_df['time'] = '20'+fname[4:8]
                        sdb_df['space'] = fname[2:4]
                        df = df.append(sdb_df)
            df['id'] = range(len(df))
            df = df.set_index('id')
            with open(pkl_dir+y+uf+'.pkl','wb') as f:
                pk.dump(df,f)
    return True
