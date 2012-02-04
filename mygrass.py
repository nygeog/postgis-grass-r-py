#!/usr/bin/python
# -*- coding: utf-8

import sys, os, numpy, argparse
import psycopg2 as ppg
import grass.script as g
from rpy2 import robjects as ro
from rpy2.robjects.packages import importr as rin

r_base = rin('base')

def getDbInfo():
	dbinfo = g.parse_command('db.connect',flags="p")
	dbstat = {}
	for i in range(len(dbinfo)):
		info = dict.keys(dbinfo)[i].split(":")[0]
		if info == "driver":
			e_key = dict.keys(dbinfo)[i].split(":")[0]
			e_val = dict.keys(dbinfo)[i].split(":")[1]
			driver=None
			if e_val == "pg":
				driver="postgres"
			dbstat[e_key] = driver
	for i in range(len(dbinfo)):
		if not dict.values(dbinfo)[i] == None:
			elems = dict.values(dbinfo)[i].split(",")
			for elem in elems:
				if len(elem.split('=')) > 1:
					e_key = elem.split('=')[0]
					e_val = elem.split('=')[1]
					dbstat[e_key] = e_val
	return(dbstat)

def isExists(FeatNam,FeatType):
	# 'Delete temporal objects.'
	result = False
	vlist = dict.keys(g.parse_command('db.tables',flags='p'))
	for i in range(len(vlist)):
		# Delete the final result if exists.
		if vlist[i] == 'public.'+ str(FeatNam):
			result = True
			print(result)
	return(result)

def getQu(FeatNam,colname):   
	def getQu(FeatNam,colname):   
	# get Calculated Values from the Feature table.
	dt = g.parse_command('v.db.select',flags='c', map=FeatNam ,columns=colname)
	dist = []
	n=len(dt)
	for i in range(n-1):
		dist=dist + [float(dict.keys(dt)[i])]
	# calculate quantile of distance to the nearest point.
	r_dist = ro.FloatVector(dist)
	r_summ = r_base.summary(r_dist)
	return(r_summ)
	dt = g.parse_command('v.db.select',flags='c', map=FeatNam ,columns=colname)
	dist = []
	n=len(dt)
	for i in range(n-1):
		dist=dist + [float(dict.keys(dt)[i])]
	# calculate quantile of distance to the nearest point.
	r_dist = ro.FloatVector(dist)
	r_summ = r_base.summary(r_dist)
	return(r_summ)

def getPointsNum(FeatNam):
        # get number of points.
        info = g.parse_command('v.info',flags='t', map=FeatNam, quiet=True)
        n = int(info['points'])
	return(n)

def getCentroidsNum(FeatNam):
        # get number of points.
        info = g.parse_command('v.info',flags='t', map=FeatNam, quiet=True)
        n = int(info['centroids'])
	return(n)

def getBoundariesNum(FeatNam):
        # get number of points.
        info = g.parse_command('v.info',flags='t', map=FeatNam, quiet=True)
        n = int(info['boundaries'])
	return(n)

def getLinesNum(FeatNam):
	info = g.parse_command('v.info',flags='t', map=FeatNam, quiet=True)
	n = int(info['lines'])
	return(n)

def getAreasNum(FeatNam):
        info = g.parse_command('v.info',flags='t', map=FeatNam, quiet=True)
        n = int(info['areas'])
        return(n)

def getFeatName(FeatNam,colname):
        # get names of sites.
        nams = g.parse_command('v.db.select',map=FeatNam,columns=colname,quiet=True)

def getColums(FeatNam):
	desc = g.parse_command('db.describe', flags='c', table=FeatNam)
	return(dict.keys(desc))

