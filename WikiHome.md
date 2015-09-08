# Table of Contents #
## [How to set up PostgreSQL?](0001_01_SetupPostgreSQL.md) ##
> Because the current PostGIS version does not support raster datasets, we should compile latest PostGIS from source code. In this section, we introduce how to install and to configure PostgreSQL server and PostGIS via subversion(SVN).

## [How to construct Database with PostGIS?](0002_01_ConstructDatabase.md) ##
> After installation of PostgreSQL server and PostGIS, we have to construct a new database supporting Geospatial data. In this section, we instruct how to construct a new database and to import geospatial data from ESRI shapefiles.

## [How to code Python Scripts for GRASS? ](0003_01_PythonForGrassGis.md) ##
> GRASS GIS can be operated from both bash shell and Python shell. We introduce how to use Python to handle GRASS. It will be helpful when we try to operate PostGIS and GRASS GIS at the same time.

## [How to code Python Scripts for PostgreSQL?](0004_01_PythonForPostGis.md) ##
> We need to write SQL statements to handle geospatial data from python scripts, and it would be not difficult for anyone who have experiences for using SQL statements. But, here, we show a python wrapper to handle PostgreSQL server to make it easy to conduct GIS operation by python scripting.