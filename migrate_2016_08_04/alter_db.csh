#!/bin/csh

set server = `head -n1 ../db_secrets.txt`
set usr = `head -n2 ../db_secrets.txt | tail -n 1`
set pw = `head -n3 ../db_secrets.txt | tail -n 1`
set db = `head -n4 ../db_secrets.txt | tail -n 1`

mysql --host=$server --user=$usr $db -p$pw < alter_db1.sql
python alter_db2.py
mysql --host=$server --user=$usr $db -p$pw < alter_db3.sql
