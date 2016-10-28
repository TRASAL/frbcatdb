#!/usr/bin/env python

'''
description:    Common database functionality for pyAccess
license:        APACHE 2.0
author:         Ronald van Haren, NLeSC (r.vanharen@esciencecenter.nl)
'''

import pymysql.cursors


def connectToDB(dbName=None, userName=None, dbPassword=None, dbHost=None,
                dbPort=None):
    '''
    Connect to a specified MySQL DB and return connection and cursor objects.
    '''
    # Start DB connection
    try:
        connection = pymysql.connect(host=dbHost,
                                     port=dbPort,
                                     user=userName,
                                     password=dbPassword,
                                     db=dbName,
                                     cursorclass=pymysql.cursors.DictCursor)
    except Exception as E:
        err_msg = 'Unable to connect to {} DB.'.format(dbName)
        # logging.error((err_msg, "; %s: %s" % (E.__class__.__name__, E)))
        raise
    msg = 'Successful connected to {} DB.'.format(dbName)
    # logging.debug(msg)
    # if the connection succeeded get a cursor
    cursor = connection.cursor()
    return connection, cursor


def closeDBConnection(connection, cursor):
    '''
    Closes a connection to a DB given the connection and cursor objects
    '''
    cursor.close()
    connection.close()
    msg = 'Connection to the DB is closed.'
    # logging.debug(msg)
    return


def commitToDB(connection, cursor):
    '''
    Commit changes to database, rollback in case of errors
    '''
    try:
        connection.commit()
    except:
        connection.rollback()


def extract_from_db_sql(cursor, table, column, row, value):
    '''
    Extract a value from the database
    '''
    sql = "select {} from {} where {}='{}'".format(column, table,
                                                   row, value)
    cursor.execute(sql)
    return cursor.fetchone()
