#!/usr/bin/env python
import os
import MySQLdb

dbCredentialsFile = "../db_secrets.txt"
if not os.path.isfile(dbCredentialsFile):
    raise Exception("This script requires the " + dbCredentialsFile + " file. A file with 4 lines with hostname, username, password and dbname")

db = MySQLdb.connect(*open(dbCredentialsFile, 'r').read().split())

cursor = db.cursor()

tables = ["frbs","observations","radio_obs_params","radio_measured_params"]

for table in tables:
    cursor.execute("select id,reference_id from " + table)
    tableHaveRefName = table + "_have_refs"
    rows = cursor.fetchall()
    for row in rows:
        try:
           cursor.execute("INSERT INTO " + tableHaveRefName + " VALUES (%s,%s)", row)
           db.commit()
        except:
           db.rollback()
db.close()
