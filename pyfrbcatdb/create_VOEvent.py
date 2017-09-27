'''
description:    Decode VOEvent db entry to xml
license:        APACHE 2.0
author:         Ronald van Haren, NLeSC (r.vanharen@esciencecenter.nl)
'''
from pyfrbcatdb import dbase
from pyfrbcatdb.FRBCat import *


def create_VOEvent(frb_ids, DB_NAME, DB_HOST, DB_PORT, USER_NAME,
                   USER_PASSWORD):
    '''
    Decode FRBCat entry.

    :param frb_ids: list of ids of FRBs in frbs table to extract
    :param DB_NAME: database name
    :param DB_HOST: database host
    :param DB_PORT: database port
    :param USER_NAME: database user name
    :param USER_PASSWORD: database user password
    :type frb_ids: list
    :type DB_NAME: str
    :type DB_HOST: str, NoneType
    :type DB_PORT: str, NoneType
    :type USER_NAME: str, NoneType
    :type USER_PASSWORD: str, NoneType

    '''
    # connect to database
    connection, cursor = dbase.connectToDB(DB_NAME,
                                           USER_NAME,
                                           USER_PASSWORD,
                                           DB_HOST,
                                           DB_PORT)
    for frb_id in frb_ids:
        FRBCat = FRBCat_create(connection, cursor, frb_id)
        FRBCat.create_VOEvent_from_FRBCat()
