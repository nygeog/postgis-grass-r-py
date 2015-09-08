

# Introduction #
Here we explain about our wrapper for migrating geometry from PostgreSQL to GRASS GIS. The following functions are defined in our Python wrapper (see [How to code Python Scripts for PostgreSQL?](0004_01_PythonForPostGis.md)).

# Migrate geometry from PostGIS to GRASS GIS #
## Export Points to GRASS ##
```
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
```

## Export Ring to GRASS ##
```
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
		widgets = ['EExporting Boundaries: ', Percentage(), ' ', Bar(marker=RotatingMarker()),' ', ETA(), ' ', FileTransferSpeed()]
		pbar = ProgressBar(widgets=widgets, maxval=n+1).start()
		for polygon in polygons:
			# Get a ring of the polygon.
			sql_ring = "ST_ExteriorRing(ST_GeomFromText('" + self.wkb2text(polygon[0]) + "'," + self.srid + "))"
			self.cursor.execute("SELECT " + sql_ring)
			ring = self.cursor.fetchall()
			ring = str(ring[0]).split(",")[0].strip("(").strip("'")

			# Get a centroid of the polygon.
			sql_cent = "SELECT ST_AsText(ST_Centroid(" + sql_ring + "))"
			self.cursor.execute(sql_cent)
			cent = self.cursor.fetchall()
			cent = str(cent[0]).strip("'POINT(").strip(")',")

			# Count the number of control points
			sql_npoints = "SELECT ST_NumPoints(ST_GeomFromText('" + self.wkb2text(ring) + "'," + self.srid + "))"
			self.cursor.execute(sql_npoints)
			p = self.cursor.fetchall()
			p = int(str(p[0]).split(",")[0].strip("(").strip("'"))

			fl.write('B  ' + str(p) + '\n ')
			# Get each point from a ring.
			ctrl = []
			for i in range(1,p):
				sql_ctrl = "SELECT ST_AsEWKT(ST_PointN(ST_GeomFromText('" + self.wkb2text(ring) + "'," + self.srid + "), " + str(i) +"))"
				self.cursor.execute(sql_ctrl)
				fetch_ctrl = self.cursor.fetchall()
				ctrl.append(str(fetch_ctrl[0]).strip("'").split(";")[1].strip("POINT(").strip(")',)"))

			sx = float(ctrl[0].split()[0])
			sy = float(ctrl[0].split()[1])
			for i in range(p-1):
				x = float(ctrl[i].split()[0])	# Coordinate X of the current point.
				y = float(ctrl[i].split()[1])	# Coordinate Y of the current point.
				fl.write(' ' + str(x) + ' ' + str(y) + '\n')

			# Export centroid.
			fl.write(' ' + str(sx) + ' ' + str(sy) + '\n')
			fl.write('C  1 1\n ')
			fl.write(' ' + str(cent.split(" ")[0]) + ' ' + str(cent.split(" ")[1]) + '\n')
			fl.write(' 1     '+ str(polygon[1])+'\n')

			# Update progress bar
			cnt += 1
			pbar.update(cnt)
		pbar.finish()
		fl.close()

		# Import geometries to GRASS database and create a temporal vector map.
		g.run_command('v.in.ascii',flags='n', overwrite=True, input=tmp,output=outmap,format="standard",quiet=True)

		# Delete temporal GRASS standard ASCII file.
		os.remove(tmp)
```