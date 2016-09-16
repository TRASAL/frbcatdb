#!/bin/csh

set server = `head -n1 db_secrets.txt`
set usr = `head -n2 db_secrets.txt | tail -n 1`
set pw = `head -n3 db_secrets.txt | tail -n 1`
set db = `head -n4 db_secrets.txt | tail -n 1`

mysqldump --host=$server --user=$usr $db -p$pw > dump_db.dat
