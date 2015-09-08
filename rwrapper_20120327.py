#-*- coding:utf-8 -*-
from rpy2 import robjects as ro
from rpy2.robjects import r
from rpy2.robjects.packages import importr

def r_vector(x):
	# Create R vector from Python Array type.
	v = ro.FloatVector(x)
	return v	

def r_matrix(x, rows):
	# Create R matrix from Python Array type.
	m = r.matrix(ro.FloatVector(x), nrow=rows)
	return m

def r_summary(x):
	# R summery function.
	rcmd = r["summary"]
	return rcmd(x)

def r_pca(x, argScale=True,argNcp=5, argGraph=False):
	# R PCA function. 
	# The "FactoMineR" package is required.
	r.library("FactoMineR")
	rcmd = r["PCA"]
	return rcmd(x,scale_unit=argScale,graph=argGraph)

def r_pca_plot(x, argAxes=[1,2], argChoix="ind"):
	# R PCA plot function. 
	# The "FactoMineR" package is required.
	r.library("FactoMineR")
	rcmd = r["plot.PCA"]
	raxe = r_vector(argAxes)
	return rcmd(x,choix=argChoix,axes=raxe)

def r_dev_off():
	# Terminate R graphics.
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
	# Query data stored in PostgreSQL database. 
	# The "RPostgreSQL" package is required.
	r.library("RPostgreSQL")
	rcmd = r["dbSendQuery"]
	return rcmd(con, queryString)

def r_fetch(query, maxrecord=-1):
	# Query data stored in PostgreSQL database.
	# The "RPostgreSQL" package is required.
	r.library("RPostgreSQL")
	rcmd = r["fetch"]
	return rcmd(query, n=maxrecord)

def r_clearResut(query):
	# Initialyse query string.
	# The "RPostgreSQL" package is required.
	r.library("RPostgreSQL")
	rcmd = r["dbClearResult"]
	return rcmd(query)	

def r_ListTables(con):
	# Get dataset from PostgreSQL.
	# The "RPostgreSQL" package is required.
	r.library("RPostgreSQL")
	rcmd = r["dbListTables"]
	return rcmd(con)	



