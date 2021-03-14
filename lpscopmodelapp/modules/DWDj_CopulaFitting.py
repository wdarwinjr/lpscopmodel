#!/usr/bin/env python
# coding: utf8

import numpy as np
import scipy.stats as stt
from scipy.interpolate import UnivariateSpline
import matplotlib.pyplot as plt
from matplotlib import cm
#import pickle as pk
from collections import Counter

#from rpy2.robjects.packages import importr
#from rpy2.rinterface_lib import openrlib
#with openrlib.rlock:
    # (put interactions with R that should not be interrupted by
    # thread switching here).
    ##pass

class Margin:
    def __init__(self, sample=None, dtype='Beta', params=None, feature='feature'):
        self.error_exp = 6
        self.error = 10**(-self.error_exp)
        self.numeric_model_dic = {'Beta':stt.beta, 'Weibull':stt.weibull_min, 'Uniform':stt.uniform,'Normal':stt.norm}
        self.feature = feature
        self.sample, self.dtype, self.N = sample, dtype, len(sample)
        if (self.dtype in self.numeric_model_dic): self.mtype = 'numeric'
        else: self.mtype = 'categorical'
        self.vals = self._get_unique_vals()
        self.params,self.comps_nr = params,len(params)
        self.s_norm,self.loc,self.scale = None,None,None
        self._cdf, self._pdf = None, None
        if (self.mtype=='numeric'):
            ### params = [[alpha,beta,weight] for each component dist]
            self.s_norm,self.loc,self.scale = self._num_normalize_sample()
            #self._cdf_tab = np.array(np.sort(self.sample))
            #self._proj_tab = np.array([float(self._cdf_tab[i]-self.loc)/self.scale for i in range(self.N)])
            self.dist = self.numeric_model_dic[dtype]
            self.w = [self.params[i][-1] for i in range(self.comps_nr)]
            self.dists = [self.dist(self.params[i][0],self.params[i][1]) for i in range(self.comps_nr)]
            supports = np.array([list(self.dists[i].support()) for i in range(self.comps_nr)])
            self.support = [min(supports[:,0]),max(supports[:,1])]
            self._cdf = self._num_cdf
        else:
            ### params = [[p1,...,pn,weight=1.0] for an unique component dist]
            self.s_norm = self._cat_normalize_sample()
            #self._cdf_tab = np.array(np.sort(self.sample))
            #self._proj_tab = np.array([float(i)/self.N for i in range(len(self._cdf_tab))])
            self.dist = stt.multinomial
            self.w = [1.]
            self.dists = [self.dist(1,params[0][:-1])]
            self.support = [-1,len(self.params[0])]
            self._cdf = self._cat_cdf
        return None
    def normalize(self,x):
        if (self.mtype=='numeric'):
            if (x<self.vals[0]): x_norm = 0.0
            elif (x>self.vals[-1]): x_norm = 1.0
            else: x_norm = (x+self.loc)/self.scale
        else:
            if (x in self.vals): x_norm = self.vals.index(x)
            else: x_norm = -1
        return x_norm
    def denormalize(self,x_norm):
        if (self.mtype=='numeric'): x = (x_norm*self.scale) + self.loc
        else: x = self.vals[x_norm]
        return x
    def cdf(self, x):
        return self._cdf(x)
    def ppf(self, q): # binary search for all kind of distributions
        xa, xb = min(self.vals),max(self.vals)
        xa_norm,xb_norm = self.normalize(xa),self.normalize(xb)
        while((xb_norm-xa_norm)>self.error):
            x_norm = (xb_norm+xa_norm)/2
            x = self.denormalize(x_norm)
            qx = self.cdf(x)
            if(qx<=q):
                xa = x
            else:
                xb = x
        #if (self.mtype=='numeric'): x=np.round(x, decimals=self.error_exp)
        #else: x=int(x)
        return x
    def rvs(self, n):
        q = np.random.random(n)
        s = np.array([self.ppf(q[i]) for i in range(n)])
        return s
    def plot_sample(self):
        x = list(self.sample)
        fig,ax = plt.subplots()
        plt.title(self.feature)
        ax.plot(x, '.', ms=1.5)
        return fig
    def plot_cdf(self):
        x = list(self.vals)
        if (self.mtype=='numeric'): x_inf,x_sup = x[0]-(x[1]-x[0]),x[-1]+(x[-1]-x[-2])
        else: x_inf,x_sup = '',''
        x_extend = [x_inf] + x + [x_sup]
        fig,ax = plt.subplots()
        F = [self.cdf(x[i]) for i in range(len(x))]
        plt.title(self.feature)
        ax.step(x_extend, [0.]+F+[1.], where='post')
        return fig
    def _get_unique_vals(self):
        vals = sorted(list(set(self.sample)))
        return vals
    def _num_cdf(self, x):
        x_norm = self.normalize(x)
        p = 0.
        for c_id in range(len(self.dists)): p = p + self.w[c_id]*self.dists[c_id].cdf(x_norm)
        if (p>1.): p=1.
        return p
    def _cat_cdf(self, x):
        ### converts categories into ints 0 to k with cdf(xk)=k
        x_norm = self.normalize(x)
        p_nr = len(self.params[0])-1
        if (x_norm<0):
            p=0.
        elif (x_norm<p_nr):
            p=0.
            for j in range(int(x_norm)+1):
                a = np.zeros(p_nr)
                a[j] = 1
                p = p+self.dists[0].pmf(a)
        else:
            p=1.
        if (p>1.): p=1.
        return p
    def _num_normalize_sample(self):
        s = np.array(self.sample)
        scale = (s.max()-s.min())*(1+2*self.error)
        loc = -s.min()+(self.error*scale)
        s_norm = (s+loc)/scale
        return s_norm,loc,scale
    def _cat_normalize_sample(self):
        s = np.array(self.sample)
        s_norm = [self.vals.index(s[i]) for i in range(len(s))]
        return s_norm

