'''
description:    Decode VOEvent db entry to xml
license:        APACHE 2.0
author:         Ronald van Haren, NLeSC (r.vanharen@esciencecenter.nl)
'''
from pyfrbcatdb import dbase
from pyfrbcatdb.FRBCat import *


def create_VOEvent(frb_ids, dbName, dbHost, dbPort, dbUser, dbPassword):
    '''
    Decode FRBCat entry.

    :param frb_ids: list of ids of FRBs in frbs table to extract
    :param dbName: database name
    :param dbHost: database host
    :param dbPort: database port
    :param dbUser: database user name
    :param dbPassword: database user password
    :type frb_ids: list
    :type dbName: str
    :type dbHost: str, NoneType
    :type dbPort: str, NoneType
    :type dbUser: str, NoneType
    :type dbPassword: str, NoneType

    '''
    # connect to database
    connection, cursor = dbase.connectToDB(dbName,
                                           dbUser,
                                           dbPassword,
                                           dbHost,
                                           dbPort)
    for frb_id in frb_ids:
        FRBCat = FRBCat_create(connection, cursor, frb_id)
        FRBCat.create_VOEvent_from_FRBCat()
