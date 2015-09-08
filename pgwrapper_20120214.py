#!/usr/bin/python
# -*- coding: utf-8
import sys, os, math, numpy, argparse
import psycopg2 as ppg
import grass.script as g
from rpy2 import robjects as ro
from rpy2.robjects.packages import importr as rin
from progressbar import * 

r_base = rin('base')

class pgwrapper:
	def __init__(self,dbname, srid, host='localhost',user='',passwd=''):
		self.dbname = dbname			# Database name which connect to.
		self.srid = str(srid)			# Identifier of spatial reference system.
		self.host = host			# Host name (default is "localhost")
		self.user = user			# User name for login to the database.
		self.password = passwd			# Password for login to the database. 
		self.connection = self.setConnect()	# Set a onnection to the database
		self.cursor = self.setCursor()		# Generate cursor.

	def setConnect(self):
		conn = ppg.connect(
			"dbname='" + self.dbname + 
			"' user='" + self.user + 
			"' host='" + self.host + 
			"' password='" + self.password + "'")
		return conn

	def tableExists(self, table):
		sql_exists = "SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='" + table + "')"
		self.cursor.execute(sql_exists)
		return self.cursor.fetchone()[0]

	def columnExists(self, table, column):
		sql_exists = "SELECT EXISTS(SELECT * FROM information_schema.columns WHERE table_name='" + table + "' AND column_name = '" + column +"')"
		self.cursor.execute(sql_exists)
		return self.cursor.fetchone()[0]

	def setCursor(self):
		return self.connection.cursor()

	def createTable(self, table, columns):
		parse = ''
		for i in range(len(columns)):
			parse = parse + str(dict.keys(columns)[i]) + ' ' + str(dict.values(columns)[i]) + ', '
		parse = parse.rstrip(', ')
		sql_create = 'CREATE TABLE "' + table + '" (' + parse + ')'
		self.cursor.execute(sql_create)

	def count(self, table):
		"""!Count the number of rows.
		@param table		: Name of the table to count rows.
		"""
		sql_count='SELECT COUNT(*) FROM "' + table + '"'
		self.cursor.execute(sql_count)
		n=self.cursor.fetchall()[0][0]
		return n

	def insert(self,table, columns):
		# Make a SQL statement.
		parse_cols = '' 
		parse_vals = '' 
		for i in range(len(columns)):
		        parse_cols = parse_cols + str(dict.keys(columns)[i]) + ','
		
		for i in range(len(columns)):
		        parse_vals = parse_vals + "'" +  str(dict.values(columns)[i]) + "', "

		parse_cols = parse_cols.rstrip(', ')
		parse_vals = parse_vals.rstrip(', ')

		sql_ins = 'INSERT INTO "' + table + '" (' + parse_cols + ') VALUES (' + parse_vals + ');'
		# Excute the SQL statement.
		self.cursor.execute(sql_ins)

	def select(self,table,columns,where=''):
		"""!Query and get the results of query.
		@param table		: Name of the table to parse.
		@param columns		: Name of columns to parse separating with comma(,).
		@param where		: Advanced search option for 'where' statement.
		"""
		# Make a SQL statement.
		if where=='':
			sql_select = 'SELECT '+columns+' FROM "'+table +'"'
		else:
		        sql_select = 'SELECT '+columns+' FROM '+table+' WHERE '+where
		# Excute the SQL statement.
		self.cursor.execute(sql_select)
		# Get the results.
		results = self.cursor.fetchall()
		# Return the results.
		return results

	def updatecol(self, table, columns, where=''):
		"""!Update the values of columns.
		@param table		: Name of the table to parse.
		@param columns		: Keys values pair of column names and values to update.
		@param where		: Advanced search option for 'where' statement.
		"""
		# Make a SQL statement.
		parse = '' 
		for i in range(len(columns)):
		        parse = parse + '"' + str(dict.keys(columns)[i]) + '"=' + str(dict.values(columns)[i]) + ','
		parse = parse.rstrip(',')

		if where=='':
		        sql_update_col = 'UPDATE "' + table + '" SET ' + parse
		else:
		        sql_update_col = 'UPDATE "' + table + '" SET ' + parse + ' WHERE ' + where
		# Excute the SQL statement.
		self.cursor.execute(sql_update_col)

	def addcol(self, table, column, dtype):
		"""!Add a column to the tabale.
		@param table		: Name of the table to add to.
		@param column		: Name of a column for adding.
		@param dtype		: Data type of the new column.
		"""
		# Make a SQL statement.
		sql_addcol = 'ALTER TABLE "'+ table +'" ADD COLUMN "' + column + '" ' + dtype
		# Excute the SQL statement.
		self.cursor.execute(sql_addcol)

	def dropcol(self, table,column):
		"""!Drop a column from the table.
		@param table		: Name of the table.
		@param column		: Name of the column to drop.
		"""
		# Make a SQL statement.
		sql_dropcol = 'ALTER TABLE "' + table +'" DROP COLUMN "' + column + '"'
		# Excute the SQL statement.
		self.cursor.execute(sql_dropcol)

	def addgeomcol(self, table, column, gtype, dim = 2):
		"""!Add a geometry column to the table.
		@param table		: Name of the table.
		@param column		: Name of the column for adding.
		@param gtype		: Geometry type of the new column.
		@param dim		: Dimension of the geometry. default is 2.
		"""
		# Make a SQL statement.
		parse = "'public','"+ table + "','" + column + "'," + self.srid + ",'" + gtype + "'," + str(dim)
		sql_addgeomcol = 'SELECT AddGeometryColumn (' + parse + ');'
		# Excute the SQL statement.
		self.cursor.execute(sql_addgeomcol)

	def dropConstraintSrid(self, table, column):
		"""!Drop information of spatial reference system.
		@param table		: Name of the table.
		@param column		: Name of the column to drop.
		"""
		# Make a SQL statement.
		sql_drop_constraint='ALTER TABLE "' + table + '" DROP CONSTRAINT "enforce_srid_' + column + '"'
		# Excute the SQL statement.
		self.cursor.execute(sql_drop_constraint)

	def addConstraintSrid(self, table, column):
		"""!Add information of spatial reference system.
		@param table		: Name of the table.
		@param column		: Name of the column to add SRID constraint.
		"""
		# Make a SQL statement.
		sql_update_srid='UPDATE "' + table + '" SET "' + column+'" = ST_SetSRID("' + column + '",'+ self.srid + ')'
		# Excute the SQL statement.
		self.cursor.execute(sql_update_srid)
		# Make a SQL statement.
		'''
		sql_update_srid_c = 'ALTER TABLE "' + table + '" ADD CONSTRAINT "enforce_srid_' + column + '" CHECK(SRID("' + column + '")='+ self.srid +')'
		# Excute the SQL statement.
		self.cursor.execute(sql_update_srid_c)
		'''

	def wkb2text(self, wkb):
		"""!Convert OGC Well Known Binary(WKB) format to OGC Enhanced Well Known Text(EWKT) format.
		@param wkb	: Input binary.
		"""
		# Make a SQL statement.
		sql_select = "SELECT ST_AsEWKT('"+ wkb + "'::geometry)"
		# Excute the SQL statement.
		self.cursor.execute(sql_select)
		# Get the results.
		results = self.cursor.fetchall()[0][0].split(";")[1]
		# Returns the results.
		return results

	def spatialQuery_pointsOnPolygon(self, points, polygons, columnlist, pointGeom="geom", polyGeom="geom", pointId="gid", polyId="gid"):
		"""!Query from spatial condition.
		@param points		: Points contained within polygons.
		@param polygons		: Poygons containing points.
		@param colmuns		: Columns for summary, which specified by dictionary type..
		@param pointGeom	: Name of the geometry column of points.
		@param polyGeom		: Name of the geometry column of polygons
		@param pointId		: Identifier of the geometry column of points.
		@param polyId		: Identifier of the geometry column of polygons
		"""
		# columns = {"n_dist":"max"}
		# The name of the column for storing the identifier of the containing buffer.
		b_cont = "container"
		if not self.columnExists(points,b_cont):
			self.addcol(points, b_cont,"int")
		# The name of the column for storing the number of points included in the buffer.
		p_cnt = "pointsnum"
		if not self.columnExists(points, p_cnt):
			self.addcol(points, p_cnt,"int")
		colnams = {}
		colnams['p.' + pointId + ', '] = 0
		for i in range(len(columnlist)):
			summtype = str(dict.values(columnlist[i])[0])
			summclmn = str(dict.keys(columnlist[i])[0])
			colnams['p.' + str(dict.keys(columnlist[i])[0]) + ', '] = 0 + i
			if summtype == "average":
				if not self.columnExists(points, summclmn + "_ave"):
					self.addcol(points, summclmn + "_ave", "numeric")
			elif summtype == "sum":
				if not self.columnExists(points, summclmn + "_sum"):
					self.addcol(points, summclmn + "_sum", "numeric")
			elif summtype == "median":
				if not self.columnExists(points, summclmn + "_med"):
					self.addcol(points, summclmn + "_med", "numeric")
			elif summtype == "max":
				if not self.columnExists(points, summclmn + "_max"):
					self.addcol(points, summclmn + "_max", "numeric")
			elif summtype == "min":
				if not self.columnExists(points, summclmn + "_min"):
					self.addcol(points, summclmn + "_min", "numeric")
			elif summtype == "count":
				if not self.columnExists(points, summclmn + "_count"):
					self.addcol(points, summclmn + "_count", "int")
		colnams_sort = colnams.keys()
		colnams_sort.sort()
		self.connection.commit()
		n = self.count(polygons)	# Number of polygon features.
		m = self.count(points)		# Number of Points features.
		# Select polygon features which contains points.
		polygons = self.select(polygons, polyGeom + "," + polyId)
		# Parse colums.
		parse = ''
		for i in range(len(colnams_sort)):
			parse = parse + str(colnams_sort[i])
		parse = parse.rstrip(" ").rstrip(",")
		# Counter for progress bar.
		cnt = 0
		# Create a progress bar object.
		widgets = ['CONSTRUCTING BUFFER: ', Percentage(), ' ', Bar(marker=RotatingMarker()),' ', ETA(), ' ', FileTransferSpeed()]
		pbar = ProgressBar(widgets=widgets, maxval=n+1).start()
		for polygon in polygons:
			# Get a containing polygon.
			container = self.wkb2text(polygon[0])
			# SQL string for converting the polygon to a geometry.
			sql_poly = "(SELECT ST_AsEWKT(ST_GeomFromText('" + container + "'," + self.srid + ")))"
			# SQL string for judging contains.
			sql_cnt = "ST_Contains(" + sql_poly + ",p." + pointGeom + ")"
			# SQL string for selecting points contained by the polygon.
			sql_pts = 'SELECT ' + parse + ' FROM ' + points + ' as p  WHERE ' + sql_cnt
                        # Excute SQL and get the results.
			self.cursor.execute(sql_pts)
			contained = self.cursor.fetchall()
			# Get the number of points.
			nums = len(contained)
			# Get the unique ID of the polygon.
			gid = str(polygon[1])
			if nums > 0:
				# Generate keys-values pair for updating columns.
				key={b_cont:gid, p_cnt:str(nums)}
				for i in range(len(columnlist)):
					summtype = str(dict.values(columnlist[i])[0])
                                        summclmn = str(dict.keys(columnlist[i])[0])
					if summtype == "average":
						value = 0
						for j in range(nums):
							value = value + float(contained[j][1])
						ave = value/nums
						key[summclmn + "_ave"] = ave
					elif summtype == "sum":
						value = 0
						for j in range(nums):
							value = value + float(contained[j][1])
						key[summclmn + "_sum"] = value
					elif summtype == "median":
						vals = []
						for j in range(nums):
							vals.append(float(contained[j][1]))
						value = 0
						if len(vals) % 2 == 1:
							value = vals[(len(vals)+1)/2-1]
						else:
							lower = vals[len(vals)/2-1]
							upper = vals[len(vals)/2]
							value = (float(lower + upper)) / 2
						key[summclmn + "_med"] = value
					elif summtype == "max":
						value = 0
						for j in range(nums):
							value = max(value, float(contained[j][1]))
						key[summclmn + "_max"] = value
					elif summtype == "min":
						value = float(sys.float_info.max)
						for j in range(nums):
							value = min(value, float(contained[j][1]))
						key[summclmn + "_min"] = value
					elif summtype == "count":
						value = 1
						for j in range(nums):
							value += 1
						key[summclmn + "_count"] = value
				for j in range(nums):
					pntkey = int(contained[j][0])
					# Generate "WHERE" keyword.
					where='gid='+str(pntkey)
					# Update the table.
					self.updatecol(points, key, where)

			cnt = cnt + 1
			pbar.update(cnt+1)

		pbar.finish()

	def bufferFromSize(self, table, size, idcol="gid", inGeom="geom",outGeom="buffer"):
		"""!Create buffer by specific buffer seize.
		@param table	: The teble defines center of buffer.
		@param size	: Size of buffer.
		@param idcol	: Identifier of the input table.
		@param inGeom	: Name of the geometry column of input table.
		@param outgeom	: Name of the geometry column adding to.
		"""
		# Add a column to store buffer
		self.addgeomcol(table, outGeom, "POLYGON", dim=2)
		# Count the number of feature.
		n = self.count(table)
		# Counter for progress bar.
		cnt = 0
		# Create a progress bar object.
		widgets = ['CONSTRUCTING BUFFER: ', Percentage(), ' ', Bar(marker=RotatingMarker()),' ', ETA(), ' ', FileTransferSpeed()]
		pbar = ProgressBar(widgets=widgets, maxval=n+1).start()
		# Get points of center for constructing buffers.
		points = self.select(table, inGeom + ',' + idcol)
		for point in points:
			center = self.wkb2text(point[0])
			gid = point[1]
			# Create buffer with specific column
			buff = "ST_Buffer(ST_GeomFromText('"+ center +"', "+self.srid+"), "+size+")"
			# Update column for storing buffer.
			where = idcol + '=' + str(gid)
			keys={outGeom:buff}
			self.updatecol(table,keys,where)
			# Update progress bar
			cnt += 1
			pbar.update(cnt)

		self.addConstraintSrid(table, outGeom)
		pbar.finish()		

	def bufferFromColumn(self, table, column, idcol="gid", inGeom="geom",outGeom="buffer"):
		"""!Create buffer by specific buffer seize.
		@param table	: The teble defines center of buffer.
		@param column	: The column defines sizes of buffer.
		@param idcol	: Identifier of the input table.
		@param inGeom	: Name of the geometry column of input table.
		@param outgeom	: Name of the geometry column adding to.
		"""
		# Add a column to store buffer
		self.addgeomcol(table, outGeom, "POLYGON", dim=2)
		# Count the number of feature.
		n = self.count(table)
		# Counter for progress bar.
		cnt = 0
		# Create a progress bar object.
		widgets = ['CONSTRUCTING BUFFER: ', Percentage(), ' ', Bar(marker=RotatingMarker()),' ', ETA(), ' ', FileTransferSpeed()]
		pbar = ProgressBar(widgets=widgets, maxval=n+1).start()
		# Get points of center for constructing buffers.
		points = self.select(table, inGeom + ',' + idcol + ',' + column)
		for point in points:
			center = self.wkb2text(point[0])	# Get the center of buffer.
			gid = str(point[1])			# Get gid for query.
			dst = str(point[2])			# Get size from
			# Create buffer with specific column
			buff = "ST_Buffer(ST_GeomFromText('" + center + "', " + self.srid + ")," + dst +")"
			# Update column for storing buffer.
			where = idcol + ' = ' + gid
			keys={outGeom:buff}
			self.updatecol(table,keys,where)
			# Update progress bar
			cnt += 1
			pbar.update(cnt)

		self.addConstraintSrid(table, outGeom)
		pbar.finish()	

	def merge(self, inmap, outtable, column = 'geom'):
		"""!Merge geometries.
		@param inmap	: Input table for merge.
		@param outtable	: Name of table to store the results.
		@param column	: Name of the geometry column for merge.
		"""
		# Make a SQL statement.
		sql_union = 'SELECT ST_Multi(ST_Union("' + column + '")) AS geom FROM ' + inmap
		sql_dump = 'SELECT (ST_Dump(geom)).geom as geom FROM (' + sql_union + ') AS dummy'
		sql_merge = 'CREATE TABLE "' + outtable + '" AS ' + sql_dump
		# Excute the SQL statement.
		self.cursor.execute(sql_merge)
		# Make a SQL statement.
		sql_gid_union='ALTER TABLE "' + outtable + '" ADD COLUMN gid serial'
		# Excute the SQL statement.
		self.cursor.execute(sql_gid_union)

	def intersect(self, table_A, table_B, outtable, geom_A, geom_B):
		"""!Intersects overlapped geometries.
		@param table_A	: Input table for merge.
		@param table_B	: Input table for merge.
		@param outtable	: Name of table to store the results.
		@param geom_A	: Name of the geometry column for intersection.
		@param geom_B	: Name of the geometry column for intersection.
		"""
		# Make a SQL statement.
		sql_geom = "a." + geom_A + ", " + "b." + geom_B
		sql_from = " FROM " + table_A + " as a, " + table_B + " as b"
		sql_overlaps = "ST_Overlaps(a." + geom_A + ", b." + geom_B + ")"
		sql_intersect = "SELECT  ST_Intersection(" + sql_geom +")" + sql_from + " WHERE " + sql_overlaps		
		sql_create = 'CREATE TABLE "' + outtable + '" AS (' + sql_intersect + ')'
		# Excute the SQL statement.
		self.cursor.execute(sql_create)

	def efd(self, table, geom="geom", gid="gid", outtable="output", harmonix=20, normalized=True):
		# Create the new table to store the results.
		arrType = "numeric[" + str(harmonix) + "]"
		cols={"gid":"integer",
			"theta":"numeric",
			"alpha":"numeric",
			"beta":"numeric",
			"phi":"numeric",
			"ee":"numeric",
			"a":arrType,
			"b":arrType,
			"c":arrType,
			"d":arrType}
		self.createTable(outtable, cols)
		# Count the number of polygons.
		n = self.count(table)
		polygons = self.select(table, geom + "," + gid)
		# Counter for progress bar.
		cnt = 0
		# Create a progress bar object.
		widgets = ['Eliptic Fourier Transform: ', Percentage(), ' ', Bar(marker=RotatingMarker()),' ', ETA(), ' ', FileTransferSpeed()]
		pbar = ProgressBar(widgets=widgets, maxval=n+1).start()
		for polygon in polygons:
			A = []	# The list of Fourier descriptor for Cosine of F(x)
			B = []	# The list of Fourier descriptor for sine of F(x)
			C = []	# The list of Fourier descriptor for Cosine of G(x)
			D = []	# The list of Fourier descriptor for sine of G(x)
			pram_theta = 0
			pram_alpha = 0
			pram_beta = 0
			param_phi = 0
			param_ee = 0

			# Get a ring of the polygon.
			sql_ring = "SELECT ST_ExteriorRing(ST_GeomFromText('" + self.wkb2text(polygon[0]) + "'," + self.srid + "))"
			self.cursor.execute(sql_ring)
			ring = self.cursor.fetchall()
			ring = str(ring[0]).split(",")[0].strip("(").strip("'")
			# Count the number of control points
			sql_npoints = "SELECT ST_NumPoints(ST_GeomFromText('" + self.wkb2text(ring) + "'," + self.srid + "))"
			self.cursor.execute(sql_npoints)
			p = self.cursor.fetchall()
			p = int(str(p[0]).split(",")[0].strip("(").strip("'"))
			# Calculate total length of the ring.
			sql_npoints = "SELECT ST_Length(ST_GeomFromText('" + self.wkb2text(ring) + "'," + self.srid + "))"
			self.cursor.execute(sql_npoints)
			l = self.cursor.fetchall()
			l = float(str(l[0]).split(",")[0].strip("(").strip("'"))
			# Get each point from a ring.
			ctrl = []
			for i in range(1,p):
				sql_ctrl = "SELECT ST_AsEWKT(ST_PointN(ST_GeomFromText('" + self.wkb2text(ring) + "'," + self.srid + "), " + str(i) +"))"
				self.cursor.execute(sql_ctrl)
				fetch_ctrl = self.cursor.fetchall()
				ctrl.append(str(fetch_ctrl[0]).strip("'").split(";")[1].strip("POINT(").strip(")',)"))
			# Calculate the length from start point to each point.
			ti = []
			ti.append(float(0))
			sx = float(ctrl[0].split()[0])			# Coordinate X of the start point.
			sy = float(ctrl[0].split()[1])			# Coordinate Y of the start point
			for i in range(p-2):
				thisXi = float(ctrl[i].split()[0])	# Coordinate X of the current point.
				thisYi = float(ctrl[i].split()[1])	# Coordinate Y of the current point.
				nextXi = float(ctrl[i+1].split()[0])	# Coordinate X of the next point.
				nextYi = float(ctrl[i+1].split()[1])	# Cootdinate Y of the next point.
				distX = float(thisXi - nextXi)		# Distance of X between current and next point.
				distY = float(thisYi - nextYi)		# Distance of Y between current and next point.
				# Add to the list of distances.
				ti.append(ti[i] + (numpy.sqrt(distX ** 2 + distY ** 2)))
			# Append the total length to the list of distances.
			ti.append(l)
			# Calculate the Fourier descriptors.
			for i in range(harmonix):
				Ai = 0	# Fourier descriptor for Cosine of F(x) in i_th haromonix.
				Bi = 0	# Fourier descriptor for sine of F(x) in i_th haromonix.
				Ci = 0	# Fourier descriptor for Cosine of G(x) in i_th haromonix.
				Di = 0	# Fourier descriptor for sine of G(x) in i_th haromonix.
				for j in range(p-2):
					t1 = ti[j]
					t2 = ti[j+1]
					CosT1 = numpy.cos((2 * numpy.pi * (i + 1) * t1)/l)
					CosT2 = numpy.cos((2 * numpy.pi * (i + 1) * t2)/l)
					SinT1 = numpy.sin((2 * numpy.pi * (i + 1) * t1)/l)
					SinT2 = numpy.sin((2 * numpy.pi * (i + 1) * t2)/l)
					# Calculate Elliptic Fourier Descriptor for F(x)
					thisXi = float(ctrl[j].split()[0])
					NextXi = float(ctrl[j+1].split()[0])
					Ai = Ai+((CosT2-CosT1)*(((NextXi-thisXi)*l)/(t2-t1)))/(4*(numpy.pi**2)*((i + 1)**2))
					Bi = Bi+((SinT2-SinT1)*(((NextXi-thisXi)*l)/(t2-t1)))/(4*(numpy.pi**2)*((i + 1)**2))
					# Calculate Elliptic Fourier Descriptor for G(x)
					thisYi = float(ctrl[j].split()[1])
					nextYi = float(ctrl[j+1].split()[1])
					Ci = Ci+((CosT2-CosT1) * (((nextYi-thisYi)*l)/(t2-t1)))/(4*(numpy.pi**2)*((i + 1)**2))
					Di = Di+((SinT2-SinT1) * (((nextYi-thisYi)*l)/(t2-t1)))/(4*(numpy.pi**2)*((i + 1)**2))
				# Normalize the Fourier descriptors.
				if normalized == True:
					X = Ai**2+Ci**2-Bi**2-Di**2
					Y = 2*(Ai*Bi+Ci*Di)

					pram_theta = 0.5*(math.atan2(Y, X))
					pram_alpha = Ai*numpy.cos(pram_theta)+Bi*numpy.sin(pram_theta)
					pram_beta = Ci*numpy.cos(pram_theta)+Di*numpy.sin(pram_theta)
					param_phi = math.atan2(pram_beta,pram_alpha)
					param_ee = numpy.sqrt(pram_alpha**2+pram_beta**2)

					SinTheta = numpy.sin(pram_theta*(i + 1))
					CosTheta = numpy.cos(pram_theta*(i + 1))
					SinPhi = numpy.sin(param_phi)
					CosPhi = numpy.cos(param_phi)

					A.append(((CosPhi*Ai+SinPhi*Ci)*(CosTheta)+(CosPhi*Bi+SinPhi*Di)*SinTheta)/param_ee)
					B.append(((CosPhi*Ai+SinPhi*Ci)*(-1*SinTheta)+(CosPhi*Bi+SinPhi*Di)*CosTheta)/param_ee)
					C.append(((-1*SinPhi*Ai+CosPhi*Ci)*(CosTheta)+(-1*SinPhi*Bi+CosPhi*Di)*SinTheta)/param_ee)
					D.append(((-1*SinPhi*Ai+CosPhi*Ci)*(-1*SinTheta)+(-1*SinPhi*Bi+CosPhi*Di)*CosTheta)/param_ee)

				else:
					#res$centroid[1] = baika.centroid(ctrlPts, IDvar=IDvar)$coord[1]
					#res$centroid[2] = baika.centroid(ctrlPts, IDvar=IDvar)$coord[2]            
					A.append(Ai)
					B.append(Bi)
					C.append(Ci)
					D.append(Di)
			# Write to the table.
			keys = {"gid":polygon[1],
				"theta":pram_theta,
				"alpha":pram_alpha,
				"beta":pram_beta,
				"phi":param_phi,
				"ee":param_ee,
				"a":str(A).replace('[','{').replace(']','}'), 
				"b":str(B).replace('[','{').replace(']','}'),
				"c":str(C).replace('[','{').replace(']','}'),
				"d":str(D).replace('[','{').replace(']','}')}
			self.insert(outtable,keys)
			# Update progress bar
			cnt += 1
			pbar.update(cnt)

		pbar.finish()	

	def exportGrassAscii_points(self, table, outmap, geom="geom", gid="gid"):
		"""!Intersects overlapped geometries.
		@param table	: The name of the table for search.
		@param outmap	: The name of GRASS vector map exported to.
		@param geom	: Columns for query.
		@param gid	: Unique value of the table, and is used for cat on GRASS.
		"""
		n = self.count(table)
		columns = gid + ",ST_X(" + geom + "), ST_Y(" + geom + ")"
		res = self.select(table,columns)

		# Export the result as GRASS standard ASCII format.
		tmp="grasspt_tmp.txt"	# The name of exported text file.

		# Create a file object.
		fl = open(tmp, "w")
		gpnt = ""
		for pt in res:
			gpnt = str(gpnt)+'P  1 1\n '+str(pt[1])+' '+str(pt[2])+'\n  1     '+str(pt[0])+'\n'

		fl.write(gpnt)
		fl.close()

		# Import to GRASS database and create a temporal vector map.
		g.run_command('v.in.ascii',flags='n', overwrite=True, input=tmp,output=outmap,format="standard",quiet=True)

		# Delete temporal GRASS standard ASCII file.
		os.remove(tmp)

	def exportGrassAscii_ring(self, table, outmap, geom="geom", gid="gid"):
		"""!Intersects overlapped geometries.
		@param table	: The name of the table for search.
		@param outmap	: The name of GRASS vector map exported to.
		@param geom	: Columns for query.
		@param gid	: Unique value of the table, and is used for cat on GRASS.
		"""
		# Export the result as GRASS standard ASCII format.
		tmp="grasspt_tmp.txt"	# The name of exported text file.

		# Create a file object.
		fl = open(tmp, "w")

		# Count the number of polygons.
		n = self.count(table)
		polygons = self.select(table, geom + "," + gid)
		# Counter for progress bar.
		cnt = 0
		# Create a progress bar object.
		widgets = ['EExporting Ring of Polygon: ', Percentage(), ' ', Bar(marker=RotatingMarker()),' ', ETA(), ' ', FileTransferSpeed()]
		pbar = ProgressBar(widgets=widgets, maxval=n+1).start()
		for polygon in polygons:
			# Get a ring of the polygon.
			sql_ring = "SELECT ST_ExteriorRing(ST_GeomFromText('" + self.wkb2text(polygon[0]) + "'," + self.srid + "))"
			self.cursor.execute(sql_ring)
			ring = self.cursor.fetchall()
			ring = str(ring[0]).split(",")[0].strip("(").strip("'")

			# Count the number of control points
			sql_npoints = "SELECT ST_NumPoints(ST_GeomFromText('" + self.wkb2text(ring) + "'," + self.srid + "))"
			self.cursor.execute(sql_npoints)
			p = self.cursor.fetchall()
			p = int(str(p[0]).split(",")[0].strip("(").strip("'"))

			fl.write('B  ' + str(p-1) + '\n ')

			# Get each point from a ring.
			ctrl = []
			for i in range(1,p):
				sql_ctrl = "SELECT ST_AsEWKT(ST_PointN(ST_GeomFromText('" + self.wkb2text(ring) + "'," + self.srid + "), " + str(i) +"))"
				self.cursor.execute(sql_ctrl)
				fetch_ctrl = self.cursor.fetchall()
				ctrl.append(str(fetch_ctrl[0]).strip("'").split(";")[1].strip("POINT(").strip(")',)"))

			for i in range(p-1):
				x = float(ctrl[i].split()[0])	# Coordinate X of the current point.
				y = float(ctrl[i].split()[1])	# Coordinate Y of the current point.
				fl.write(str(x)+' '+str(y) + '\n ')

			# fl.write('1     '+ str(polygon[1])+'\n')
			# Update progress bar
			cnt += 1
			pbar.update(cnt)
		fl.close()
		pbar.finish()	

		# Import to GRASS database and create a temporal vector map.
		g.run_command('v.in.ascii',flags='n', overwrite=True, input=tmp,output=outmap,format="standard",quiet=True)

		# Delete temporal GRASS standard ASCII file.
		os.remove(tmp)
