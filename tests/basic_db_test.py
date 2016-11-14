import os
import unittest
import datetime
import psycopg2
from pyfrbcatdb import dbase as dbase

class BasicDBTest(unittest.TestCase):
    def setUp(self):
        if 'TRAVIS' in os.environ:
            self.connection, self.cursor = dbase.connectToDB(dbName='frbcat', userName='postgres', dbPassword=None, dbHost=None,dbPort=None, dbCursor=psycopg2.extensions.cursor)
        else:
            self.connection, self.cursor = dbase.connectToDB(dbName='frbcat', dbCursor=psycopg2.extensions.cursor)
        self.tableColumnsDict = {
        'authors': 'id,ivorn,title,logo_url,short_name,contact_name,contact_email,contact_phone,other_information',
        'publications': 'id,type,reference,link,description',
        'frbs': 'id,author_id,name,utc,private' ,
        'frbs_have_publications': 'frb_id,pub_id',
        'frbs_notes': 'id,frb_id,last_modified,author,note',
        'observations': 'id,frb_id,author_id,type,telescope,utc,data_link,detected',
        'observations_have_publications': 'obs_id,pub_id',
        'observations_notes': 'id,obs_id,last_modified,author,note',
        'radio_observations_params': 'id,obs_id,author_id,settings_id,receiver,backend,beam,raj,decj,gl,gb,pointing_error,FWHM,sampling_time,bandwidth,centre_frequency,npol,channel_bandwidth,bits_per_sample,gain,tsys,ne2001_dm_limit',
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
        'radio_observations_params': (1,1,1,'settings1','receiver 1','backend 1','beam 1','19:06:53','-40:37:14',356.641,-20.0206,11,15,0.125,288,1372.5,2,None,1,0.69,28,110),
        'radio_observations_params_have_publications': (1,1),
        'radio_observations_params_notes': (1,2,datetime.datetime(2016, 3, 13, 5, 45, 12),'J. Doe','some note'),
        'radio_measured_params': (1,1,1,'ivo://unknown:frb1','',790,3,17,9.4,0.2,0.2,0.3,'',None,None,0,2,0.01,-4.2,1.2,None,None,None,None,None,None,None,None,None,None,None,None,1),
        'radio_measured_params_have_publications': (1,1),
        'radio_measured_params_notes': (1,3,datetime.datetime(2016, 3, 13, 5, 45, 12),'J. Doe','some note'),
        'radio_images': (1,'Radio Image 1', None, None),
        'radio_images_have_radio_measured_params': (1,1)
        }

    def tearDown(self):
        self.connection.close()

    def test_01_select_num(self):
        # Test to see if test data is loaded as expected (number of rows per table)
        for table in self.tableNumDict:
            self.cursor.execute('SELECT * from ' + table)
            self.assertEqual(self.tableNumDict[table], len(self.cursor.fetchall()))

    def test_02_select_columns(self):
        # Test to select all columns of all tables
        for table in self.tableColumnsDict:
            self.cursor.execute('select ' + self.tableColumnsDict[table] + ' from ' + table)
            self.assertEqual(len(self.tableColumnsDict[table].split(',')), len(self.cursor.fetchone()))

    def test_03_select_first_row(self):
        # Test to see if test data is loaded as expected (first row)
        for table in self.tableFirstRow:
            self.cursor.execute('select ' + self.tableColumnsDict[table] + ' from ' + table + ' limit 1')
            self.assertTupleEqual(self.tableFirstRow[table], self.cursor.fetchone())

    def test_04_join_main(self):
        # Test join authors and frbs
        self.cursor.execute('select f.name,a.ivorn from frbs f join authors a on (f.author_id = a.id)')
        self.assertEqual(3, len(self.cursor.fetchall()))

        # Test join frbs and observations
        self.cursor.execute('select f.name,o.telescope,o.utc from frbs f join observations o on (f.id = o.frb_id)')
        self.assertEqual(4, len(self.cursor.fetchall()))

        # Test join observations and radio_observations_params
        self.cursor.execute('select o.telescope,o.utc,rop.settings_id,rop.raj,rop.decj from observations o join radio_observations_params rop on (o.id = rop.obs_id)')
        self.assertEqual(4, len(self.cursor.fetchall()))

        # Test join radio_observations_params and radio_measured_params
        self.cursor.execute('select rop.settings_id,rop.raj,rop.decj,rmp.voevent_ivorn from radio_observations_params rop join radio_measured_params rmp on (rop.id = rmp.rop_id)')
        self.assertEqual(4,  len(self.cursor.fetchall()))

        # Test all main tables (frbs, observations, radio_observations_params and radio_measured_params)
        self.cursor.execute('select f.name,o.telescope,o.utc,rop.settings_id,rop.raj,rop.decj,rmp.voevent_ivorn from frbs f join observations o on (f.id = o.frb_id) join radio_observations_params rop on (o.id = rop.obs_id) join radio_measured_params rmp on (rop.id = rmp.rop_id)')
        self.assertEqual(4,  len(self.cursor.fetchall()))

    def test_05_join_secondary(self):
        self.cursor.execute('select rmp.voevent_ivorn,ri.title from radio_measured_params rmp join radio_images_have_radio_measured_params rihrmp on (rmp.id = rihrmp.rmp_id) join radio_images ri on (rihrmp.radio_image_id = ri.id)')
        self.assertEqual(8, len(self.cursor.fetchall()))

        self.cursor.execute('select f.name,fn.note from frbs f join frbs_notes fn on (f.id = fn.frb_id)')
        self.assertEqual(2, len(self.cursor.fetchall()))

        self.cursor.execute('select o.telescope,o.utc,ont.note from observations o join observations_notes ont on (o.id = ont.obs_id)')
        self.assertEqual(1, len(self.cursor.fetchall()))

        self.cursor.execute('select rop.settings_id,rop.raj,rop.decj,ropn.note from radio_observations_params rop join radio_observations_params_notes ropn on (rop.id = ropn.rop_id)')
        self.assertEqual(1, len(self.cursor.fetchall()))

        self.cursor.execute('select rmp.voevent_ivorn,rmpn.note from radio_measured_params rmp join radio_measured_params_notes rmpn on (rmp.id = rmpn.rmp_id)')
        self.assertEqual(1, len(self.cursor.fetchall()))

        self.cursor.execute('select f.name,p.reference from frbs f join frbs_have_publications fhp on (f.id = fhp.frb_id) join publications p on (fhp.pub_id = p.id)')
        self.assertEqual(5, len(self.cursor.fetchall()))

        self.cursor.execute('select o.telescope,o.utc,p.reference from observations o join observations_have_publications ohp on (o.id = ohp.obs_id) join publications p on (ohp.pub_id = p.id)')
        self.assertEqual(8, len(self.cursor.fetchall()))

        self.cursor.execute('select rop.settings_id,rop.raj,rop.decj,p.reference from radio_observations_params rop join radio_observations_params_have_publications rophp on (rop.id = rophp.rop_id) join publications p on (rophp.pub_id = p.id)')
        self.assertEqual(8, len(self.cursor.fetchall()))

        self.cursor.execute('select rmp.voevent_ivorn,p.reference from radio_measured_params rmp join radio_measured_params_have_publications rmphp on (rmp.id = rmphp.rmp_id) join publications p on (rmphp.pub_id = p.id)')
        self.assertEqual(8, len(self.cursor.fetchall()))

    def test_06_insert_delete_main(self):
        self.cursor.execute("INSERT INTO authors (ivorn) VALUES (%s)", ('ivo://unknown2',))
        self.connection.commit()
        self.cursor.execute("DELETE FROM authors WHERE ivorn = %s", ('ivo://unknown2',))
        self.connection.commit()

        self.cursor.execute("INSERT INTO frbs (author_id,name,utc) VALUES (%s,%s,%s)", (1,"NEW FRB",datetime.datetime(2016, 10, 30, 0, 0, 1)))
        self.connection.commit()
        self.cursor.execute("DELETE FROM frbs WHERE name = %s", ("NEW FRB",))
        self.connection.commit()

        self.cursor.execute("INSERT INTO observations (frb_id,author_id,telescope,utc) VALUES (%s,%s,%s,%s)", (1,1,'eye',datetime.datetime(2016, 10, 30, 0, 0, 1)))
        self.connection.commit()
        self.cursor.execute("DELETE FROM observations WHERE frb_id = %s AND author_id = %s AND telescope = %s AND utc = %s", (1,1,'eye',datetime.datetime(2016, 10, 30, 0, 0, 1)))
        self.connection.commit()

        self.cursor.execute("INSERT INTO radio_observations_params (obs_id,author_id,settings_id,raj,decj) VALUES (%s,%s,%s,%s,%s)", (1,1,'mycustomsettings','00:00:00','00:00:00'))
        self.connection.commit()
        self.cursor.execute("DELETE FROM radio_observations_params WHERE obs_id = %s AND author_id = %s AND settings_id = %s AND raj = %s AND decj = %s", (1,1,'mycustomsettings','00:00:00','00:00:00'))
        self.connection.commit()

        self.cursor.execute("INSERT INTO radio_measured_params (rop_id,author_id,voevent_ivorn,voevent_xml,dm,snr,width) VALUES (%s,%s,%s,%s,%s,%s,%s)", (1,1,'ivo://unknown_new','',0,0,0))
        self.connection.commit()
        self.cursor.execute("DELETE FROM radio_measured_params WHERE voevent_ivorn = %s", ('ivo://unknown_new',))
        self.connection.commit()

    def test_07_insert_check_unique_main(self):
        # Test uniqueness of authors: ivorn must be unique
        self.assertRaises(psycopg2.IntegrityError, self.cursor.execute, "INSERT INTO authors (ivorn) VALUES (%s)", ('ivo://unknown',))
        self.connection.rollback()
        # Test uniquess of frb: name must be unique
        self.assertRaises(psycopg2.IntegrityError, self.cursor.execute, "INSERT INTO frbs (author_id,name,utc) VALUES (%s,%s,%s)", (1,"FRB010125",datetime.datetime(2016, 10, 30, 0, 0, 1)))
        self.connection.rollback()
        # Test uniquess of observation: frb_id,telescope,utc must be unique
        self.assertRaises(psycopg2.IntegrityError, self.cursor.execute, "INSERT INTO observations (frb_id,author_id,telescope,utc) VALUES (%s,%s,%s,%s)", (1,1,'telescope 1',datetime.datetime(2001, 1, 24, 23, 29, 14)))
        self.connection.rollback()
        # Test uniquess of rop: obs_id,settings_id must be unique
        self.assertRaises(psycopg2.IntegrityError, self.cursor.execute, "INSERT INTO radio_observations_params (obs_id,author_id,settings_id,raj,decj) VALUES (%s,%s,%s,%s,%s)", (1,1,'settings1','19:06:53','-40:37:14'))
        self.connection.rollback()
        # Test uniquess of rmp: voevent_ivorn must be unique
        self.assertRaises(psycopg2.IntegrityError, self.cursor.execute, "INSERT INTO radio_measured_params (rop_id,author_id,voevent_ivorn,voevent_xml,dm,snr,width) VALUES (%s,%s,%s,%s,%s,%s,%s)", (1,1,'ivo://unknown:frb4','',0,0,0))
        self.connection.rollback()

if __name__ == '__main__':
    unittest.main()
