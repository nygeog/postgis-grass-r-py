# How to Construct Database #
Please check the [InstallPostGISOnUbuntu](InstallPostGISOnUbuntu.md) page if you had any problems in following process.



# Create Database #

## Create and Drop database ##
  * Database can be easily created from terminal. Open terminal and type as below.
```
createdb dbname
```

  * You can drop existing database from terminal as well.
```
dropdb dbname
```

## Apply spatial extension ##
  * You'll find following sql files at "**/usr/share/postgresql/9.1/contrib/postgis-2.0**". If you're running PostGIS on Mac OSX 10.6 or later, you'll find these files at "**/usr/local/pgsql-9.1/share/contrib**" and "**/usr/local/pgsql-9.1/share/contrib/postgis-1.5**".
```
# Apply spatial extension to the database.
psql -U [username] -f '/usr/share/postgresql/9.1/contrib/postgis-2.0/postgis.sql' -d [dbname]

# Insert information of spatial reference system to the database.
psql -U [username] -f '/usr/share/postgresql/9.1/contrib/postgis-2.0/spatial_ref_sys.sql' -d [dbname]

# Apply PostGIS raster extension to the database.
psql -U [username] -f '/usr/share/postgresql/9.1/contrib/postgis-2.0/rtpostgis.sql' -d [dbname]

```

# Import existing vector and raster files #
## Import Shapefiles to PostgreSQL ##

  * SQL file is exported by using "shp2pgsql" command. "shp2pgsql" command produce a SQL command file, and which **appends** new commands to the file if the is existed. Therefore, you need to **delete** existing file before you runs this command.
```
shp2pgsql -s 2452 -D -i -I -W UTF8 '/path/to/shapefile.shp' columnname >> '/path/to/sqlfile.sql'
```

  * The command may not work collect in some cases. In such a case, shp2pgsql command may work with following ways.
```
sh '/home/username/postgis-svn/loader/shp2pgsql' -s 2452 -D -i -I -W UTF8 '/path/to/shapefile.shp' columnname >> '/path/to/sqlfile.sql'
```

# Create a template for using PostGIS 2.0 #
```
# Create a new database for the template.
createdb -E UTF8 template_postgis
createlang -d template_postgis plpgsql

# Create the template by using PostGIS sql files.
psql -c "UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis'" -d postgres

# Apply spatial extension to the database.
psql -f /usr/share/postgresql/9.1/contrib/postgis-2.0/postgis.sql -d template_postgis 

# Insert information of spatial reference system to the database.
psql -f '/usr/share/postgresql/9.1/contrib/postgis-2.0/spatial_ref_sys.sql' -d template_postgis

# Apply PostGIS raster extension to the database.
psql -f '/usr/share/postgresql/9.1/contrib/postgis-2.0/rtpostgis.sql' -d template_postgis

psql -c "GRANT ALL ON geometry_columns TO PUBLIC;" -d template_postgis
psql -c "GRANT ALL ON geography_columns TO PUBLIC;" -d template_postgis
psql -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;" -d template_postgis
```