#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 27 14:37:46 2019

@author: willian
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('index.html', views.index, name='index'),
    path('doModelingAction', views.doModelingAction, name='doModelingAction'),
    path('defineProj', views.defineProj, name='defineProj'),
    path('selectDataFileOptions', views.selectDataFileOptions, name='selectDataFileOptions'),
    path('data_acquisition', views.data_acquisition, name='data_acquisition'),
    path('data_acquisition_end', views.data_acquisition_end, name='data_acquisition_end'),
    path('load_data_slicing', views.load_data_slicing, name='load_data_slicing'),
    path('forest_import', views.forest_import, name='forest_import'),
    path('selectData', views.selectData, name='selectData'),
    #path('descriptive_stats', views.descriptive_stats, name='descriptive_stats'),
    path('make_description', views.make_description, name='make_description'),
    path('sendFigure', views.sendFigure, name='sendFigure'),
    #path('margin_modeling', views.margin_modeling, name='margin_modeling'),
    path('loadMarginStartData', views.loadMarginStartData, name='loadMarginStartData'),
    path('loadMCMCParams', views.loadMCMCParams, name='loadMCMCParams'),
    #path('makeMargin_roundstep', views.makeMargin_roundstep, name='makeMargin_roundstep'),
    path('makeMCMCMargin', views.makeMCMCMargin, name='makeMCMCMargin'),
    path('makeMCMCMargin_end', views.makeMCMCMargin_end, name='makeMCMCMargin_end'),
    path('makeMargin_end', views.makeMargin_end, name='makeMargin_end'),
    path('sendMarginFigure', views.sendMarginFigure, name='sendMarginFigure'),
    #path('makeAllMargins', views.makeAllMargins, name='makeAllMargins'),
    path('copula_modeling', views.copula_modeling, name='copula_modeling'),
    path('sendCopulaFigure', views.sendCopulaFigure, name='sendCopulaFigure'),
    path('waitProcessing', views.waitProcessing, name='waitProcessing'),
    path('waitProcessing', views.waitProcessing, name='waitProcessing'),
    path('doUploadDataset', views.doUploadDataset, name='doUploadDataset'),
    path('doDownloadResults', views.doDownloadResults, name='doDownloadResults'),
    path('doClearProjects', views.doClearProjects, name='doClearProjects'),
    #path('<str:filepath>/', views.doDownloadResults),
]
