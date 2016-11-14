#!/usr/bin/env python

'''
description:    Common database functionality for pyfrbcatdb
license:        APACHE 2.0
author:         Ronald van Haren, NLeSC (r.vanharen@esciencecenter.nl)
'''
import psycopg2
import psycopg2.extras
from pyfrbcatdb import config

def connectToDB(dbName=config.DB_NAME, userName=config.USER_NAME, dbPassword=config.USER_PASSWORD, dbHost=config.DB_HOST,
                dbPort=config.DB_PORT, dbCursor=psycopg2.extras.DictCursor):
    '''
    Connect to a specified PostgreSQL DB and return connection and cursor objects.
    '''
    # Start DB connection
    try:
        connectionString = "dbname='" + dbName + "'"
        if userName != None and userName != '':
            connectionString += " user='" + userName + "'"
        if dbHost != None and dbHost != '':
            connectionString += " host='" + dbHost + "'"
        if dbPassword != None and dbPassword != '':
            connectionString += " password='" + dbPassword + "'"
        if dbPort != None:
            connectionString += " port='" + str(dbPort) + "'"
        connection  = psycopg2.connect(connectionString)
    except:
        raise
    # if the connection succeeded get a cursor
    cursor = connection.cursor(cursor_factory=dbCursor)
    return connection, cursor


def closeDBConnection(connection, cursor):
    '''
    Closes a connection to a DB given the connection and cursor objects
    '''
    cursor.close()
    connection.close()
    # msg = 'Connection to the DB is closed.'
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