class Copula:
    def __init__(self, sample=None, margins=[], margins_tab=None, copula_tab=None, ctype='empirical'):
        self.sample_lim = 3000
        self.error_exp = 6
        self.error = 10**(-self.error_exp)
        self.sample,self.margins,self.ctype = sample,margins,ctype
        (self.sample_size, self.D) = sample.shape
        self.N = min(self.sample_size,self.sample_lim)
        self.margins_tab = margins_tab # marginal probability projection of sample vectors
        self.copula_tab = copula_tab # margins_tab plus copula probability p for each sample ordered by p
        #self.ordered_copula_tab = None # copula_tab sequencialy ordered by dimension
        if (self.margins_tab is None): self.margins_tab = self._project_margins()
        self._search_mtx = self._make_search_mtx()
        if (self.copula_tab is None): self.copula_tab = self._make_copula_tab()
        if (ctype=='empirical'):
            #probs = self._calc_SampleProbs(margins_tab)
            #copula_tab = np.concatenate((margins_tab, probs), axis=1)
            #copula_tab = copula_tab[copula_tab[:,self.D-1].argsort()]
            #self.ordered_margins_tab = self._make_ordered(self.margins_tab)
            #self.ordered_copula_tab = self._make_ordered(copula_tab)
            compute = self._empirical_copula
        self._compute = compute
    def predict(self, x):
        return self.compute(self.project(x))
    def retrieve(self, p):
        return self.deproject(self.decompute(p))
    def compute(self, f):
        return self._compute(f)
    def decompute(self, p):
        p_vec = self.margins_tab #self.copula_tab[:,-1]
        ind = np.abs(p_vec-p).argmin()
        ind_min, ind_max = ind, ind
        while (p_vec[ind_min]>=p): ind_min = ind_min-1
        while (p_vec[ind_max]<=p): ind_max = ind_max+1
        f = self.margins_tab[ind_min:ind_max+1,:].mean(axis=0) #self.copula_tab[ind_min:ind_max+1,0:-1].mean(axis=0)
        return f
    def project(self, x):
        return [self.margins[j].cdf(x[j]) for j in range(self.D)]
    def deproject(self, f):
        return [self.margins[j].ppf(f[j]) for j in range(self.D)]
    def sample(self, n):
        p = np.random.random(n)
        s = self.retrieve(p)
        return s
    '''
    def plotLevels(self, d1, d2, title=''):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.title(title)
        p_colors = ['black','blue','red','grey','green','orange']
        p_nr = 5
        ps = [[i*(1./p_nr),p_colors[np.mod(i,len(p_colors))]] for i in range(p_nr+1)]
        for [p,p_color] in ps:
            idx_inf = 0
            for i in range(len(self.copula_tab)):
                if ((p-self.copula_tab[i][-1])<0.01):
                    idx_inf=i
                    break
            idx_sup = idx_inf
            for i in range(len(self.copula_tab)-1,-1,-1):
                if (self.copula_tab[i][-1]-p<0.01):
                    idx_sup=i
                    break
            print(idx_inf,' - ',idx_sup)
            x,y = self.copula_tab[idx_inf:idx_sup+1,d1],self.copula_tab[idx_inf:idx_sup+1,d2]
            ax.plot(x,y,'.',color=p_color)
        plt.savefig('copula_levels_'+str(d1)+'_'+str(d2)+'.png')
        return fig
    def plotSurface(self, d1, d2, x_2=None, bins=10, title=''):
        if (x_2==None): x_2 = [self.margins[i].vals[-1] for i in range(len(self.margins)) if i not in [d1,d2]]
        rg = [i*(1./(bins)) for i in range(bins+1)]
        XX, YY = np.meshgrid(rg, rg)
        C = []
        for i in range(bins+1):
            c = []
            for j in range(bins+1):
                f,idx = [],0
                for d in range(self.D):
                    if (d==d1): f.append(XX[i][j])
                    elif (d==d2): f.append(YY[i][j])
                    else:
                        f_2_d = self.margins[d].cdf(x_2[idx])
                        f.append(f_2_d)
                        idx=idx+1
                c.append(self.compute(f))
            C.append(c)
        CC = np.array(C)
        from mpl_toolkits.mplot3d import Axes3D
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        plt.title(title)
        ax.plot_surface(XX, YY, CC, cmap=cm.coolwarm, linewidth=0, antialiased=False)
        ax.plot_wireframe(XX, YY, CC, rstride=10, cstride=10)
        plt.savefig('copula_surface_'+str(d1)+'_'+str(d2)+'.png')
        return fig
    '''
    def plotGraphics(self, d1, d2, x_2=None, bins=20, title=''):
        levels = {1:'blue', 6:'green'}
        if (x_2==None):
            f_2 = [1. for i in range(self.D-2)]
        else:
            f_2 = [self.margins[i].cdf(x_2[i]) for i in range(self.D)  if i not in [d1,d2]]
        rg = [round(i*(1./(bins)),4) for i in range(bins+1)]
        XX, YY = np.meshgrid(rg, rg)
        C = []
        for i in range(bins+1):
            c = []
            for j in range(bins+1):
                f,idx = [],0
                for d in range(self.D):
                    if (d==d1): f.append(XX[i][j])
                    elif (d==d2): f.append(YY[i][j])
                    else:
                        f.append(f_2[idx])
                        idx=idx+1
                c.append(self.compute(f))
            C.append(c)
        CC = np.array(C)
        from mpl_toolkits.mplot3d import Axes3D
        surface_fig = plt.figure()
        ax = surface_fig.add_subplot(111, projection='3d')
        plt.title(title+' - Surface')
        ax.plot_surface(XX, YY, CC, cmap=cm.coolwarm, linewidth=0, antialiased=False)
        ax.plot_wireframe(XX, YY, CC, rstride=10, cstride=10)
        levels_fig, levels_ax = plt.subplots()
        levels_ax.set_title(title+' - Levels')
        levels_ax.set_xlim([0.0, 1.0])
        levels_ax.set_ylim([0.0, 1.0])
        WX, WY, MX, MY, PX, PY, XX, YY = self.makeLevels(self.copula_tab[:,[d1, d2, self.D]], levels)
        levels_list = list(levels.keys())
        for i in range(len(levels_list)):
            level = levels_list[i]
            levels_ax.plot(XX[i], YY[i], 'o', markersize=3, color=levels[level])
            levels_ax.plot(WX[i], WY[i], '.', markersize=2, color='grey')
            levels_ax.plot(MX[i], MY[i], '.', markersize=2, color='grey')
            levels_ax.plot(PX[i], PY[i], '.',markersize=2, color='grey')
        '''
        p_colors,p_lim = ['grey','blue','red','orange','yellow','green'],6
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
        for i in range(p_nr):
            ax.plot( pline_list[i]['x'], pline_list[i]['y'],\
                     '.',color=pline_list[i]['color'] )
        '''
        #plt.savefig('copula_surface_'+str(d1)+'_'+str(d2)+'.png')
        #plt.savefig('copula_levels_'+str(d1)+'_'+str(d2)+'.png')
        return surface_fig, levels_fig
    def calcCopulaLevelDelta(self, proj_tab, c):
        dots_min, delta_max = 50, 0.1
        go, delta = True, 0.01
        while go:
            dots_nr = 0
            for j in range(proj_tab.shape[0]):
                [x, y, p] = proj_tab[j]
                if abs(p-c)<=delta:
                    dots_nr += 1
            if dots_nr>=dots_min:
                c_delta = delta
                go = False
            else:
                delta += 0.01
                if  delta>=delta_max:
                    c_delta = delta_max
                    go = False
        return delta
    def makeLevels(self, proj_tab, levels):
        dots_nr = 50
        WX, WY, MX, MY, PX, PY, XX, YY = [], [], [], [], [], [], [], []
        for i in levels:
            grid = int(50/np.sqrt(i))
            c = float(i)/10
            c_delta = self.calcCopulaLevelDelta(proj_tab, c)
            c_w, c_m = c-c_delta, c+c_delta
            a, b = c*np.ones((1,grid)), np.linspace(c, 1.0, grid).reshape((1, grid))
            WX.append(np.concatenate((a, b)))
            WY.append(np.concatenate((b, a)))
            mx, my = np.linspace(1.0, c, 2*grid), np.linspace(c, 1.0, 2*grid)
            MX.append(mx)
            MY.append(my)
            PX.append(mx)
            PY.append(c/mx)
            xx, yy, pc = [], [], []
            for j in range(proj_tab.shape[0]):
                [x, y, p] = proj_tab[j]
                p_c = abs(p-c)
                if p_c<c_delta:
                    xx.append(x), yy.append(y), pc.append(p_c)
            xx, yy, pc = np.array(xx), np.array(yy), np.array(pc)
            pc_sort = pc.argsort()
            XX.append(list(xx[pc_sort[:dots_nr]]))
            YY.append(list(yy[pc_sort[:dots_nr]]))
        return WX, WY, MX, MY, PX, PY, XX, YY
    def _project_margins(self):
        idx_list = np.random.choice(self.sample_size,size=self.N,replace=False)
        sample = self.sample[idx_list,:]
        margins_tab = np.array([[self.margins[j].cdf(sample[i][j]) for j in range(self.D)] for i in range(len(sample))])
        return margins_tab
    def _make_search_mtx(self):
        aux = [tuple([f[j] for j in range(self.D)]) for f in self.margins_tab]
        search_mtx = np.array(aux, dtype=[(str(j),float) for j in range(self.D)])
        return search_mtx
    def _count_dbox(self, f):
        src_mtx = self._search_mtx
        for j in range(self.D):
            src_mtx_ord = np.sort(src_mtx, order=str(j))
            ind = np.searchsorted(src_mtx_ord[str(j)], f[j], side='right')
            src_mtx = src_mtx_ord[:ind]
        return ind
    def _make_copula_tab(self):
        aux_tab = []
        for f in self.margins_tab:
            p = self._count_dbox(f)/len(self.margins_tab)
            fl = list(f)
            fl = fl + [p]
            aux_tab.append(fl)
        aux_mtx = np.array(aux_tab)
        args = np.argsort(aux_mtx[:,-1])
        copula_tab = aux_mtx[args]
        return copula_tab
        '''
        counter = 0
        for i in range(len(f_sample)):
            if (self._in_dbox(f_sample[i], f)):
                counter = counter + 1
        return counter
        '''
    def _empirical_copula(self, f):
        p = float(self._count_dbox(f))/self.N #self.copula_tab[:,0:-1]
        if (p>1.): p=1.
        return p
    '''
    def plot_plane(self, d, dp, fp=1., bins=10, title=''):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.title(title)
        x = np.array([i*(1./(bins)) for i in range(bins+1)])
        fs = []
        for i in range(bins+1):
            f = []
            for di in range(self.D):
                if (di==d): f.append(x[i])
                elif (di==dp): f.append(fp)
                else: f.append(1.)
            fs.append(f)
        c = np.array([self.compute(fs[i]) for i in range(bins+1)])
        #print(fs[0:10],c)
        ax.plot(x, c)
        plt.savefig('COPULA_PLANE.png')
        return fig
    def _count_dbox_ordered(self, f, f_sample_ordered):
        ind = self.N-1
        for d in range(self.D):
            for i in range(ind,-1,-1):
                if (f[i,d]>=f_sample_ordered[i,d]):
                    ind = i
                    break
        return ind
    def _in_dbox(self, f, fbox):
        return not np.any(np.clip(fbox-f, None, 0))
    def _make_ordered(self, tab):50,
        new_tab = np.array([tab[i]+[i] for i in range(len(tab))])
        new_tab = new_tab[new_tab[:,0].argsort()]
        for d in range(self.D):
            state = 'searching'
            for i in range(self.N-1):
                if (state=='searching'):
                    if (new_tab[i,d]==new_tab[i+1,d]):
                        state='sorting'
                        sort_ind = i
                elif (state=='sorting'):
                    if (new_tab[i,d]!=new_tab[i+1,d]):
                        state='searching'
                        rng = range(sort_ind,i+1)
                        new_tab[rng] = new_tab[new_tab[rng].argsort()]
                else:
                    pass
        return new_tab
    def _calc_SampleProbs(self, margins_tab):
        vecs = [np.sort(np.array([tuple([i,margins_tab[i][j]]) for i in range(self.N)], dtype=[('ind',int),('val',float)]), order='val') for j in range(self.D)]
        probs = []
        for i in range(self.N):
            inds = [np.searchsorted(vecs[j]['val'], margins_tab[i][j], side='right') for j in range(self.D)]
            aux = set(vecs[0]['ind'][:inds[0]])
            for j in range(self.D):
                aux.intersection_update(set(vecs[j]['ind'][:inds[j]]))
            probs.append(float(len(aux))/self.N)
        probs = np.array(probs)
        probs = probs.reshape((len(probs),1))
        return probs
    '''

