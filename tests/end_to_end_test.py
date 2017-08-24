import os
from os.path import join,dirname,abspath
import unittest
import datetime
import psycopg2
from pyfrbcatdb import dbase as dbase
from pyfrbcatdb import decode_VOEvent as decode
from pyfrbcatdb import create_VOEvent as create

class end2endtest(unittest.TestCase):
    def setUp(self):
        if 'TRAVIS' in os.environ:
             self.DB_NAME = 'frbcat'
             self.USER_NAME = 'postgres'
             self.DB_HOST = None
             self.DB_PORT = None
             self.USER_PASSWORD = None
             self.connection, self.cursor = dbase.connectToDB(
                 dbName=self.DB_NAME, userName=self.USER_NAME,
                 dbPassword=self.USER_PASSWORD, dbHost=self.DB_HOST,
                 dbPort=self.DB_PORT, dbCursor=psycopg2.extensions.cursor)
        else:
            # TODO: read config file
            self.DB_NAME = 'frbcat'
            self.USER_NAME = 'aa-alert'
            self.DB_HOST = 'localhost'
            self.DB_PORT = None
            self.USER_PASSWORD = 'aa-alert'
            self.connection, self.cursor = dbase.connectToDB(
                dbName=self.DB_NAME, userName=self.USER_NAME,
                dbPassword=self.USER_PASSWORD, dbHost=self.DB_HOST,
                dbPort=self.DB_PORT, dbCursor=psycopg2.extensions.cursor)
        self.test_data = os.path.join(dirname(abspath(__file__)), '..', 'test_data')

    def tearDown(self):
        self.connection.close()

    def get_num_rows_main_tables(self):
        '''
        return the number of rows for the main tables:
            authors, frbs, observations, rop, rmp
        '''
        sql = "select id from authors"
        self.cursor.execute(sql)
        len_authors = len(self.cursor.fetchall())
        sql = "select id from frbs"
        self.cursor.execute(sql)
        len_frbs = len(self.cursor.fetchall())
        sql = "select id from observations"
        self.cursor.execute(sql)
        len_observations = len(self.cursor.fetchall())
        sql = "select id from radio_observations_params"
        self.cursor.execute(sql)
        len_rop = len(self.cursor.fetchall())
        sql = "select id from radio_measured_params"
        self.cursor.execute(sql)
        len_rmp = len(self.cursor.fetchall())
        return (len_authors, len_frbs, len_observations, len_rop, len_rmp)

    def test_01(self):
        '''
        Adding a new event with a new author
        should add one row in authors, frbs, observations, rop, rmp
        detected=True, Verified=True (importance flag higher than threshold)
        '''
        len_before = self.get_num_rows_main_tables()
        decode.decode_VOEvent(os.path.join(self.test_data, 'Detection_unitTest1.xml'),
                              self.DB_NAME, self.DB_HOST, self.DB_PORT,
                              self.USER_NAME, self.USER_PASSWORD)
        len_after = self.get_num_rows_main_tables()
        # assert authors increased by 1
        self.assertEqual(len_before[0], len_after[0]-1)
        # assert frbs increased by 1
        self.assertEqual(len_before[1], len_after[1]-1)
        # assert observations increased by 1
        self.assertEqual(len_before[2], len_after[2]-1)
        # assert rop increased by 1
        self.assertEqual(len_before[3], len_after[3]-1)
        # assert rmp increased by 1
        self.assertEqual(len_before[4], len_after[4]-1)
        # check inserted values in database
        sql = "select authors.ivorn, authors.contact_name, authors.contact_email, frbs.name, frbs.utc, o.telescope, o.detected, o.verified from radio_measured_params rmp join radio_observations_params rop ON rmp.rop_id=rop.id join observations o on rop.obs_id=o.id join frbs on o.frb_id=frbs.id join authors on frbs.author_id=authors.id where voevent_ivorn='ivo://au.csiro.parkes/parkes#FRB1405141714/57953.44444444';"
        values = ('ivo://au.csiro.parkes.superb', 'Emily Petroff',
                  'ebpetroff@gmail.com', 'FRB140514',
                  datetime.datetime(2014, 5, 14, 17, 14, 11), 'PARKES',
                  True, True)  # both detected and verified (importance=1) = True
        self.cursor.execute(sql)
        self.assertTupleEqual(values, self.cursor.fetchone())

    def test_01b(self):
        '''
        Adding a new event with a new author
        should add one row in authors, frbs, observations, rop, rmp
        detected=True, Verified=False (importance flag lower than threshold)
        '''
        len_before = self.get_num_rows_main_tables()
        decode.decode_VOEvent(os.path.join(self.test_data, 'Detection_unitTest2.xml'),
                              self.DB_NAME, self.DB_HOST, self.DB_PORT,
                              self.USER_NAME, self.USER_PASSWORD)
        len_after = self.get_num_rows_main_tables()
        # assert authors increased by 1
        self.assertEqual(len_before[0], len_after[0]-1)
        # assert frbs increased by 1
        self.assertEqual(len_before[1], len_after[1]-1)
        # assert observations increased by 1
        self.assertEqual(len_before[2], len_after[2]-1)
        # assert rop increased by 1
        self.assertEqual(len_before[3], len_after[3]-1)
        # assert rmp increased by 1
        self.assertEqual(len_before[4], len_after[4]-1)
        # check inserted values in database
        sql = "select authors.ivorn, authors.contact_name, authors.contact_email, frbs.name, frbs.utc, o.telescope, o.detected, o.verified from radio_measured_params rmp join radio_observations_params rop ON rmp.rop_id=rop.id join observations o on rop.obs_id=o.id join frbs on o.frb_id=frbs.id join authors on frbs.author_id=authors.id where voevent_ivorn='ivo://nl.astron.apertif/alert#FRB1707201312/57954.55000000';"
        values = ('ivo://nl.astron.apertif.alert', 'Emily Petroff',
                  'ebpetroff@gmail.com', 'FRB170720',
                  datetime.datetime(2014, 5, 14, 17, 14, 11), 'PARKES',
                  True, False)  # both detected and verified (importance=0.85) = True
        self.cursor.execute(sql)
        self.assertTupleEqual(values, self.cursor.fetchone())

    def test_02(self):
        '''
        A confirmation of type supersedes
        of the event in Detection_unitTest1.xml (test_01) should not
        add any rows in authors, frbs, observations, rop, rmp
        '''
        len_before = self.get_num_rows_main_tables()
        decode.decode_VOEvent(os.path.join(self.test_data, 'Confirmation_unitTest1.xml'),
                              self.DB_NAME, self.DB_HOST, self.DB_PORT,
                              self.USER_NAME, self.USER_PASSWORD)
        len_after = self.get_num_rows_main_tables()
        # assert authors remains the same
        self.assertEqual(len_before[0], len_after[0])
        # assert frbs remains the same
        self.assertEqual(len_before[1], len_after[1])
        # assert observations remains the same
        self.assertEqual(len_before[2], len_after[2])
        # assert rop remains the same
        self.assertEqual(len_before[3], len_after[3])
        # assert rmp remains the same
        self.assertEqual(len_before[4], len_after[4])

    def test_02b(self):
        '''
        A confirmation of type supersedes
        of the event in Detection_unitTest1.xml (test_01) should not
        add any rows in authors, frbs, observations, rop, rmp
        '''
        len_before = self.get_num_rows_main_tables()
        decode.decode_VOEvent(os.path.join(self.test_data, 'Confirmation_unitTest2.xml'),
                              self.DB_NAME, self.DB_HOST, self.DB_PORT,
                              self.USER_NAME, self.USER_PASSWORD)
        len_after = self.get_num_rows_main_tables()
        # assert authors remains the same
        self.assertEqual(len_before[0], len_after[0])
        # assert frbs remains the same
        self.assertEqual(len_before[1], len_after[1])
        # assert observations remains the same
        self.assertEqual(len_before[2], len_after[2])
        # assert rop remains the same
        self.assertEqual(len_before[3], len_after[3])
        # assert rmp remains the same
        self.assertEqual(len_before[4], len_after[4])

    def test_03(self):
        '''
        A subsequent event
        of the event in Detection_unitTest2.xml (test_01b)
        with a new author should
        add rows in authors, observations, rop, rmp
        '''
        len_before = self.get_num_rows_main_tables()
        decode.decode_VOEvent(os.path.join(self.test_data, 'Subsequent_unitTest1.xml'),
                              self.DB_NAME, self.DB_HOST, self.DB_PORT,
                              self.USER_NAME, self.USER_PASSWORD)
        len_after = self.get_num_rows_main_tables()
        # assert authors increased by 1
        self.assertEqual(len_before[0], len_after[0]-1)
        # assert frbs remains the same
        self.assertEqual(len_before[1], len_after[1])
        # assert observations increased by 1
        self.assertEqual(len_before[2], len_after[2]-1)
        # assert rop increased by 1
        self.assertEqual(len_before[3], len_after[3]-1)
        # assert rmp increased by 1
        self.assertEqual(len_before[4], len_after[4]-1)

    def test_04(self):
        '''
        Retraction of event
        of the event added by Subsequent_unitTest1.xml
        '''
        len_before = self.get_num_rows_main_tables()
        decode.decode_VOEvent(os.path.join(self.test_data, 'Retraction_unitTest1.xml'),
                              self.DB_NAME, self.DB_HOST, self.DB_PORT,
                              self.USER_NAME, self.USER_PASSWORD)
        len_after = self.get_num_rows_main_tables()
        # assert authors remains the same
        self.assertEqual(len_before[0], len_after[0])
        # assert frbs remains the same
        self.assertEqual(len_before[1], len_after[1])
        # assert observations remains the same
        self.assertEqual(len_before[2], len_after[2])
        # assert rop remains the same
        self.assertEqual(len_before[3], len_after[3])
        # assert rmp remains the same
        self.assertEqual(len_before[4], len_after[4])
        # check inserted values in database
        sql = "select frbs.name, o.detected, o.verified from radio_measured_params rmp join radio_observations_params rop ON rmp.rop_id=rop.id join observations o on rop.obs_id=o.id join frbs on o.frb_id=frbs.id join authors on frbs.author_id=authors.id where voevent_ivorn='ivo://nl.astron.lofar/alert#FRB1707201312/57954.56250000';"
        # both detected and verified should be False for a retracted event
        values = ('FRB170720', False, False)
        self.cursor.execute(sql)
        self.assertTupleEqual(values, self.cursor.fetchone())

    def test_04b(self):
        '''
        Retraction of event
        of the event added by Detection_unitTest2.xml
        '''
        len_before = self.get_num_rows_main_tables()
        decode.decode_VOEvent(os.path.join(self.test_data, 'Retraction_unitTest2.xml'),
                              self.DB_NAME, self.DB_HOST, self.DB_PORT,
                              self.USER_NAME, self.USER_PASSWORD)
        len_after = self.get_num_rows_main_tables()
        # assert authors remains the same
        self.assertEqual(len_before[0], len_after[0])
        # assert frbs remains the same
        self.assertEqual(len_before[1], len_after[1])
        # assert observations remains the same
        self.assertEqual(len_before[2], len_after[2])
        # assert rop remains the same
        self.assertEqual(len_before[3], len_after[3])
        # assert rmp remains the same
        self.assertEqual(len_before[4], len_after[4])
        # check inserted values in database
        sql = "select frbs.name, o.detected, o.verified from radio_measured_params rmp join radio_observations_params rop ON rmp.rop_id=rop.id join observations o on rop.obs_id=o.id join frbs on o.frb_id=frbs.id join authors on frbs.author_id=authors.id where voevent_ivorn='ivo://nl.astron.apertif/alert#FRB1707201312/57954.55000000';"
        # both detected and verified should be False for a retracted event
        values = ('FRB170720', False, False)
        self.cursor.execute(sql)
        self.assertTupleEqual(values, self.cursor.fetchone())

    def test_05(self):
        '''
        Creating VOEvent from database
        '''
        create.create_VOEvent([1], self.DB_NAME, self.DB_HOST, self.DB_PORT,
                              self.USER_NAME, self.USER_PASSWORD)


if __name__ == '__main__':
    unittest.main()
