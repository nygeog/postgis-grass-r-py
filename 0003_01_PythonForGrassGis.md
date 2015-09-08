# Python Scripts For GRASS GIS #
We briefly explain about Python scripting for GRASS GIS in this page.



# Preliminary settings #

  * To operate GRASS GIS from outside, some environment variables have to be set up. Open bash profile and add following lines.

  1. Open bash profile with vi;
```
vi .bashrc
```
  1. Then, add following lines at the end of the file.
```
export GISBASE="/usr/lib/grass64"
export PATH="$PATH:$GISBASE/bin:$GISBASE/script:$GISBASE/lib"
export PYTHONPATH="${PYTHONPATH}:$GISBASE/etc/python/"
export PYTHONPATH="${PYTHONPATH}:$GISBASE/etc/python/grass"
export PYTHONPATH="${PYTHONPATH}:$GISBASE/etc/python/grass/script"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$GISBASE/lib"
export GIS_LOCK=$$
export GISRC="$HOME/.grassrc6"
```
  1. Now,  you can define the class, which can operate GRASS GIS from the outside.
```
#!/usr/bin/python
# -*- coding: utf-8

import sys, os, numpy, argparse
import grass.script as g
import grass.script.setup as gsetup

class grasswrapper():
	def __init__(self, dbBase="", location="", mapset="PERMANENT"):
		'''
		Wrapper of "python.setup.init" defined in GRASS python.
		Initialize system variables to run scripts without starting GRASS explicitly.
		
		@param dbBase: path to GRASS database (default: '').
		@param location: location name (default: '').
		@param mapset: mapset within given location (default: 'PERMANENT')

		@return: Path to gisrc file.
		'''
		self.gisbase = os.environ['GISBASE']
		self.gisdb = dbBase
		self.loc = location
		self.mapset = mapset
		gsetup.init(self.gisbase, self.gisdb, self.loc, self.mapset)
```

# Accessing GRASS modules from Python script #
> There are two useful functions, which can call GRASS GIS modules; "run\_command()" function and "parse\_command()" function. The former command simply makes run GRASS command from Python script, and the latter command get the results after the execution. The below example shows an example of "g.list" command.
```
>>> from grass.script import core as g
>>> 
>>> g.run_command("g.list", _type="vect")
0
>>> g.parse_command("g.list", _type="vect")
{'----------------------------------------------': None, '': None, 'vector files available in mapset <PERMANENT>:': None, 'buff   diss_2 sites': None}
```

## Using "parse\_command()" ##
> Here, we try to parse the result of "g.list" via "g.parse\_command()".
```
>>> from grass.script import core as g
>>> res = g.parse_command("g.list", _type="vect")
>>> len(res)
4
>>> type(res)
<type 'dict'>
>>> for elem in res:
...     print "Elemet:" + elem
... 
Elemet:----------------------------------------------
Elemet:
Elemet:vector files available in mapset <PERMANENT>:
Elemet:buff   diss_2 sites
```

> The result has four elements of dictionary type, and we should need the 4th element. Now, we try to extract 4th element from the result.
```
>>> res2 = dict.keys(res)[3].split(" ")
>>> res2
['buff', '', '', 'diss_2', 'sites']
```

> In this example, the results includes two unexpected values(Null values) , and we extract valid elements having values.
```
>>> val = []
>>> for i in range(len(res2)):
...     if not res2[i] == "":
...             val.append(res2[i])
... 
>>> val
['buff', 'diss_2', 'sites']
```

> Because it would be great trouble to implement above codes every time, we define new function to get the results of "g.list".
```
def getVectorMap():
	# Parse the command and get results from the GRASS module.
	parse = dict.keys(g.parse_command("g.list", _type="vect"))[3].split(" ")
	# Create a null object to store names of vector maps.
	result = []
	# Add a name of vector map when the value is not empty.
	for i in range(len(parse)):
	     if not parse[i] == "":
		     result.append(parse[i])
	# Finally retun the results.
	return result
```

