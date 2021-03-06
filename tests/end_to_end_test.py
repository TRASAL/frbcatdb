import os
from os.path import dirname, abspath
import unittest
import datetime
import psycopg2
from pyfrbcatdb import dbase as dbase
from pyfrbcatdb import decode_VOEvent as decode
from pyfrbcatdb import create_VOEvent as create
from pyfrbcatdb import writeCSV
from pyfrbcatdb import zenodo
import sys


class end2endtest(unittest.TestCase):
    def setUp(self):
        if 'TRAVIS' in os.environ:
            self.dbName = 'frbcat'
            self.dbUser = 'postgres'
            self.dbHost = None
            self.dbPort = None
            self.dbPassword = None
            self.logfile = 'frbcatdb.log'
            self.CSV = 'frbcatdb.csv'
            self.connection, self.cursor = dbase.connectToDB(
                dbName=self.dbName, dbUser=self.dbUser,
                dbPassword=self.dbPassword, dbHost=self.dbHost,
                dbPort=self.dbPort, dbCursor=psycopg2.extensions.cursor)
        else:
            # TODO: read config file
            self.dbName = 'frbcat'
            self.dbUser = 'postgres'
            self.dbHost = 'localhost'
            self.dbPort = None
            self.dbPassword = 'None'
            self.logfile = 'frbcatdb.log'
            self.CSV = 'frbcatdb.csv'
            self.connection, self.cursor = dbase.connectToDB(
                dbName=self.dbName, dbUser=self.dbUser,
                dbPassword=self.dbPassword, dbHost=self.dbHost,
                dbPort=self.dbPort, dbCursor=psycopg2.extensions.cursor)
        self.test_data = os.path.join(dirname(abspath(__file__)), '..',
                                      'test_data')

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
        decode.decode_VOEvent(os.path.join(self.test_data,
                              'Detection_unitTest1.xml'),
                              self.dbName, self.dbHost, self.dbPort,
                              self.dbUser, self.dbPassword, self.logfile)
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
        sql = "select authors.ivorn, authors.contact_name, authors.contact_email, frbs.name, frbs.utc, o.telescope, o.detected, o.verified, rop.beam_semi_major_axis, rop.beam_semi_minor_axis, rop.beam_rotation_angle, rop.sampling_time, rop.bandwidth, rop.centre_frequency, rop.npol, rop.bits_per_sample, rop.gain, rop.tsys, rop.backend, rop.beam, rop.gl, rop.gb, rop.mw_dm_limit, rmp.dm, rmp.dm_error, rmp.width, rmp.snr, rmp.flux, rmp.redshift_inferred, rmp.dispersion_smearing from radio_measured_params rmp join radio_observations_params rop ON rmp.rop_id=rop.id join observations o on rop.obs_id=o.id join frbs on o.frb_id=frbs.id join authors on o.author_id=authors.id where voevent_ivorn='ivo://au.csiro.parkes/parkes#FRB1405141714/57953.44444444';"
        # both detected and verified (importance=1) = True
        values = ('ivo://au.csiro.parkes.superb', 'Emily Petroff',
                  'ebpetroff@gmail.com', 'FRB140514',
                  datetime.datetime(2014, 5, 14, 17, 14, 11, 59000), 'PARKES',
                  True, True,
                  7.5, 7.5, 0, 0.064, 400, 1382, 2, 2, 0.735, 28, 'BPSR', '1',
                  50.8, -54.6, 34.9,
                  563.3, 1.0, 4.096, 16.1, 0.361, 0.44, 1.1)
        self.cursor.execute(sql)
        self.assertTupleEqual(values, self.cursor.fetchone())

    def test_01b(self):
        '''
        Adding a new event with a new author
        should add one row in authors, frbs, observations, rop, rmp
        detected=True, Verified=False (importance flag lower than threshold)
        '''
        len_before = self.get_num_rows_main_tables()
        decode.decode_VOEvent(os.path.join(self.test_data,
                              'Detection_unitTest2.xml'),
                              self.dbName, self.dbHost, self.dbPort,
                              self.dbUser, self.dbPassword, self.logfile)
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
        sql = "select authors.ivorn, authors.contact_name, authors.contact_email, frbs.name, frbs.utc, o.telescope, o.detected, o.verified, rop.beam_semi_major_axis, rop.beam_semi_minor_axis, rop.beam_rotation_angle, rop.sampling_time, rop.bandwidth, rop.centre_frequency, rop.npol, rop.bits_per_sample, rop.gain, rop.tsys, rop.backend, rop.beam, rop.gl, rop.gb, rop.mw_dm_limit, rmp.dm, rmp.dm_error, rmp.width, rmp.snr, rmp.flux, rmp.redshift_inferred, rmp.dispersion_smearing from radio_measured_params rmp join radio_observations_params rop ON rmp.rop_id=rop.id join observations o on rop.obs_id=o.id join frbs on o.frb_id=frbs.id join authors on o.author_id=authors.id where voevent_ivorn='ivo://nl.astron.apertif/alert#FRB1707201312/57954.55000000';"
        # both detected and verified (importance=0.85) = True
        values = ('ivo://nl.astron.apertif.alert', 'Emily Petroff',
                  'ebpetroff@gmail.com', 'FRB170720',
                  datetime.datetime(2014, 5, 14, 17, 14, 11, 59000), 'PARKES',
                  True, False,
                  30.0, 0.41, 15, 0.04096, 300, 1400, 2, 2, 0.8, 1000, 'ARTS',
                  '35', 151.6, 6.65, 156.4,
                  750.0, 1.0, 2.048, 50, 60, 0.5, 0.93)
        self.cursor.execute(sql)
        self.assertTupleEqual(values, self.cursor.fetchone())

    def test_02(self):
        '''
        A confirmation of type supersedes
        of the event in Detection_unitTest1.xml (test_01) should not
        add any rows in authors, frbs, observations, rop, rmp
        '''
        len_before = self.get_num_rows_main_tables()
        decode.decode_VOEvent(os.path.join(self.test_data,
                              'Confirmation_unitTest1.xml'),
                              self.dbName, self.dbHost, self.dbPort,
                              self.dbUser, self.dbPassword, self.logfile)
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
        sql = "select authors.ivorn, authors.contact_name, authors.contact_email, frbs.name, frbs.utc, o.telescope, o.detected, o.verified, rop.beam_semi_major_axis, rop.beam_semi_minor_axis, rop.beam_rotation_angle, rop.sampling_time, rop.bandwidth, rop.centre_frequency, rop.npol, rop.bits_per_sample, rop.gain, rop.tsys, rop.backend, rop.beam, rop.gl, rop.gb, rop.mw_dm_limit, rmp.dm, rmp.dm_error, rmp.width, rmp.snr, rmp.flux, rmp.redshift_inferred, rmp.dispersion_smearing, rmp.scattering, rmp.dm_index, rmp.dm_index_error, rmp.width_error_upper, rmp.width_error_lower, rmp.flux_calibrated, rmp.flux_error_upper, rmp.flux_error_lower, rmp.fluence, rmp.fluence_error_upper, rmp.fluence_error_lower, rmp.linear_poln_frac, rmp.linear_poln_frac_error, rmp.circular_poln_frac, rmp.circular_poln_frac_error from radio_measured_params rmp join radio_observations_params rop ON rmp.rop_id=rop.id join observations o on rop.obs_id=o.id join frbs on o.frb_id=frbs.id join authors on o.author_id=authors.id where voevent_ivorn='ivo://au.csiro.parkes/parkes#FRB1405141714/57953.44444444';"
        # both detected and verified (importance=1) = True
        values = ('ivo://au.csiro.parkes.superb', 'Emily Petroff',
                  'ebpetroff@gmail.com', 'FRB140514',
                  datetime.datetime(2014, 5, 14, 17, 14, 11, 59000), 'PARKES',
                  True, False,
                  7.5, 7.5, 0, 0.064, 338.281, 1352.0, 2, 2, 0.735, 28,
                  'BPSR', '1', 50.8, -54.6, 34.9,
                  562.7, 0.6, 2.80, 16, 0.47, 0.44, 1.1, 5.4, 2.000, 0.004,
                  3.50, 0.7, True, 0.11, 0.08, 1.32, 2.34, 0.50, 0.0, 10.0,
                  21.0, 7.0)
        self.cursor.execute(sql)
        self.assertTupleEqual(values, self.cursor.fetchone())

    def test_02b(self):
        '''
        A confirmation of type supersedes
        of the event in Detection_unitTest1.xml (test_01) should not
        add any rows in authors, frbs, observations, rop, rmp
        '''
        len_before = self.get_num_rows_main_tables()
        decode.decode_VOEvent(os.path.join(self.test_data,
                              'Confirmation_unitTest2.xml'),
                              self.dbName, self.dbHost, self.dbPort,
                              self.dbUser, self.dbPassword, self.logfile)
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
        # same values as test_02 except changing dm_index_error,
        # and adding scattering_timescale, scater_index
        sql = "select authors.ivorn, authors.contact_name, authors.contact_email, frbs.name, frbs.utc, o.telescope, o.detected, o.verified, rop.beam_semi_major_axis, rop.beam_semi_minor_axis, rop.beam_rotation_angle, rop.sampling_time, rop.bandwidth, rop.centre_frequency, rop.npol, rop.bits_per_sample, rop.gain, rop.tsys, rop.backend, rop.beam, rop.gl, rop.gb, rop.mw_dm_limit, rmp.dm, rmp.dm_error, rmp.width, rmp.snr, rmp.flux, rmp.redshift_inferred, rmp.dispersion_smearing, rmp.scattering, rmp.dm_index, rmp.dm_index_error, rmp.width_error_upper, rmp.width_error_lower, rmp.flux_calibrated, rmp.flux_error_upper, rmp.flux_error_lower, rmp.fluence, rmp.fluence_error_upper, rmp.fluence_error_lower, rmp.linear_poln_frac, rmp.linear_poln_frac_error, rmp.circular_poln_frac, rmp.circular_poln_frac_error, rmp.scattering_timescale, rmp.scattering_index from radio_measured_params rmp join radio_observations_params rop ON rmp.rop_id=rop.id join observations o on rop.obs_id=o.id join frbs on o.frb_id=frbs.id join authors on o.author_id=authors.id where voevent_ivorn='ivo://au.csiro.parkes/parkes#FRB1405141714/57953.44444444';"
        # both detected and verified (importance=1) = True
        values = ('ivo://au.csiro.parkes.superb', 'Emily Petroff',
                  'ebpetroff@gmail.com', 'FRB140514',
                  datetime.datetime(2014, 5, 14, 17, 14, 11, 59000), 'PARKES',
                  True, False,
                  7.5, 7.5, 0, 0.064, 338.281, 1352.0, 2, 2, 0.735, 28,
                  'BPSR', '1', 50.8, -54.6, 34.9,
                  562.7, 0.6, 2.80, 16, 0.47, 0.44, 1.1, 5.4, 2.000, 0.005,
                  3.50, 0.7, True, 0.11, 0.08, 1.32, 2.34, 0.50, 0.0, 10.0,
                  21.0, 7.0, 4.00, 0.01)
        self.cursor.execute(sql)
        self.assertTupleEqual(values, self.cursor.fetchone())

    def test_03(self):
        '''
        A subsequent event
        of the event in Detection_unitTest2.xml (test_01b)
        with a new author should
        add rows in authors, observations, rop, rmp
        '''
        len_before = self.get_num_rows_main_tables()
        decode.decode_VOEvent(os.path.join(self.test_data,
                              'Subsequent_unitTest1.xml'),
                              self.dbName, self.dbHost, self.dbPort,
                              self.dbUser, self.dbPassword, self.logfile)
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
        sql = "select authors.ivorn, authors.contact_name, authors.contact_email, frbs.name, frbs.utc, o.utc, o.telescope, o.detected, o.verified, rop.beam_semi_major_axis, rop.beam_semi_minor_axis, rop.beam_rotation_angle, rop.sampling_time, rop.bandwidth, rop.centre_frequency, rop.npol, rop.bits_per_sample, rop.gain, rop.tsys, rop.backend, rop.gl, rop.gb, rmp.dm, rmp.dm_error, rmp.width, rmp.snr, rmp.flux from radio_measured_params rmp join radio_observations_params rop ON rmp.rop_id=rop.id join observations o on rop.obs_id=o.id join frbs on o.frb_id=frbs.id join authors on o.author_id=authors.id where voevent_ivorn='ivo://nl.astron.lofar/alert#FRB1707201312/57954.56250000';"
        # both detected and verified (importance=0.85) = True
        values = ('ivo://nl.astron.lofar.alert', 'Emily Petroff',
                  'ebpetroff@gmail.com', 'FRB170720',
                  datetime.datetime(2014, 5, 14, 17, 14, 11, 59000),
                  datetime.datetime(2014, 5, 14, 17, 14, 13, 59000), 'PARKES',
                  True, False,
                  0.5, 0.5, 0, 1.0, 32, 115, 2, 2, 8.8, 1000, None,
                  151.6, 6.65, 750, 5, 10.0, 10, 1.5)
        self.cursor.execute(sql)
        self.assertTupleEqual(values, self.cursor.fetchone())

    def test_04(self):
        '''
        Retraction of event
        of the event added by Subsequent_unitTest1.xml
        '''
        len_before = self.get_num_rows_main_tables()
        decode.decode_VOEvent(os.path.join(self.test_data,
                              'Retraction_unitTest1.xml'),
                              self.dbName, self.dbHost, self.dbPort,
                              self.dbUser, self.dbPassword, self.logfile)
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
        sql = "select frbs.name, o.detected, o.verified from radio_measured_params rmp join radio_observations_params rop ON rmp.rop_id=rop.id join observations o on rop.obs_id=o.id join frbs on o.frb_id=frbs.id join authors on o.author_id=authors.id where voevent_ivorn='ivo://nl.astron.lofar/alert#FRB1707201312/57954.56250000';"
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
        decode.decode_VOEvent(os.path.join(self.test_data,
                              'Retraction_unitTest2.xml'),
                              self.dbName, self.dbHost, self.dbPort,
                              self.dbUser, self.dbPassword, self.logfile)
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
        sql = "select frbs.name, o.detected, o.verified from radio_measured_params rmp join radio_observations_params rop ON rmp.rop_id=rop.id join observations o on rop.obs_id=o.id join frbs on o.frb_id=frbs.id join authors on o.author_id=authors.id where voevent_ivorn='ivo://nl.astron.apertif/alert#FRB1707201312/57954.55000000';"
        # both detected and verified should be False for a retracted event
        values = ('FRB170720', False, False)
        self.cursor.execute(sql)
        self.assertTupleEqual(values, self.cursor.fetchone())

    def test_05(self):
        '''
        Adding a new event with an existing author
        should add one row in authors, frbs, observations, rop, rmp
        detected=True, Verified=True (importance flag higher than threshold)
        '''
        len_before = self.get_num_rows_main_tables()
        decode.decode_VOEvent(os.path.join(self.test_data,
                              'Notes_unitTest1.xml'),
                              self.dbName, self.dbHost, self.dbPort,
                              self.dbUser, self.dbPassword, self.logfile)
        len_after = self.get_num_rows_main_tables()
        # assert authors increased by 1
        self.assertEqual(len_before[0], len_after[0])
        # assert frbs increased by 1
        self.assertEqual(len_before[1], len_after[1]-1)
        # assert observations increased by 1
        self.assertEqual(len_before[2], len_after[2]-1)
        # assert rop increased by 1
        self.assertEqual(len_before[3], len_after[3]-1)
        # assert rmp increased by 1
        self.assertEqual(len_before[4], len_after[4]-1)
        # extract rop.id and rmp.id from database to
        # allow for extraction of notes
        sql = "select rop.id, rmp.id from radio_measured_params rmp join radio_observations_params rop ON rmp.rop_id=rop.id join observations o on rop.obs_id=o.id join frbs on o.frb_id=frbs.id join authors on o.author_id=authors.id where voevent_ivorn='ivo://au.csiro.parkes/parkes#FRB170831/57996.50000000';"
        self.cursor.execute(sql)
        (rop_id, rmp_id) = self.cursor.fetchone()
        # extract radio_observations_params_notes
        sql = "select last_modified, author, note from radio_observations_params_notes where rop_id={}".format(rop_id)
        self.cursor.execute(sql)
        values = (datetime.datetime(2017, 8, 31, 12, 00, 00), 'Emily Petroff',
                  '[beam] Detection beam number if backend is a multi beam receiver')
        self.assertTupleEqual(values, self.cursor.fetchone())
        # extract radio_measured_params_notes
        sql = "select last_modified, author, note from radio_measured_params_notes where rmp_id={}".format(rmp_id)
        self.cursor.execute(sql)
        values = [(datetime.datetime(2017, 8, 31, 12, 0), 'Emily Petroff', '[scattering] Measured scattering.'), (datetime.datetime(2017, 8, 31, 12, 0), 'Emily Petroff', '[redshift_inferred] Note on inferred redshift.'), (datetime.datetime(2017, 8, 31, 12, 0), 'Emily Petroff', '[redshift_host] Note on host redshift.')]
        self.assertEqual(values, self.cursor.fetchall())

    def test_06(self):
        '''
        Create csv from database
        '''
        writeCSV.writeCSV(self.CSV,  self.dbName, self.dbHost, self.dbPort,
                          self.dbUser, self.dbPassword, self.logfile)

    def test_07(self):
        '''
        Creating VOEvent from database
        '''
        create.create_VOEvent([1], self.dbName, self.dbHost, self.dbPort,
                              self.dbUser, self.dbPassword)

    def test_08(self):
        '''
        Upload csv to Zenodo sandbox environment
        '''
        if 'TRAVIS' in os.environ:
            # only perform the Zenodo test for 1 python version on TRAVIS
            # as simultaneous uploads fail
            if (sys.version_info.major==3 and sys.version_info.minor==6):
                zenodoSandbox = os.environ.get('zenodoSandbox')
                zenodo.zenodo(zenodoSandbox, self.CSV, self.logfile, sandbox=True)
        else:
            zenodoSandbox = os.environ.get('zenodoSandbox')
            zenodo.zenodo(zenodoSandbox, self.CSV, self.logfile, sandbox=True)

if __name__ == '__main__':
    unittest.main()
