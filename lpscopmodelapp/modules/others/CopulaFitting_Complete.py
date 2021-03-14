#!/usr/bin/env python
# coding: utf8

import numpy as np
import scipy.stats as stt
import matplotlib.pyplot as plt
#from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

class Margin:
    def __init__(self, sample=None, dtype='empirical', params=None):
        self.error_exp = 6
        self.error = 10**(-self.error_exp)
        self.poly_grade = 10
        self.Sample, self.Type, self.N = sample, dtype, len(sample)
        self._lim_inf, self._lim_sup, self._cdf, self._pdf = None, None, None, None
        self._cdf_tab, self._proj_tab, self._params = None, None, None
        if (dtype=='empirical'):
            self._lim_inf, self._lim_sup = -np.inf, np.inf
            self._cdf_tab = np.array(np.sort(sample))
            self._cdf = self._empirical_cdf
            self._proj_tab = np.array([float(i)/self.N for i in range(len(self._cdf_tab))])
        if (dtype=='smooth_empirical'):
            self._lim_inf, self._lim_sup = -np.inf, np.inf
            self._cdf_tab = np.array(np.sort(sample))
            self._H = self._smooth_poly(self.poly_grade)
            self._h = self._cdf_tab[-1] - self._cdf_tab[0]
            self._tail_param = self._smooth_tail(self.N, self._cdf_tab, self._H, self._h)
            self._cdf = self._smooth_empirical_cdf
        if (dtype=='betas'):
            ### params = [[alpha,beta,weight] for each component dist]
            self.w = [params[i][2] for i in range(len(params))]
            self.params = params
            self.dists = [stt.beta(a=params[i][0],b=params[i][1]) for i in range(len(params))]
            self._lim_inf, self._lim_sup = 0., 1.
            self._cdf_tab = np.array(np.sort(sample))
            self._proj_tab = np.array([float(i)/self.N for i in range(len(self._cdf_tab))])
            self._cdf = self._betas_cdf
        return None
    def cdf(self, x):
        return self._cdf(x)
    def ppf(self, q): # binary search for all kind of distributions
        lim = 1.
        while((self.cdf(-lim)>0.) or (self.cdf(lim)<1.)):
            lim = lim*10
        x_inf, x_sup = -lim, lim
        xa, xb = x_inf, x_sup
        while((xb-xa)>self.error):
            x = (xb+xa)/2
            qx = self.cdf(x)
            if(qx<q):
                xa = x
            else:
                xb = x
        return np.round(x, decimals=self.error_exp)
    def sample(self, n):
        q = np.random.random(n)
        return np.array([self.ppf(q[i]) for i in range(n)])
    def proj_tab(self):
        return self._proj_tab
    def plot(self, bins=200, title=''):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        x0, l = min(self.Sample)-0.5*(max(self.Sample)-min(self.Sample)), 2*(max(self.Sample)-min(self.Sample))
        x = [x0+((1./(bins))*i*l) for i in range(bins+1)]
        F = [self.cdf(x[i]) for i in range(bins+1)]
        plt.title(title)
        ax.plot(x, F)
        if (self.Type=='smooth_empirical'):
            E = [self._empirical_cdf(x[i]) for i in range(bins+1)]
            ax.plot(x, E, 'r')
        plt.savefig('MARGIN.png')
    def _empirical_cdf(self, x):
        q = 1.0
        for i in range(self.N):
            if (x<self._cdf_tab[i]):
                q = float(i)/self.N
                break
        return q
    def _smooth_empirical_cdf(self, x):
        N, cdf_tab, H, tail_param, h = self.N, self._cdf_tab, self._H, self._tail_param, self._h
        if (x<cdf_tab[0]):
            a, b = tail_param[0][0], tail_param[0][1]
            q = a*np.exp(b*x)
            print('q=',q, '*** x=', x, '*** tail=', tail_param)
        elif (x>cdf_tab[-1]):
            a, b = tail_param[1][0], tail_param[1][1]
            q = 1. - a*np.exp(-b*x)
        else:
            h_args = (x-cdf_tab)/h
            P = [np.dot(H, [h_args[i]**j for j in range(len(H))]) for i in range(N)]
            q = (1./N)*np.sum(P)
        return q
    def _betas_cdf(self, x):
        p = 0.
        for i in range(len(self.dists)): p = p + self.w[i]*self.dists[i].cdf(x)
        return p
    def _smooth_poly(self, k):
        v = np.array([float(1-((-1)**(r+1)))/(r+1) for r in range(2*k+1)])
        C = np.array([[v[j+i] for j in range(k+1)] for i in range(k+1)])
        c = np.linalg.det(C)
        V = np.array([[v[j+i+1] for j in range(k)] for i in range(k+1)])
        K = [((-1)**i)*np.linalg.det(np.delete(V, i, axis=0))/c for i in range(k+1)]
        H = [-np.sum([K[i]*(-1)**(i+1)/(i+1) for i in range(len(K))])] + [K[i]/(i+1) for i in range(len(K))]
        return H
    def _smooth_tail(self, N, cdf_tab, H, h):
        x0 = cdf_tab[0]
        for i in range(1,len(cdf_tab)):
            if(cdf_tab[i]!=x0):
                xr = cdf_tab[i]
                break
                print(i, x0, xr)
        h0_args, hr_args = (x0-cdf_tab)/h, (xr-cdf_tab)/h
        #P = [np.dot(self._H, [h_args[i]**j for j in range(len(self._H))]) for i in range(self.N)]
        q0 = (1./N)*np.sum(np.polynomial.polynomial.polyval(h0_args, H))
        qr = (1./N)*np.sum(np.polynomial.polynomial.polyval(hr_args, H))
        r = (qr-q0)/(xr-x0)
        tail_param = [[q0/(np.exp(x0*r/q0)), r/q0]]
        x0 = cdf_tab[-1]
        for i in range(len(cdf_tab)-1, -1, -1):
            if(cdf_tab[i]!=x0):
                xr = cdf_tab[i]
                break
                print(i, x0, xr)
        h0_args, hr_args = (x0-cdf_tab)/h, (xr-cdf_tab)/h
        #P = [np.dot(self._H, [h_args[i]**j for j in range(len(self._H))]) for i in range(self.N)]
        q0 = (1./N)*np.sum(np.polynomial.polynomial.polyval(h0_args, H))
        qr = (1./N)*np.sum(np.polynomial.polynomial.polyval(hr_args, H))
        r = (q0-qr)/(x0-xr)
        tail_param.append([(1-q0)/(np.exp(-x0*r/(1-q0))), r/(1-q0)])
        return tail_param

