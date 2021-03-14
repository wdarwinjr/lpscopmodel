#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 10:11:53 2018

@author: willian
"""
import sys
import pickle as pk
import DWDj_Copula_MarginFitting as MF

### MAIN - treat commandline parameters
if len(sys.argv)>1:
    func_name,pkl_dir = sys.argv[1],sys.argv[2]
    if (func_name=='estimateMargin'):
        with open(pkl_dir+func_name+'_in.pkl','rb') as f:
            in_vars = pk.load(f)
        obs,margin = in_vars['obs'],in_vars['margin']
        margin,traces = MF.estimateMargin(obs,margin)
        out_vars = {'margin':margin,'traces':traces}
        with open(pkl_dir+func_name+'_out.pkl','wb') as f:
            pk.dump(out_vars,f)
    elif (func_name=='b'):
        pass
    else:
        pass