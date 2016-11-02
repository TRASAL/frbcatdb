import unittest
import datetime
import pymysql.cursors
from pyfrbcatdb import dbase as dbase

class BasicDBTest(unittest.TestCase):
    def setUp(self):
        self.connection, self.cursor = dbase.connectToDB(dbHost='localhost',
                                            dbName='frbcat_test',
                                            userName='travis_pymysql',
                                            dbPassword='password',
                                            dbCursor=pymysql.cursors.Cursor)
        self.tableColumnsDict = {
        'authors': 'id,ivorn,title,logo_url,short_name,contact_name,contact_email,contact_phone,other_information',
        'publications': 'id,type,reference,link,description',
        'frbs': 'id,author_id,name,utc,private' ,
        'frbs_have_publications': 'frb_id,pub_id',
        'frbs_notes': 'id,frb_id,last_modified,author,note',
        'observations': 'id,frb_id,author_id,type,telescope,utc,data_link,detected',
        'observations_have_publications': 'obs_id,pub_id',
        'observations_notes': 'id,obs_id,last_modified,author,note',
        'radio_observations_params': 'id,obs_id,author_id,receiver,backend,beam,raj,decj,gl,gb,pointing_error,FWHM,sampling_time,bandwidth,centre_frequency,npol,channel_bandwidth,bits_per_sample,gain,tsys,ne2001_dm_limit',
        'radio_observations_params_have_publications': 'rop_id,pub_id',
        'radio_observations_params_notes': 'id,rop_id,last_modified,author,note',
        'radio_measured_params': 'id,rop_id,author_id,voevent_ivorn,voevent_xml,dm,dm_error,snr,width,width_error_upper,width_error_lower,flux,flux_prefix,flux_error_upper,flux_error_lower,flux_calibrated,dm_index,dm_index_error,scattering_index,scattering_index_error,scattering_time,scattering_time_error,linear_poln_frac,linear_poln_frac_error,circular_poln_frac,circular_poln_frac_error,spectral_index,spectral_index_error,z_phot,z_phot_error,z_spec,z_spec_error,rank',
        'radio_measured_params_have_publications': 'rmp_id,pub_id',
        'radio_measured_params_notes': 'id,rmp_id,last_modified,author,note',
        'radio_images': 'id,title,caption,image',
        'radio_images_have_radio_measured_params': 'radio_image_id,rmp_id'
        }

        self.tableNumDict = {
        'authors': 1, 'publications': 3, 'frbs': 3 ,
        'frbs_have_publications': 5, 'frbs_notes': 2, 'observations': 4,
        'observations_have_publications': 8, 'observations_notes': 1,
        'radio_observations_params': 4, 'radio_observations_params_have_publications': 8,
        'radio_observations_params_notes': 1, 'radio_measured_params': 4,
        'radio_measured_params_have_publications': 8, 'radio_measured_params_notes': 1,
        'radio_images': 4, 'radio_images_have_radio_measured_params': 8
        }

        self.tableFirstRow = {
        'authors': (1,'ivo://unknown',None,None,None,None,None,None,None),
        'publications': (1,'type 0','Nobody et. no one','http://blah','description!'),
        'frbs': (1,1,'FRB010125',datetime.datetime(2001, 1, 24, 23, 29, 14),0),
        'frbs_have_publications': (1,1),
        'frbs_notes': (1,1,datetime.datetime(2015, 10, 19, 0, 40, 2),'J. Doe','some note'),
        'observations': (1,1,1,'type 1','telescope 1',datetime.datetime(2001, 1, 24, 23, 29, 14),'http://data111/',1),
        'observations_have_publications': (1,1),
        'observations_notes': (1,4,datetime.datetime(2016, 3, 13, 5, 45, 12),'J. Doe','some note'),
        'radio_observations_params': (1,1,1,'receiver 1','backend 1','beam 1','19:06:53','-40:37:14',356.641,-20.0206,11,15,0.125,288,1372.5,2,None,1,0.69,28,110),
        'radio_observations_params_have_publications': (1,1),
        'radio_observations_params_notes': (1,2,datetime.datetime(2016, 3, 13, 5, 45, 12),'J. Doe','some note'),
        'radio_measured_params': (1,1,1,'ivo://unknown','',790,3,17,9.4,0.2,0.2,0.3,'',None,None,0,2,0.01,-4.2,1.2,None,None,None,None,None,None,None,None,None,None,None,None,1),
        'radio_measured_params_have_publications': (1,1),
        'radio_measured_params_notes': (1,3,datetime.datetime(2016, 3, 13, 5, 45, 12),'J. Doe','some note'),
        'radio_images': (1,'Radio Image 1', None, None),
        'radio_images_have_radio_measured_params': (1,1)
        }

    def tearDown(self):
        self.connection.close()

    def test_select_num(self):
        # Test to see if test data is loaded as expected (number of rows per table)
        for table in self.tableNumDict:
            self.assertEqual(self.tableNumDict[table], self.cursor.execute('SELECT * from ' + table))

    def test_select_columns(self):
        # Test to query all columns of all tables
        for table in self.tableColumnsDict:
            self.cursor.execute('select ' + self.tableColumnsDict[table] + ' from ' + table)
            self.assertEqual(len(self.tableColumnsDict[table].split(',')), len(self.cursor.fetchone()))

    def test_select_first_row(self):
        # Test to see if test data is loaded as expected (first row)
        for table in self.tableFirstRow:
            self.cursor.execute('select ' + self.tableColumnsDict[table] + ' from ' + table + ' limit 1')
            self.assertTupleEqual(self.tableFirstRow[table], self.cursor.fetchone())

if __name__ == '__main__':
    unittest.main()
