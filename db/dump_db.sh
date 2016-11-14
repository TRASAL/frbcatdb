#!/bin/bash

# $1 is the server
# $2 is the user name
# $3 is the password
# $4 is the database name
# $5 must be the dump file

export PGPASSWORD=$3
pg_dump -h $1 -U $2 $4 > $5
