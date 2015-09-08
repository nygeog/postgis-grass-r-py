# How to set up PostgreSQL #

In this wiki, we briefly introduce how to setup PostgreSQL server and PostGIS via SVN. SVN might not be stable, and it might not be compiled because of any problems. Additionally, you need to configure proxy setting if you are working behind proxy. The setting file is located at **~/.subversion/servers**. To do so, you need to open the setting file with your favorite text editor (vim for example), and to configure commented-out lines for proxy setting under the [**global**] tag(around line 142 on the default).



# Install PostgreSQL 9.1 #

  * Ubuntu users may install PostgreSQL using the "apt" utility as below.
```
sudo apt-get install postgresql-9.1
sudo apt-get install pgadmin3
```

  * Domain socket configuration is required to handle both GRASS GIS and PostgreSQL from Python scripts. Settings for domain socket are described in "pg\_hba.conf", and the file can be found at **/etc/postgresql/_[version](version.md)_/main**.
```
sudo vi '/etc/postgresql/9.1/main/pg_hba.conf'
```

  * Comment all lines out after the line "# Database administrative login by Unix domain socket", and append new three lines as below.
```
# Database administrative login by Unix domain socket
# local   all             postgres                                peer

# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
# local   all             all                                     peer
# IPv4 local connections:
# host    all             all             127.0.0.1/32            md5
# IPv6 local connections:
# host    all             all             ::1/128                 md5
# Allow replication connections from localhost, by a user with the
# replication privilege.
#local   replication     postgres                                peer
#host    replication     postgres        127.0.0.1/32            md5
#host    replication     postgres        ::1/128                 md5
local   all             all                                      trust
host    all             all              127.0.0.1/32            trust
host    all             all              ::1/128                 trust

```

  * Add current linux user as a new PostgreSQL user.
```
# Login as postgres
sudo su postgres

# Add a Linux user as a super user with password.
createuser -P -s -e _linuxuser_
Enter password for new role: 
Enter it again: 
CREATE ROLE linuxuser PASSWORD '**********************************' SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN;

# Logout and return to current user.
exit
```

# Install GEOS From SVN #

GEOS is required to install PostGIS via the subversion. The latest version of GEOS can be installed by following process.
  * Install following packages to install PostGIS with raster support.
```
sudo apt-get install subversion
sudo apt-get install libtool
sudo apt-get install libxml2
sudo apt-get install libxml2-dev
sudo apt-get install postgresql-server-dev-9.1
sudo apt-get install swig
```

  * Download source from svn.
```
cd ~
svn checkout http://svn.osgeo.org/geos/trunk geos-svn
cd geos-svn
```

  * You need to configure proxy settings if you would like to access SVN over proxy. Open the configuration file located at "/etc/subversion/servers", and modify the file like below.
```
[global]
http-proxy-exceptions = *.exception.com, www.internal-site.org
http-proxy-host = proxy.domain.com
http-proxy-port = 8080
http-proxy-username = your_account
http-proxy-password = your_password
# http-compression = no
# http-auth-types = basic;digest;negotiate
# No http-timeout, so just use the builtin default.
# No neon-debug-mask, so neon debugging is disabled.
# ssl-authority-files = /path/to/CAcert.pem;/path/to/CAcert2.pem
```

  * Configure
```
./autogen.sh
./configure

```

  * Build check and install
```
make
make check
sudo make install
```

# Install PROJ4 From SVN #

PROJ4 is also required to install PostGIS via the subversion as well as GEOS. The latest version of PROJ4 can be installed by following process.

  * Download source from svn.
```
cd ~
svn checkout http://svn.osgeo.org/metacrs/proj/trunk/proj/
cd proj
```

  * Configure
```
./autogen.sh
./configure

```

  * Build, check and install
```
make
make check
sudo make install
```

# Install GDAL from SVN #
  * Download source from svn.
```
cd ~
svn checkout https://svn.osgeo.org/gdal/branches/1.8/gdal gdal
cd gdal
```

  * Configure
```
./autogen.sh
./configure

```

  * Build and install
```
make
sudo make install
```

# Install PostGIS #
  * Install following packages to install PostGIS with raster support.
```
sudo apt-get install postgresql-server-dev-9.1
sudo apt-get install libproj-dev
```
  * Download source from svn.
```
cd ~
svn checkout https://svn.osgeo.org/postgis/trunk postgis-svn
cd postgis-svn
```

  * Configure
```
./autogen.sh
./configure --with-raster
```

  * Build and install
```
make
sudo make install
```