#!/bin/bash

# $1 is the server
# $2 is the user name
# $3 is the password
# $4 is the database name

export PGPASSWORD=$3
psql -h $1 -U $2 $4 < create_spot_view.sql