class Copula:
    def __init__(self, sample=None, margins=[], ctype='empirical'):
        self.Sample, self.margins, self.ctype = sample, margins, ctype
        self.margins_tab = None # marginal probability projection of sample vectors
        self.copula_tab = None # margins_tab plus copula probability for each sample
        self.ordered_copula_tab = None # copula_tab sequencialy ordered by dimension
        (self.N, self.D) = sample.shape
        if (ctype=='empirical'):
            margins_tab = np.stack(tuple([self.margins[j]._proj_tab for j in range(self.D)]), axis=1) #np.array([self.project(sample[i]) for i in range(self.N)])
            probs = self._calc_SampleProbs(margins_tab)
            copula_tab = np.concatenate((margins_tab, probs), axis=1)
            ordered_margins_tab = self._make_ordered(margins_tab)
            self.ordered_copula_tab = self._make_ordered(copula_tab)
            self.copula_tab = copula_tab[copula_tab[:,self.D-1].argsort()]
            self.margins_tab, self.ordered_margins_tab = margins_tab, ordered_margins_tab
            compute = self._empirical_copula
            #self.margins_tab,self.probs = margins_tab,probs
        self._compute = compute
    def predict(self, x):
        return self.compute(self.project(x))
    def retrieve(self, p):
        return self.deproject(self.decompute(p))
    def compute(self, f):
        return self._compute(f)
    def decompute(self, p):
        p_vec = self.copula_tab[:,-1]
        ind = np.abs(p_vec-p).argmin()
        ind_min, ind_max = ind, ind
        while (p_vec[ind_min]>=p): ind_min = ind_min-1
        while (p_vec[ind_max]<=p): ind_max = ind_max+1
        return self.copula_tab[ind_min:ind_max+1,0:-1].mean(axis=0)
    def project(self, x):
        return [self.margins[j].cdf(x[j]) for j in range(self.D)]
    def deproject(self, f):
        return [self.margins[j].ppf(f[j]) for j in range(self.D)]
    def sample(self, n):
        p = np.random.random(n)
        s = self.retrieve(p)
        return s
    def plot(self, d1, d2, bins=10, title=''):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        rg = [i*(1./(bins)) for i in range(bins+1)]
        XX, YY = np.meshgrid(rg, rg)
        C = []
        for i in range(bins+1):
            c = []
            for j in range(bins+1):
                f = []
                for d in range(self.D):
                    if (d==d1): f.append(XX[i][j])
                    elif (d==d2): f.append(YY[i][j])
                    else: f.append(1.)
                c.append(self.compute(f))
            C.append(c)
        CC = np.array(C)
        plt.title(title)
        ax.plot_surface(XX, YY, CC, cmap=cm.coolwarm, linewidth=0, antialiased=False)
        ax.plot_wireframe(XX, YY, CC, rstride=10, cstride=10)
        plt.savefig('COPULA.png')
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
    def _count_dbox_ordered(self, f, f_sample_ordered):
        ind = self.N-1
        for d in range(self.D):
            for i in range(ind,-1,-1):
                if (f[i,d]>=f_sample_ordered[i,d]):
                    ind = i
                    break
        return ind
    def _count_dbox(self, f, f_sample):
        aux = [tuple([xx[j] for j in range(self.D)]) for xx in f_sample]
        aux = np.array(aux, dtype=[(str(j),float) for j in range(self.D)])
        for j in range(self.D):
            aux = np.sort(aux, order=str(j))
            ind = np.searchsorted(aux[str(j)], f[j], side='right')
            aux = aux[:ind+1]
        return ind+1
        '''
        counter = 0
        for i in range(len(f_sample)):
            if (self._in_dbox(f_sample[i], f)):
                counter = counter + 1
        return counter
        '''
    def _in_dbox(self, f, fbox):
        return not np.any(np.clip(fbox-f, None, 0))
    def _make_ordered(self, tab):
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
    def _empirical_copula(self, f):
        return float(self._count_dbox(f, self.copula_tab[:,0:-1]))/self.N

def modelCopula(mvsample=None,dtype=None,params=None):
    ms = []#[Margin(sample=mvsample[:,i],dtype=dtype,params=params[i]) for i in range(mvsample.shape[1])]
    for i in range(mvsample.shape[1]):
        print('MARGIN '+str(i))
        ms.append(Margin(sample=mvsample[:,i],dtype=dtype,params=params[i]))
    print('COPULA')
    cop = []#Copula(sample=mvsample, margins=ms)
    return ms, cop