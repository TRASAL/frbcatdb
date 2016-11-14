#!/bin/bash

# $1 is the server
# $2 is the user name
# $3 is the password
# $4 is the database name
# $5 must be the location of schemaSpy JAR file
# $6 must be the location of JDBC connector JAR file


# We use SchemaSpy to generate a HTML page with the diagram
# INSTALLATION
# First of all, your system should have Java runtime properly installed. Download from https://java.com/en/download/.
# SchemaSpy, which is a .jar file also needs to be downlaoded. Get it here: http://sourceforge.net/projects/schemaspy/files/.
# Also, download the JDBC connector to PostgreSQL. Make sure to match your PostgreSQL version. You can download it from here: http://jdbc.postgresql.org/download.html. You can check your PostgreSQL version by running: “SELECT version();” query on psql prompt.
# Also, SchemaSpy depends on GraphViz to generate the ER-diagrams, so you need to be installed it on your system. Get it from here: http://www.graphviz.org/ (though in Ubuntu for example it can be installed with sudo apt-get install graphviz)
# After it has been installed you can execute this script

java -jar $5 -t pgsql -host $1 -db $4 -u $2 -p $3 -s public -dp $6 -o schema
cp schema/diagrams/summary/*png .

# the schema with the relationships are cp in currernt directory
# you can also open the $7/index.html and graphically explore the diagram