def createEachHull(inmap, outmap):
        n = getAreasNum(inmap)
        if isExists(outmap,'vect') == True:
                g.run_command('g.remove', vect=outmap)
        if isExists('tmp','vect') == True:
                g.run_command('g.remove', vect='tmp')
        if isExists('tmp_hull','vect') == True:
                g.run_command('g.remove', vect='tmp_hull')
        g.run_command('v.edit', tool='create', map=outmap)
        for i in range(n):
                g.run_command('v.extract',input=inmap, list=i+1, output='tmp',type='area', quiet=True, overwrite=True)
                g.run_command('v.hull', input='tmp', output='tmp_hull', quiet=True, overwrite=True)
                g.run_command('v.patch', flags='a', input='tmp_hull', output=outmap, quiet=True, overwrite=True)
		g.run_command('g.remove', vect='tmp,tmp_hull', quiet=True)
		print(i)
	return(True)

# Construct Round-robin Least Cost Path
def createRrlcp(inmap,outmap,elev):
	# Create a empty vector map
	# Create empty vector map
	g.run_command('v.edit', tool='create', map=outmap)
	g.run_command('v.db.addtable', map=outmap, quiet=True)
	g.run_command('v.db.addcol', map=outmap, columns='value int', quiet=True)
	g.run_command('v.db.addcol', map=outmap, columns='org int', quiet=True)
	g.run_command('v.db.addcol', map=outmap, columns='dst int', quiet=True)
	g.run_command('v.db.addcol', map=outmap, columns='len double precision', quiet=True)
	# Create friction raster for 'r.walk' command.
	g.run_command('r.mapcalc',fric=1.0)
	# get number of points
	n = getPointsNum(inmap)
	for i in range(num-1):
	    # Extract ith observation from a vector map.
	    g.run_command('v.extract',list=i+1,input=inmap, output='v_startPoint',type='point', new=i, overwrite=True)  
	    for j in range(num):
		print('Extract'+str(i)+':'+str(j)+'th observation from a vector map.')
		g.run_command('v.extract', quiet=True,list=j+1,input=inmap,output='v_endPoint',type='point',new=j,overwrite=True)
		# Calculate cost distance
		g.run_command('r.walk',quiet=True,elevation=elev,friction=fric,output='r_walk',start_points='v_startPoint',overwrite=True)
		# Draw least cost path
		g.run_command('r.drain',quiet=True,input=wlk,output='r_drain',vector_points='v_startPoint,v_endPoint',overwrite=True)
		# Convert raster to vector
		g.run_command('r.to.vect',quiet=True,flags='s',input='r_drain',output='v_drain',feature='line',overwrite=True)
		g.run_command('v.db.addcol', map=vdrn, columns='value int', quiet=True)
		g.run_command('v.db.addcol', map=vdrn, columns='org int', quiet=True)
		g.run_command('v.db.addcol', map=vdrn, columns='dst int', quiet=True)
		g.run_command('v.db.update', map=vdrn, column='org',val=i+1)
		g.run_command('v.db.update', map=vdrn, column='dst',val=j+1)	
		# Add new vector path to the result
		g.run_command('v.patch',flags='ae',quiet=True,input=vdrn,output=res,overwrite=True)
		g.run_command('v.to.db',map=res,option='length',type='line',col='len',units='me')
		g.run_command('g.remove',quiet=True,vect='v_endPoint,r_walk,r_drain')
	g.run_command('g.remove',quiet=True,rast='friction',vect='v_startPoint')
	return(True)

def selectFromDb(user,password,column,table,host='localhost',query=""):
	dbinfo = getDbInfo()
	dbname=dbinfo['dbname']
	driver=dbinfo['driver']
	conn = ppg.connect("dbname='"+str(dbname)+"' user='"+str(driver)+"' host='"+str(host)+"' password='"+str(password)+"'")
	cur = conn.cursor()
	if query=="" :
		sql = 'select '+str(column)+' from '+str(table)
	else:
		sql = 'select '+str(column)+' from '+str(table)+' '+query
	cur.execute(sql)
	res=cur.fetchall()
	conn.close()
	return res

