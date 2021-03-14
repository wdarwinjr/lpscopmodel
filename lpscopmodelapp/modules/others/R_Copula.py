#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 15:09:51 2020

@author: willian
"""

'''
There is a twist though. R object names can contain a “.” (dot) while in Python the dot means
“attribute in a namespace”. Because of this, importr is trying to translate “.” into “_”.
The details will not be necessary in most of the cases, but when they do
the documentation for R packages should be consulted.
'''

# import rpy2's package module
import rpy2.robjects.packages as rpackages

# import R's utility package
utils = rpackages.importr('utils')

# select a mirror for R packages
utils.chooseCRANmirror(ind=1) # select the first mirror in the list

# We are now ready to install packages using R’s own function install.package:

# R package names
## packnames = ('ggplot2', 'hexbin','copula')

# R vector of strings
## from rpy2.robjects.vectors import StrVector

# Selectively install what needs to be install.
# We are fancy, just because we can.

## names_to_install = [x for x in packnames if not rpackages.isinstalled(x)]
## if len(names_to_install) > 0:
##     utils.install_packages(StrVector(names_to_install))
utils.install_packages('copula',lib='/home/willian/anaconda3/lib/R/library')

###############################################################################

from rpy2.robjects.packages import importr
# import R's "base" package
#base = importr('base')

# import R's "utils" package
#utils = importr('utils')

# import R's "copula" package
copula = importr('copula',lib='/usr/local/lib/R/site-library')

# Getting R objects
# pi = robjects.r['pi']


###############################################################################
#from rpy2 import robjects

R_string = '# create a function `f`'+\
'f <- function(r, verbose=FALSE) {'+\
'if (verbose) {'+\
'cat("I am calling f().\n")'+\
'}'+\
'2 * pi * r'+\
'}'+\
'# call the function `f` with argument value 3'+\
'f(3)'
#robjects.r(R_string)

###############################################################################

# Let us first generate some copula samples based on which we then compute the empirical copulas.

## Generate copula data based on which to build empirical copula
R_string = 'n <- 1000 # sample size'+\
'd <- 2 # dimension'+\
'set.seed(271)'+\
'U <- rCopula(n, copula = gumbelCopula(iTau(gumbelCopula(), tau = 0.5), dim = d))'

# Next, consider a grid of evaluation points for the empirical copulas (and a density in one of the cases).

## Evaluation points
R_string = R_string+'\n'+'n.grid <- 26'+\
'sq <- seq(0, 1, length.out = n.grid)'+\
'u <- as.matrix(expand.grid("u[1]" = sq, "u[2]" = sq, KEEP.OUT.ATTRS = FALSE))'+\
'## ... for the density of the empirical beta copula'+\
'delta <- 0.01'+\
'sq. <- seq(delta, 1-delta, length.out = n.grid)'+\
'u. <- as.matrix(expand.grid("u[1]" = sq., "u[2]" = sq., KEEP.OUT.ATTRS = FALSE))'

# Now let us evaluate the empirical copula, the empirical beta copula, its density and the empirical checkerboard copula at u (for the density of the empirical beta copula, we use u.).

## Evaluate empirical copulas
R_string = R_string+'\n'+'emp.cop.none   <- empirical_copula(u,  U = U)'+\
'emp.cop.pbeta  <- empirical_copula(u,  U = U, smoothing = "pbeta")'+\
'emp.cop.dbeta  <- empirical_copula(u., U = U, smoothing = "dbeta")'+\
'lemp.cop.dbeta <- empirical_copula(u., U = U, smoothing = "dbeta", log = TRUE)'+\
'stopifnot(all.equal(lemp.cop.dbeta, log(emp.cop.dbeta))) # sanity check'+\
'emp.cop.chck   <- empirical_copula(u,  U = U, smoothing = "checkerboard")'


###############################################################################

R_string_empCop = 'empirical_copula <- function(u, U, smoothing = c("none", "pbeta", "dbeta", "checkerboard"),'+\
'                             offset = 0, log = FALSE, ...)'+\
'{'+\
'    stopifnot(0 <= u, u <= 1, 0 <= U, U <= 1)'+\
'    if(!is.matrix(u)) u <- rbind(u)'+\
'    if(!is.matrix(U)) U <- rbind(U)'+\
'    m <- nrow(u) # number of evaluation points'+\
'    n <- nrow(U) # number of points based on which the empirical copula is computed'+\
'    d <- ncol(U) # dimension'+\
'    stopifnot(ncol(u) == d)'+\
'    R <- apply(U, 2, rank, ...) # (n, d)-matrix of ranks'+\
'    switch(match.arg(smoothing),'+\
'    "none" = {'+\
'        R. <- t(R) / (n + 1) # (d, n)-matrix'+\
'        vapply(seq_len(m), function(k) # iterate over rows k of u'+\
'           sum(colSums(R. <= u[k,]) == d) / (n + offset), NA_real_)'+\
'    },'+\
'    "pbeta" = {'+\
'        ## Note: pbeta(q, shape1, shape2) is vectorized in the following sense:'+\
'        ##       1) pbeta(c(0.8, 0.6), shape1 = 1, shape2 = 1) => 2-vector (as expected)'+\
 '       ##       2) pbeta(0.8, shape1 = 1:4, shape2 = 1:4) => 4-vector (as expected)'+\
'        ##       3) pbeta(c(0.8, 0.6), shape1 = 1:2, shape2 = 1:2) => 2-vector (as expected)'+\
'        ##       4) pbeta(c(0.8, 0.6), shape1 = 1:4, shape2 = 1:4) => This is'+\
'        ##          equal to the recycled pbeta(c(0.8, 0.6, 0.8, 0.6), shape1 = 1:4, shape2 = 1:4)'+\
'        vapply(seq_len(m), function(k) { # iterate over rows k of u'+\
'                sum( # sum() over i'+\
'                    vapply(seq_len(n), function(i)'+\
'                        prod( pbeta(u[k,], shape1 = R[i,], shape2 = n + 1 - R[i,]) ), # prod() over j'+\
'                        NA_real_)) / (n + offset)'+\
'        }, NA_real_)'+\
'    },'+\
'    "dbeta" = {'+\
'        if(log) {'+\
'            vapply(seq_len(m), function(k) { # iterate over rows k of u'+\
'                lsum( # lsum() over i'+\
'                    vapply(seq_len(n), function(i) {'+\
'                        ## k and i are fixed now'+\
'                        lx.k.i <- sum( dbeta(u[k,], shape1 = R[i,], shape2 = n + 1 - R[i,], log = TRUE) ) # log(prod()) = sum(log()) over j for fixed k and i'+\
'                    },'+\
'                    NA_real_)) - log(n + offset)'+\
'            }, NA_real_)'+\
'        } else { # as for "pbeta", just with dbeta()'+\
'            vapply(seq_len(m), function(k) { # iterate over rows k of u'+\
'                sum( # sum() over i'+\
'                    vapply(seq_len(n), function(i)'+\
'                        prod( dbeta(u[k,], shape1 = R[i,], shape2 = n + 1 - R[i,]) ), # prod() over j'+\
'                        NA_real_)) / (n + offset)'+\
'            }, NA_real_)'+\
'        }'+\
'    },'+\
'    "checkerboard" = {'+\
'        R. <- t(R) # (d, n)-matrix'+\
'        vapply(seq_len(m), function(k) # iterate over rows k of u'+\
'            sum(apply(pmin(pmax(n * u[k,] - R. + 1, 0), 1), 2, prod)) / (n + offset),'+\
'            NA_real_) # pmin(...) = (d, n)-matrix'+\
'    },'+\
'    stop("Wrong smoothing"))'+\
'}'


R_string_empCop2 = 'empirical_copula <- function(u, U, smoothing = c("none", "pbeta", "dbeta", "checkerboard"), offset = 0, log = FALSE, ...)'+\
'{'+\
'    stopifnot(0 <= u, u <= 1, 0 <= U, U <= 1)'+\
'    if(!is.matrix(u)) u <- rbind(u)'+\
'    if(!is.matrix(U)) U <- rbind(U)'+\
'    m <- nrow(u)'+\
'    n <- nrow(U)'+\
'    d <- ncol(U)'+\
'    stopifnot(ncol(u) == d)'+\
'    R <- apply(U, 2, rank, ...)'+\
'    switch(match.arg(smoothing),'+\
'    "none" = {'+\
'        R. <- t(R) / (n + 1) # (d, n)-matrix'+\
'        vapply(seq_len(m), function(k)'+\
'           sum(colSums(R. <= u[k,]) == d) / (n + offset), NA_real_)'+\
'    },'+\
'    "pbeta" = {'+\
'        vapply(seq_len(m), function(k) {'+\
'                sum('+\
'                    vapply(seq_len(n), function(i)'+\
'                        prod( pbeta(u[k,], shape1 = R[i,], shape2 = n + 1 - R[i,]) ),'+\
'                        NA_real_)) / (n + offset)'+\
'        }, NA_real_)'+\
'    },'+\
'    "dbeta" = {'+\
'        if(log) {'+\
'            vapply(seq_len(m), function(k) {'+\
'                lsum('+\
'                    vapply(seq_len(n), function(i) {'+\
'                        lx.k.i <- sum( dbeta(u[k,], shape1 = R[i,], shape2 = n + 1 - R[i,], log = TRUE) )'+\
'                    },'+\
'                    NA_real_)) - log(n + offset)'+\
'            }, NA_real_)'+\
'        } else {'+\
'            vapply(seq_len(m), function(k) {'+\
'                sum('+\
'                    vapply(seq_len(n), function(i)'+\
'                        prod( dbeta(u[k,], shape1 = R[i,], shape2 = n + 1 - R[i,]) ),'+\
'                        NA_real_)) / (n + offset)'+\
'            }, NA_real_)'+\
'        }'+\
'    },'+\
'    "checkerboard" = {'+\
'        R. <- t(R)'+\
'        vapply(seq_len(m), function(k)'+\
'            sum(apply(pmin(pmax(n * u[k,] - R. + 1, 0), 1), 2, prod)) / (n + offset),'+\
'            NA_real_) # pmin(...) = (d, n)-matrix'+\
'    },'+\
'    stop("Wrong smoothing"))'+\
'}'


R_string_empCop3 = 'empirical_copula <- function(u, U, offset = 0, log = FALSE, ...) {'+\
'    stopifnot(0 <= u, u <= 1, 0 <= U, U <= 1)'+\
'    if(!is.matrix(u)) u <- rbind(u)'+\
'    if(!is.matrix(U)) U <- rbind(U)'+\
'    m <- nrow(u)'+\
'    n <- nrow(U)'+\
'    d <- ncol(U)'+\
'    stopifnot(ncol(u) == d)'+\
'    R <- apply(U, 2, rank, ...)'+\
'    R. <- t(R) / (n + 1)'+\
'    vapply(seq_len(m), function(k)'+\
'    sum(colSums(R. <= u[k,]) == d) / (n + offset), NA_real_)}'


'''
### TESTE GRAFICOS DE CÓPULAS ###


#import os
import numpy as np
import pickle as pk
from matplotlib import pyplot as plt
from matplotlib import cm
from collections import Counter


def plotGraphics(copula, d1, d2, x_2=None, bins=100, title=''):
    if (x_2==None):
        f_2 = [1. for i in range(copula.D-2)]
    else:
        f_2 = [copula.margins[i].cdf(x_2[i]) for i in range(copula.D)  if i not in [d1,d2]]
    rg = [round(i*(1./(bins)),4) for i in range(bins+1)]
    XX, YY = np.meshgrid(rg, rg)
    C = []
    for i in range(bins+1):
        c = []
        for j in range(bins+1):
            f,idx = [],0
            for d in range(copula.D):
                if (d==d1): f.append(XX[i][j])
                elif (d==d2): f.append(YY[i][j])
                else:
                    f.append(f_2[idx])
                    idx=idx+1
            c.append(copula.compute(f))
        C.append(c)
    CC = np.array(C)
    with open('debug_'+str(d1)+'_'+str(d2)+'.pkl','wb') as f:
        pk.dump([XX,YY,CC],f)
    p_colors,p_lim = ['black','blue','red','grey','green','orange'],6
    p_dict = dict(Counter(CC.flatten()).items())
    p_keys = list(p_dict.keys())
    p_keys_nr = len(p_keys)
    p_nr = min(p_keys_nr,p_lim)
    p_idxs = [int(p_keys_nr/p_nr)*i for i in range(p_nr)]
    p_list = [p_keys[p_idx] for p_idx in p_idxs]
    pline_list = []
    for p_id in range(len(p_list)):
        p,p_color = p_list[p_id],p_colors[p_id]
        x_list,y_list = [],[]
        for i in range(bins+1):
            for j in range(bins+1):
                if abs(CC[i][j]-p)<0.01:
                    x_list.append(XX[i][j]),y_list.append(YY[i][j])
        pline_list.append({'x':x_list,'y':y_list,'color':p_color})
    from mpl_toolkits.mplot3d import Axes3D
    surface_fig = plt.figure()
    ax = surface_fig.add_subplot(111, projection='3d')
    plt.title(title+' - Surface')
    ax.plot_surface(XX, YY, CC, cmap=cm.coolwarm, linewidth=0, antialiased=False)
    ax.plot_wireframe(XX, YY, CC, rstride=10, cstride=10)
    plt.savefig('copula_surface_'+str(d1)+'_'+str(d2)+'.png')
    levels_fig = plt.figure()
    ax = levels_fig.add_subplot(111)
    plt.title(title+' - Levels')
    for i in range(p_nr): ax.plot(pline_list[i]['x'],pline_list[i]['y'],'.',color=pline_list[i]['color'])
    plt.savefig('copula_levels_'+str(d1)+'_'+str(d2)+'.png')
    return surface_fig,levels_fig,XX,YY,CC


proj_dir = '/media/willian/Seagate Expansion Drive/GoogleDrive/USP_SCarlos/Doutorado/Tese/Experimentos/Codigo/WebInterface/uspdarwin/'
proj_static_dir = proj_dir+'/uspdarwinapp/static/'
proj_data_dir = proj_static_dir+'data/'
img_dir = proj_static_dir+'images/'
map_dir = proj_static_dir+'maps/'
result_dir = proj_static_dir+'results/'
pkl_dir = proj_static_dir+'pkl/'
datasus_dbf_dir = proj_data_dir+'datasus/dbf/'
datasus_pkl_dir = proj_data_dir+'datasus/pkl/'
packs_dir = proj_dir+'/uspdarwinapp/python_packs/'
task_output_fpath = result_dir+'task_output.pkl'
dataset_dir_dic = {'DATASUS':'datasus/','ForestFire':'forestfire/','OTHER':'other/'}

proj_name = 'Proj01'
pkl_file = pkl_dir+proj_name+'_session.pkl'
with open(pkl_file,'rb') as f:
    session = pk.load(f)

with open(session['df_pklfname'],'rb') as f:
    df = pk.load(f)
feature_list = session['feature_list']
margins_tab = session['margins_tab']
copula_tab = session['copula_tab']
ps = copula_tab[:,-1]
dtypes = [m['components']['mtype'] for f,m in session['margins'].items()]
params = [m['components']['params'] for f,m in session['margins'].items()]
copula = modelCopula(mvsample=df.to_numpy(copy=True),dtypes=dtypes,params=params,features=feature_list)

d1,d2,bins = 0,1,10
'''


