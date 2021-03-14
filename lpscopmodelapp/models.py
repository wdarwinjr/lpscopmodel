from django.db import models
#from django.contrib.postgres.fields import ArrayField

class Project(models.Model):
    name = models.TextField(default='default')
    file_list = models.TextField(default='{}')
    df_pklfname = models.TextField(default='default')
    filter_text = models.TextField(default='{}')
    feature_list = models.TextField(default='{}')
    value_list = models.TextField(default='{}')
    val_mtx = models.TextField(default='{}')
    conc_mtx = models.TextField(default='{}')
    margins = models.TextField(default='{}')
    feature = models.TextField(default='{}')
    space_col = models.TextField(default='')
    time_col = models.TextField(default='')
    margins_tab = models.TextField(default='{}')
    copula_tab = models.TextField(default='{}')
    stage = models.IntegerField(default=0)

class Figure(models.Model):
    proj_name = models.TextField(default='default')
    fname = models.TextField(default='default')
    fbody = models.BinaryField(default=None)
