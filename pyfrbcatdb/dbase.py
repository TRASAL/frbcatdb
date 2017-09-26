#!/usr/bin/env python

'''
description:    Common database functionality for pyfrbcatdb
license:        APACHE 2.0
author:         Ronald van Haren, NLeSC (r.vanharen@esciencecenter.nl)
'''
import psycopg2
import psycopg2.extras


def connectToDB(dbName=None, userName=None, dbPassword=None, dbHost=None,
                dbPort=None, dbCursor=psycopg2.extras.DictCursor):
    '''
    Connect to a specified PostgreSQL DB and
    return connection and cursor objects.
    '''
    # Start DB connection
    try:
        connectionString = "dbname='" + dbName + "'"
        if userName is not None and userName != '':
            connectionString += " user='" + userName + "'"
        if dbHost is not None and dbHost != '':
            connectionString += " host='" + dbHost + "'"
        if dbPassword is not None and dbPassword != '':
            connectionString += " password='" + dbPassword + "'"
        if dbPort is not None:
            connectionString += " port='" + str(dbPort) + "'"
        connection = psycopg2.connect(connectionString)
    except Exception:
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
    except psycopg2.DatabaseError:
        connection.rollback()


def extract_from_db_sql(cursor, table, column, row, value):
    '''
    Extract a value from the database
    '''
    sql = "select {} from {} where {}='{}'".format(column, table,
                                                   row, value)
    cursor.execute(sql)
    return cursor.fetchone()
