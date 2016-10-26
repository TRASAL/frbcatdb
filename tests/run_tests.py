#!/usr/bin/env python
import os, sys
import MySQLdb

dbName = 'frbcatdb_test'

os.system("mysql " + dbName + " < ../create_db.sql")
os.system("mysql " + dbName + " < fill_db_test_data.sql")

c = MySQLdb.connect('localhost','travis_pymysql','password',dbName)
cursor = c.cursor()
n = cursor.execute('SELECT * from frbs')
if n != 3:
    print('expected 3!')
    sys.exit(1)

c.close()
print('All tests passed!')
