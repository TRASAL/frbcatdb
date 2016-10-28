#!/bin/csh

# $1 is the server
# $2 is the user name
# $3 is the password
# $4 is the database name

mysql --host=$1 --user=$2 -p$3 -e "create database $4"
mysql --host=$1 --user=$2 -p$3 $4 < create_db_tables.sql
