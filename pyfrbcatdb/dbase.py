#!/usr/bin/env python

'''
description:    Common database functionality for pyfrbcatdb
license:        APACHE 2.0
author:         Ronald van Haren, NLeSC (r.vanharen@esciencecenter.nl)
'''
import psycopg2
import psycopg2.extras


def connectToDB(dbName=None, dbUser=None, dbPassword=None, dbHost=None,
                dbPort=None, dbCursor=psycopg2.extras.DictCursor):
    '''
    Connect to a specified PostgreSQL DB and
    return connection and cursor objects.

    :param dbName: database name
    :param dbHost: database host
    :param dbPort: database port
    :param dbUser: database user name
    :param dbPassword: database user password
    :type dbName: str
    :type dbHost: str, NoneType
    :type dbPort: str, NoneType
    :type dbUser: str, NoneType
    :type dbPassword: str, NoneType
    :returns: connection, cursor
    :rtype: psycopg2.extensions.connection,
        psycopg2.extras.DictCursor
    '''
    # Start DB connection
    try:
        connectionString = "dbname='" + dbName + "'"
        if (dbUser and dbUser is not '='):
            connectionString += " user='" + dbUser + "'"
        if (dbHost and dbHost is not '='):
            connectionString += " host='" + dbHost + "'"
        if (dbPassword and dbPassword is not '='):
            connectionString += " password='" + dbPassword + "'"
        if (dbPort and dbPort is not '='):
            connectionString += " port='" + str(dbPort) + "'"
        connection = psycopg2.connect(connectionString)
    except Exception:
        raise
    # if the connection succeeded get a cursor
    cursor = connection.cursor(cursor_factory=dbCursor)
    return connection, cursor


def closeDBConnection(connection, cursor):
    '''
    Closes a connection to a DB given the connection and cursor objects.

    :param connection: database connection
    :param cursor: database cursor object
    :type connection: psycopg2.extensions.connection
    :type cursor: psycopg2.extras.DictCursor
    '''
    cursor.close()
    connection.close()
    return


def commitToDB(connection, cursor):
    '''
    Commit changes to database, rollback in case of errors.

    :param connection: database connection
    :param cursor: database cursor object
    :type connection: psycopg2.extensions.connection
    :type cursor: psycopg2.extras.DictCursor
    '''
    try:
        connection.commit()
    except psycopg2.DatabaseError:
        connection.rollback()


def extract_from_db_sql(cursor, table, column, col, value):
    '''
    Extract a value from the database.

    :param cursor: database cursor object
    :param table: db table name
    :param column: db table column name
    :param col: db table column name
    :param value: value of db table column name to match
    :type cursor: psycopg2.extras.DictCursor
    :type table: str
    :type column: str
    :type col: str
    :type value: str
    '''
    sql = "select {} from {} where {}='{}'".format(column, table,
                                                   col, value)
    cursor.execute(sql)
    return cursor.fetchone()