def getValOnBuffer(inmap,elev,dist,output,user="",password=""):
	# get number of points
	n = getPointsNum(inmap)
	g.run_command('v.db.addcol', map=outmap, columns='pix_vals double array', quiet=True)
	#g.run_command('v.db.addcol', map=outmap, columns='fft_real double array', quiet=True)
	#g.run_command('v.db.addcol', map=outmap, columns='fft_imgn double array', quiet=True)
	# Connect to db server
	dbinfo = getDbInfo()
	dbname=dbinfo['dbname']
	driver=dbinfo['driver']
	conn = ppg.connect("dbname='"+str(dbname)+"' user='"+str(driver)+"' host='"+str(host)+"' password='"+str(password)+"'")
	cur = conn.cursor()
	for i in range(n-1):
		print "Now processing:" + str(i+1) +":" + nams.keys()[i]
		# extract one feature from points set with cat value.
		g.run_command("v.extract",input=inmap,output="tmp",type="point",new=-1,list=i+1,quiet=True,overwrite=True)
		# create buffer of the extracted point
		g.run_command("v.buffer",input="tmp",output="tmp2",type="point",distance=dist,quiet=True,overwrite=True)
		# add attributes table and new a column storing value for the buffer object.
		g.run_command("v.db.addtable",map="tmp2",columns="val double precision",quiet=True)
		# set default value as 1.
		g.run_command("v.db.update",map="tmp2",column="val",value=1,quiet=True)
		# Redefine geographic region for procedure.
		g.run_command("g.region",vect="tmp2",quiet=True)   
		# convert vector map buffer to raster map buffer.
		g.run_command("v.to.rast",input="tmp2",output="tmprast",col="val",overwrite=True,quiet=True)
		# get elevation on the raster buffer.
		g.run_command("r.mapcalculator",amap="tmprast",bmap=elev,formula="A*B",outfile="tmprast2",overwrite=True,quiet=True)    
		nam = i+1
		pix = g.parse_command("r.stats",flags="1",input="tmprast2",nv="",fs=",",quiet=True)
		res = 'ARRAY['
		for j in pix.keys():
			res = res + str(j) + ','
		res = res + ']'
		# Update the column
		sql='UPDATE '+str(inmap)+' SET pix_vals = '+str(pix_vals)+' WHERE cat = '+str(i+1)
		cur.execute(sql)
		# Remove temporal features
		g.parse_command("g.remove",vect="tmp,tmp2",rast="tmprast,tmprast2",quiet=True)
		# Set region with DEM.
		g.parse_command("g.region",rast=elv,quiet=True)
	conn.close()

def getValOnPolys(inmap,poly,elev,dist,output):
	n = getAreasNum(inmap)
	for i in range(n-1):
		# extract one feature from points set with cat value.
		g.run_command("v.extract",input=poly,output="tmp",type="area",layer=1,new=-1,list=i+1,quiet=True,overwrite=True)
		# Add a new column for storing a new value.
		g.run_command("v.db.addcol",map="tmp",columns="val int")                    
		# set default value as 1.
		g.run_command("v.db.update",map="tmp",column="val",value=1,quiet=True)
		# Redefine geographic region for procedure.
		g.run_command("g.region",vect="tmp",quiet=True)
		# convert vector map buffer to raster map buffer.
		g.run_command("v.to.rast",input="tmp",output="tmprast",use="val",overwrite=True,quiet=True)
		# get elevation on the raster buffer.
		g.run_command("r.mapcalculator",amap="tmprast",bmap=elev,formula="A*B",outfile="tmprast2",overwrite=True,quiet=True)
		pix = g.parse_command("r.stats",flags="1",input="tmprast2",nv="",fs=",",quiet=True)
		res = "ID_" + str(i+1)                    
		for j in pix.keys():
			res = str(res) + str(j) + ","
		# Write the result to text file
		file = open(output + str(i+1) + ".txt", "w")
		file.write(res)
		file.write("\n")
		file.close()
		# Remove temporal features
		g.parse_command("g.remove",vect="tmp",rast="tmprast,tmprast2",quiet=True)
		# Set region with DEM.
		g.parse_command("g.region",rast=elv,quiet=True)