> To do this, you can get the list of vector maps like below.
```
>>> getVectorMap()
['buff', 'diss_2', 'sites']
```

# Developing "grasswrapper.py" #
> In this section, we introduce some functions defined in our custom class, "grasswrrapper.py".

## Get Grass Database information ##
  * Get database information.
```
	def getDbInfo(self):
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
```

  * Get feature names.
```

	def getFeatName(self, FeatNam, colname):
		nams = g.parse_command('v.db.select',map=FeatNam,columns=colname,quiet=True)
```

  * Get columns list.
```
	def getColums(self, FeatNam):
		desc = g.parse_command('db.describe', flags='c', table=FeatNam)
		return(dict.keys(desc))
```

## Count Geometry ##
  * Count the number of points included in a vector feature.
```
	def getPointsNum(self, FeatNam):
		info = g.parse_command('v.info',flags='t', map=FeatNam, quiet=True)
		n = int(info['points'])
		return(n)
```

  * Count the number of centroids included in a vector feature.
```
	def getCentroidsNum(self, FeatNam):
		info = g.parse_command('v.info',flags='t', map=FeatNam, quiet=True)
		n = int(info['centroids'])
		return(n)
```

  * Count the number of boundaries included in a vector feature.
```

	def getBoundariesNum(self, FeatNam):
		info = g.parse_command('v.info',flags='t', map=FeatNam, quiet=True)
		n = int(info['boundaries'])
		return(n)
```

  * Count the number of lines included in a vector feature.
```
	def getLinesNum(self, FeatNam):
		info = g.parse_command('v.info',flags='t', map=FeatNam, quiet=True)
		n = int(info['lines'])
		return(n)
```
  * Count the number of areas included in a vector feature.
```
	def getAreasNum(self, FeatNam):
		info = g.parse_command('v.info',flags='t', map=FeatNam, quiet=True)
		n = int(info['areas'])
		return(n)
```

## Conducting Geo-processing ##
  * construct convex hulls for each feature.
```
	def createEachHull(self, inmap, outmap):
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
```

  * Get raster values overlapped by a polygon.
```
	def getValOnPolys(self, inmap,poly,elev,dist,output):
		n = getAreasNum(inmap)
		for i in range(n-1):
			g.run_command("v.extract",input=poly,output="tmp",type="area",layer=1,new=-1,list=i+1,quiet=True,overwrite=True)
			g.run_command("v.db.addcol",map="tmp",columns="val int")                    
			g.run_command("v.db.update",map="tmp",column="val",value=1,quiet=True)
			g.run_command("g.region",vect="tmp",quiet=True)
			g.run_command("v.to.rast",input="tmp",output="tmprast",use="val",overwrite=True,quiet=True)
			g.run_command("r.mapcalculator",amap="tmprast",bmap=elev,formula="A*B",outfile="tmprast2",overwrite=True,quiet=True)
			pix = g.parse_command("r.stats",flags="1",input="tmprast2",nv="",fs=",",quiet=True)
			res = "ID_" + str(i+1)                    
			for j in pix.keys():
				res = str(res) + str(j) + ","
			file = open(output + str(i+1) + ".txt", "w")
			file.write(res)
			file.write("\n")
			file.close()
			g.parse_command("g.remove",vect="tmp",rast="tmprast,tmprast2",quiet=True)
			g.parse_command("g.region",rast=elv,quiet=True)
```

## Using "grasswrapper.py" ##
> In order to use your own scripts, which would define some classes and functions, you need to add the path to the python scrips before import your custom classes. For example, you need to add the path for "grasswrapper.py" if you want to call the scripts from other python scripts files.
```
# Add the path for the "grasswrapper.py";
sys.path.append('/path/to/the/pythonscripts/defining/general/functions')

# And Import the wrapper as following.
import grasswrapper
```