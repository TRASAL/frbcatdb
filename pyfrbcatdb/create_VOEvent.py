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
    Decode FRBCat entry
    '''
    # load mapping VOEvent -> FRBCat
    # connect to database
    # TODO: add connection details
    connection, cursor = dbase.connectToDB(DB_NAME, USER_NAME,
                                           USER_PASSWORD, DB_HOST,
                                           DB_PORT)

    for frb_id in frb_ids:
        FRBCat = FRBCat_create(connection, cursor, frb_id)
        FRBCat.create_VOEvent_from_FRBCat()
