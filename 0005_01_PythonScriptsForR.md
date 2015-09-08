# Introduction #

Under constructing...Please wait for a while.


# Python scripts for R #
```
#-*- coding:utf-8 -*-
from rpy2 import robjects as ro
from rpy2.robjects import r
from rpy2.robjects.packages import importr

def r_vector(x):
	v = ro.FloatVector(x)
	return v	

def r_matrix(x, rows):
	m = r.matrix(ro.FloatVector(x), nrow=rows)
	return m

def r_summary(x):
	rcmd = r["summary"]
	return rcmd(x)

def r_pca(x, argScale=True,argNcp=5, argGraph=False):
	r.library("FactoMineR")
	rcmd = r["PCA"]
	return rcmd(x,scale_unit=argScale,graph=argGraph)

def r_pca_plot(x, argAxes=[1,2], argChoix="ind"):
	r.library("FactoMineR")
	rcmd = r["plot.PCA"]
	raxe = r_vector(argAxes)
	return rcmd(x,choix=argChoix,axes=raxe)

def r_dev_off():
	grdevices = importr('grDevices')
	grdevices.dev_off()

def r_conPgsql(user, passwd, dbname):
	# create a PostgreSQL instance and create one connection.
	r.library("RPostgreSQL")
	rcmd_drv = r["dbDriver"]
	rcmd_con = r["dbConnect"]
	drv = rcmd_drv("PostgreSQL")
	return rcmd_con(drv,user=user,password=passwd,dbname=dbname)

def r_query(con,queryString=""):
	r.library("RPostgreSQL")
	rcmd = r["dbSendQuery"]
	return rcmd(con, queryString)

def r_fetch(query, maxrecord=-1):
	r.library("RPostgreSQL")
	rcmd = r["fetch"]
	return rcmd(query, n=maxrecord)

def r_clearResut(query):
	r.library("RPostgreSQL")
	rcmd = r["dbClearResult"]
	return rcmd(query)	

def r_ListTables(con):
	r.library("RPostgreSQL")
	rcmd = r["dbListTables"]
	return rcmd(con)	
```