def modelCopula(mvsample=None,dtypes=None,params=None,features=None):
    ms = []
    for i in range(mvsample.shape[1]):
        ms.append(Margin(sample=mvsample[:,i],dtype=dtypes[i],params=params[i],feature=features[i]))
        print('Margin '+features[i])
    #ms = [Margin(sample=mvsample[:,i],dtype=dtypes[i],params=params[i],feature=features[i]) for i in range(mvsample.shape[1])]
    copula = Copula(sample=mvsample, margins=ms, ctype='empirical')
    return copula

''' for testing copula modeling with toy multinormal sample
def makeTestParams():
    sample = np.random.multivariate_normal([0.,0.],[[1.,.5],[.5,1.]],10000)
    D = sample.shape[1]
    inf,sup = min(sample.flatten()),max(sample.flatten())
    loc,sc = inf*1.01,(sup-inf)*1.02
    sample_norm = (sample-loc)/sc
    fits = [stt.beta.fit(sample_norm[:,i]) for i in range(D)]
    params = [[[fits[i][0],fits[i][1],1.]] for i in range(D)]
    return sample,params

sample,params = makeTestParams()

ms,cop = modelCopula(mvsample=sample,dtypes=['Beta','Beta'],params=params)
'''
def testMITCopulas():
    import warnings
    warnings.filterwarnings('ignore')
    
    from copulas.datasets import sample_trivariate_xyz
    from copulas.multivariate import GaussianMultivariate
    from copulas.visualization import compare_3d
    
    # Load a dataset with 3 columns that are not independent
    real_data = sample_trivariate_xyz()
    
    # Fit a gaussian copula to the data
    copula = GaussianMultivariate()
    copula.fit(real_data)
    
    # Sample synthetic data
    synthetic_data = copula.sample(len(real_data))
    
    # Plot the real and the synthetic data to compare
    compare_3d(real_data, synthetic_data)
    return True
