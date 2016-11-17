'''
description:    FRBCat functionality for pyfrbcatdb
license:        APACHE 2.0
author:         Ronald van Haren, NLeSC (r.vanharen@esciencecenter.nl)
'''
import pandas as pd
from pyfrbcatdb import dbase as dbase
from pyfrbcatdb import utils as utils
import os
import sys
from numpy import append as npappend
from numpy import array as nparray
from numpy import where as npwhere
from numpy import ravel as npravel
import voeventparse as vp
import datetime
import re
import psycopg2
import lxml

class FRBCat_remove:
    def __init__(self, connection, cursor, mapping, event_type):
        self.connection = connection
        self.cursor = cursor
        self.ivorn = (mapping[mapping['FRBCAT COLUMN']=='voevent_ivorn']
                     )['value'].values[0]
        self.event_type = event_type
        
    def remove_entry(self):
        '''
        Remove entry from FRBCat
        '''
        cont = self.remove_from_radio_measured_params()
        if cont:
            cont = self.remove_from_radio_observations_params()
        if cont:
            cont = self.remove_from_observations()
        if cont:
            self.remove_from_frbs()
        self.remove_from_publications()
        self.remove_from_authors()
        dbase.commitToDB(self.connection, self.cursor)
        dbase.closeDBConnection(self.connection, self.cursor)

    def remove_from_publications(self):
        pass

    def remove_from_authors(self):
        pass

    def remove_from_frbs(self):
        # check if there are more rops for the selected obs_id
        sql = """select id as obs_id from observations
                 where frb_id='{}'""".format(self.frb_id)
        self.cursor.execute(sql)
        if self.cursor.fetchone():  # is not None
            # we don't want to delete obs_id from observations
            # as well as entries from upstream tables
            return False
        else:
            # delete from frbs_notes
            sql = """delete from frbs_notes
                     where frb_id='{}'""".format(self.frb_id)
            self.cursor.execute(sql)
            # select pub_ids from frbs_have_publications
            sql = """select pub_id from frbs_have_publications
                     where frb_id='{}'""".format(self.frb_id)
            self.cursor.execute(sql)
            self.pub_ids_frbs = self.cursor.fetchall()
            # delete entry from frbs_have_publications
            sql = """delete from frbs_have_publications
                     where frb_id='{}'""".format(self.frb_id)
            self.cursor.execute(sql)
            # select author_id from frbs
            sql = """select author_id from frbs
                     where id='{}'""".format(self.frb_id)
            self.cursor.execute(sql)
            self.author_id_frbs = self.cursor.fetchone()
            # delete entry from frbs
            sql = """delete from frbs
                     where id='{}'""".format(self.frb_id)
            self.cursor.execute(sql)
            return True
        
    def remove_from_observations(self):
        # check if there are more rops for the selected obs_id
        sql = """select id as rop_id from radio_observations_params
                 where obs_id='{}'""".format(self.obs_id)
        self.cursor.execute(sql)
        if self.cursor.fetchone():  # is not None
            # we don't want to delete obs_id from observations
            # as well as entries from upstream tables
            return False
        else:
            # delete from observations add_frbs_notes
            sql = """delete from observations_notes
                     where obs_id='{}'""".format(self.obs_id)
            self.cursor.execute(sql)
            # select pub_ids from observations_have_publications
            sql = """select pub_id from observations_have_publications
                     where obs_id='{}'""".format(self.obs_id)
            self.cursor.execute(sql)
            self.pub_ids_obs = self.cursor.fetchall()
            # delete entry from observations_have_publications
            sql = """delete from observations_have_publications
                     where obs_id='{}'""".format(self.obs_id)
            self.cursor.execute(sql)
            # select frb_id, author_id from observations
            sql = """select frb_id, author_id from observations
                     where id='{}'""".format(self.obs_id)
            self.cursor.execute(sql)
            sql_exec = self.cursor.fetchone()
            self.frb_id = sql_exec['frb_id']
            self.author_id_obs = sql_exec['author_id']
            # delete entry from observations
            sql = """delete from observations
                     where id='{}'""".format(self.obs_id)
            self.cursor.execute(sql)
            return True
    
    def remove_from_radio_observations_params(self):
        # check if there are more rmps for the selected rop_id
        sql = """select id as rmp_id from radio_measured_params
                 where rop_id='{}'""".format(self.rop_id)
        self.cursor.execute(sql)
        if self.cursor.fetchone():  # is not None
            # we don't want to delete rop_id from radio_observation_params
            # as well as entries from upstream tables
            return False
        else:
            # delete from radio_observations_params_notes
            sql = """delete from radio_observations_params_notes
                     where rop_id='{}'""".format(self.rop_id)
            self.cursor.execute(sql)
            # select pub_ids from rop_have_publications
            sql = """select pub_id
                     from radio_observations_params_have_publications
                     where rop_id='{}'""".format(self.rop_id)
            self.cursor.execute(sql)
            self.pub_ids_rop = self.cursor.fetchall()
            # delete entry from rop_have_publications
            sql = """delete from radio_observations_params_have_publications
                     where rop_id='{}'""".format(self.rop_id)
            self.cursor.execute(sql)             
            # select obs_id, author_id from rop
            sql = """select obs_id, author_id from radio_observations_params
                     where id='{}'""".format(self.rop_id)
            self.cursor.execute(sql)
            sql_exec = self.cursor.fetchone()
            self.obs_id = sql_exec['obs_id']
            self.author_id = sql_exec['author_id']
            # delete entry from radio_observations_params
            sql = """delete from radio_observations_params
                     where id='{}'""".format(self.rop_id)
            self.cursor.execute(sql)
            return True

    def remove_from_radio_measured_params(self):
        sql = """select rop_id,id as rmp_id from radio_measured_params
                 where voevent_ivorn='{}'""".format(self.ivorn)
        self.cursor.execute(sql)
        sql_exec = self.cursor.fetchone()
        if sql_exec:  # there is an entry to remove
            self.rmp_id = sql_exec['rmp_id']
            self.rop_id = sql_exec['rop_id']
            # delete from radio_measured_params_notes
            sql = """delete from radio_measured_params_notes
                    where rmp_id='{}'""".format(self.rmp_id)
            self.cursor.execute(sql)
            # get all radio_images for the selected rmp_id
            sql = """select radio_image_id
                    from radio_images_have_radio_measured_params
                    where rmp_id='{}'""".format(self.rmp_id)
            self.cursor.execute(sql)
            # delete all radio_images for the selected rmp_id
            for radio_image_id in self.cursor:
                sql = """delete from radio_images
                        where id='{}'""".format(radio_image_id)
                self.cursor.execute(sql)
            # delete entry from radio_images_have_radio_measured_params
            sql = """delete from radio_images_have_radio_measured_params
                    where rmp_id='{}'""".format(self.rmp_id)
            self.cursor.execute(sql)
            # select all publication ids for the selected rmp_id
            sql = """select pub_id
                    from radio_measured_params_have_publications
                    where rmp_id='{}'""".format(self.rmp_id)
            self.cursor.execute(sql)
            self.pub_ids_rmp = self.cursor.fetchall()
            # delete entry from rmp_have_publications
            sql = """delete from radio_measured_params_have_publications
                    where rmp_id='{}'""".format(self.rmp_id)
            self.cursor.execute(sql)
            # delete all publications for the selected rmp_id
            #for pub_id in self.cursor:
            #    sql = """delete from publications where id
            # delete entry from radio_observations_params
            sql = """delete from radio_measured_params
                    where voevent_ivorn='{}'""".format(self.ivorn)
            self.cursor.execute(sql)
            return True
        else:
            # no entry found in database
            return False

class FRBCat_add:
    def __init__(self, connection, cursor, mapping, event_type):
        self.connection = connection
        self.cursor = cursor
        self.mapping = mapping
        self.event_type = event_type
        
    def check_author_exists(self, ivorn):
        '''
        Check if author already exists in Fdatabase
        if author is found, set self.author_id
        '''
        # check if the author ivorn is already in the database
        author_id = dbase.extract_from_db_sql(self.cursor, 'authors', 'id',
                                              'ivorn', ivorn)
        if not author_id:  # did not find the author ivorn
            return False
        else:  # set self.author_id to the one in the database
            self.author_id = author_id['id']
            return True

    def check_event_exists(self, ivorn):
        '''
        Check if event ivorn already exists in database
        if event is found, set self.event_id
        '''
        # check if the event ivorn is already in the database
        event_id = dbase.extract_from_db_sql(
            self.cursor, 'radio_measured_params', 'id', 'voevent_ivorn', ivorn)
        if not event_id:  # did not find the event ivorn
            return False
        else:  # set self.event_id to the id of the ivorn in the database
            self.event_id = event_id['id']
            return True

    def add_authors(self, table, rows, value):
        '''
        Add author to the database if the ivorn is not in the authors table
        '''
        # check if author already exists in database
        # TODO: try/except
        ivorn = value[npwhere(rows == 'ivorn')][0]
        author_exists = self.check_author_exists(ivorn)
        # add author to database if author does not yet exist in db
        if not author_exists:
            self.author_id = self.insert_into_database(table, rows, value)

    def add_frbs(self, table, rows, value):
        '''
        Add event to the frbs table
        '''
        rows = npappend(rows, 'author_id')
        value = npappend(value, self.author_id)
        self.frb_id = self.insert_into_database(table, rows, value)

    def add_frbs_notes(self, table, rows, value):
        '''
        Add event to the frbs_notes table
        '''
        rows = npappend(rows, ('frb_id'))
        value = npappend(value, (self.frb_id))
        self.insert_into_database(table, rows, value)

    def add_frbs_have_publications(self, table, rows, value):
        '''
        Add event to the frbs_have_publications table
        '''
        rows = npappend(rows, ('frb_id', 'pub_id'))
        value = npappend(value, (self.frb_id, self.pub_id))
        self.insert_into_database(table, rows, value)

    def add_observations(self, table, rows, value):
        '''
        Add event to the observations table
        '''
        rows = npappend(rows, ('frb_id', 'author_id'))
        value = npappend(value, (self.frb_id, self.author_id))
        self.obs_id = self.insert_into_database(table, rows, value)

    def add_observations_notes(self, table, rows, value):
        '''
        Add event to the observations_notes table
        '''
        rows = npappend(rows, ('obs_id'))
        value = npappend(value, (self.obs_id))
        self.insert_into_database(table, rows, value)

    def add_observations_have_publications(self, table, rows, value):
        '''
        Add event to the observations_have_publications table
        '''
        rows = npappend(rows, ('obs_id', 'pub_id'))
        value = npappend(value, (self.obs_id, self.pub_id))
        self.insert_into_database(table, rows, value)

    def add_radio_observations_params(self, table, rows, value):
        '''
        Add event to the radio_observations_params table
        '''
        # create settigns_id if we don't have one yet
        if not 'settings_id' in rows:
            settings_id2 = str(value[rows=='raj'][0]
                               ) + ';' + str(value[rows=='decj'][0])
            settings_id = self.settings_id1 + ';' + settings_id2
        rows = npappend(rows, ('obs_id', 'author_id', 'settings_id'))
        value = npappend(value, (self.obs_id, self.author_id, settings_id))
        self.rop_id = self.insert_into_database(table, rows, value)

    def add_radio_observations_params_notes(self, table, rows, value):
        '''
        Add event to the radio_observations_params_notes table
        '''
        rows = npappend(rows, ('rop_id'))
        value = npappend(value, (self.rop_id))
        self.insert_into_database(table, rows, value)

    def add_radio_observations_params_have_publications(
      self, table, rows, value):
        '''
        Add event to the radio_observations_params_have_publications table
        '''
        rows = npappend(rows, ('rop_id', 'pub_id'))
        value = npappend(value, (self.rop_id, self.pub_id))
        self.insert_into_database(table, rows, value)

    def add_radio_measured_params(self, table, rows, value):
        '''
        Add event to the radio_measured_params table
        '''
        rows = npappend(rows, ('rop_id', 'author_id'))
        value = npappend(value, (self.rop_id, self.author_id))
        ivorn = value[npwhere(rows == 'voevent_ivorn')][0]
        self.event_exists = self.check_event_exists(ivorn)
        # add event to the database if it does not exist yet
        if not self.event_exists:
            self.rmp_id = self.insert_into_database(table, rows, value)

    def add_radio_measured_params_notes(self, table, rows, value):
        '''
        Add event to the radio_measured_params_notes table
        '''
        rows = npappend(rows, ('rmp_id'))
        value = npappend(value, (self.rmp_id))
        self.insert_into_database(table, rows, value)

    def add_radio_measured_params_have_publications(self, table, rows, value):
        '''
        Add event to the radio_measured_params_have_publications table
        '''
        rows = npappend(rows, ('rmp_id', 'pub_id'))
        value = npappend(value, (self.rmp_id, self.pub_id))
        self.insert_into_database(table, rows, value)

    def add_publications(self, table, rows, value):
        '''
        Add event to the publications table
        '''
        self.pubid = self.insert_into_database(table, rows, value)

    def add_radio_images(self, table, rows, value):
        '''
        Add event to the radio_images table
        '''
        self.rid = self.insert_into_database(table, rows, value)

    def add_radio_images_have_rmp(self, table, rows, value):
        '''
        Add event to the radio_images_have_rmp table
        '''
        rows = npappend(rows, ('radio_image_id', 'rmp_id'))
        value = npappend(value, (self.rid, self.rmp_id))
        self.insert_into_database(table, rows, value)

    def insert_into_database(self, table, rows, value):
        try:
            row_sql = ', '.join(map(str, rows))
            parameters = '(' + ','.join(['%s' for i in value]) + ')'
            value = [x.text if isinstance(
                     x, lxml.objectify.StringElement) else x for x in value]
            value = nparray(value)
            sql = """INSERT INTO {} ({}) VALUES {} RETURNING id
                  """.format(table, row_sql, parameters)
            self.cursor.execute(sql, tuple(value))
            return self.cursor.fetchone()[0]  # return last insert id
        except psycopg2.IntegrityError:
            self.connection.rollback()
            # database IntegrityError
            if table == 'authors':
                # authors table should have unique ivorn
                sql = "select id from {} WHERE id = '{}'".format(
                    table, value[rows=='ivorn'][0])
            elif table == 'frbs':
                # frbs table should have unique name
                sql = "select id from {} WHERE name = '{}'".format(
                    table, value[rows=='name'][0])
            elif table == 'observations':
                # observation table should have an unique combination of
                # frb_id, telescope, utc
                sql = """select id from {} WHERE frb_id = '{}' AND
                         telescope = '{}' AND utc = '{}'""".format(table,
                             value[rows=='frb_id'][0],
                             value[rows=='telescope'][0],
                             value[rows=='utc'][0])
            elif table == 'radio_observations_params':
                # rop table should have an unique combination of
                # obs_id, settings_id
                sql = """select id from {} WHERE obs_id = '{}' AND settings_id =
                         '{}'""".format(table,
                                        value[rows=='obs_id'][0],
                                        value[rows=='settings_id'][0])
            elif table == 'radio_measured_params':
                # voevent_ivorn must be unique
                sql = "select id from {} WHERE voevent_ivorn = '{}'".format(
                    table, value[rows=='voevent_ivorn'][0])
            else:
                # re-raise IntegrityError
                raise
            # get the id
            self.cursor.execute(sql)
            return_id = self.cursor.fetchone()
            if not return_id:
                # Could not get the id from the database
                # re-raise IntegrityError
                raise
            else:
                return return_id['id']

    def add_VOEvent_to_FRBCat(self):
        '''
        Add a VOEvent to the FRBCat database
          - input:
              connection: database connection
              cursor: database cursor object
              mapping: mapping between database entry and VOEvent value
                         db tables in mapping['FRBCAT TABLE']
                         db columns in mapping['FRBCAT COLUMN']
                         db values in mapping['values']
        '''
        # define database tables in the order they need to be filled
        #tables = ['authors', 'frbs', 'frbs_notes', 'observations',
        #          'observations_notes', 'radio_observations_params',
        #          'radio_observations_params_notes',
        #          'radio_measured_params', 'radio_measured_params_notes']
        tables = ['authors', 'frbs', 'observations',
                  'radio_observations_params',
                  'radio_measured_params']
        # loop over defined tables
        for table in tables:
            try:
                del value
            except NameError:
                pass
            # extract the rows from the mapping that are in the table
            to_add = self.mapping.loc[(self.mapping['FRBCAT TABLE'] == table) &
                                      (self.mapping['value'].notnull())]
            # extract db rows and values to add
            rows = to_add['FRBCAT COLUMN'].values
            # loop over extracted rows and insert values
            for row in rows:
                # extract value from pandas dataframe
                try:
                    # value
                    value.append(to_add.loc[to_add['FRBCAT COLUMN'] == row][
                        'value'].values[0])
                except UnboundLocalError:
                    value = [to_add.loc[to_add[
                             'FRBCAT COLUMN'] == row]['value'].values[0]]
            value = npravel(nparray(value))  # convert to numpy array
            if table == 'authors':
                self.add_authors(table, rows, value)
            if table == 'frbs':
                self.add_frbs(table, rows, value)
            if table == 'frbs_notes':
                self.add_frbs_notes(table, rows, value)
            if table == 'observations':
                self.add_observations(table, rows, value)
                # create first part of settings_id
                self.settings_id1 = str(value[rows=='telescope'][0]
                                        ) + ';' + str(value[rows=='utc'][0])
            if table == 'observations_notes':
                self.add_observations_notes(table, rows, value)
            if table == 'radio_observations_params':
                self.add_radio_observations_params(table, rows, value)
            if table == 'radio_observations_params_notes':
                self.add_radio_observations_params_notes(table, rows, value)
            if table == 'radio_measured_params':
                self.add_radio_measured_params(table, rows, value)
                if self.event_exists:
                    break  # don't want to add already existing event
            if table == 'radio_measured_params_notes':
                self.add_radio_measured_params_notes(table, rows, value)
        if self.event_exists:
            # event is already in database, rollback
            # TODO: is this what we want to do?
            self.connection.rollback()
        else:
            dbase.commitToDB(self.connection, self.cursor)
        dbase.closeDBConnection(self.connection, self.cursor)


class FRBCat_decode:
    def __init__(self, connection, cursor, frbs_id):
        self.connection = connection
        self.cursor = cursor
        self.frbs_id = frbs_id
        
    def decode_VOEvent_from_FRBCat(self):
        '''
        Decode a VOEvent from the FRBCat database
          input:
            cursor: database cursor object
            mapping: mapping between database entry and VOEvent xml
          output:
            updated mapping with added values column
        '''
        sql = """select *, radio_measured_params_notes.note as rmp_note,
                 radio_observations_params_notes.note as rop_note,
                 observations_notes.note as obs_note,
                 publications.type as pub_type
                FROM frbs
                INNER JOIN authors
                 ON frbs.author_id=authors.id
                INNER JOIN observations
                 ON observations.frb_id=frbs.id
                INNER JOIN radio_observations_params
                 ON radio_observations_params.obs_id=observations.id
                INNER JOIN radio_measured_params
                 ON radio_measured_params.rop_id=radio_observations_params.id
                LEFT JOIN radio_measured_params_notes
                 ON radio_measured_params_notes.rmp_id=radio_measured_params.id
                LEFT JOIN radio_observations_params_notes
                 ON radio_observations_params_notes.rop_id=
                  radio_observations_params.id
                LEFT JOIN observations_notes
                 ON observations_notes.obs_id=observations.id
                INNER JOIN frbs_have_publications
                 ON frbs_have_publications.frb_id=frbs.id
                INNER JOIN publications
                 ON frbs_have_publications.pub_id=publications.id
                WHERE frbs.id in ({})""".format(self.frbs_id)
        self.cursor.execute(sql)
        while True:
            # extract next event from cursor
            self.event = self.cursor.fetchone()
            if not self.event:
                # no more events to process
                break
            # set the xml name
            try:
                # more than 1 event for this frb
                counter += 1
                xmlname = self.event['name'] + '_' + str(counter) + '.xml'
            except NameError:
                # first event for this frb
                counter = 0
                xmlname = self.event['name'] + '.xml'
            self.create_xml(xmlname)

    def create_xml(self, xmlname):
        '''
        create VOEvent xml file from extracted database values
        '''
        # Initialize voevent
        self.init_voevent()
        # Define Who details
        self.set_who()
        # Define WhereWhen details
        self.set_wherewhen()
        # Define How details
        self.set_how()
        # Define What section
        self.set_what()
        # Define Why section
        self.set_why()
        # TODO: add citations (not in frbcat?)
        self.save_xml(xmlname)

    def init_voevent(self):
        '''
        Initialize voevent
        '''
        # /begin placeholders
        stream = 'teststream'
        stream_id = 1
        role = vp.definitions.roles.test
        # /end placeholders
        self.v = vp.Voevent(stream=stream, stream_id=stream_id, role=role)
        # set description TODO, do we have something to put here?
        # v.Description =

    def set_who(self):
        '''
        Add who section to voevent object
        '''
        # Set Who.Date timestamp to date of packet-generation
        # regular expression to remove ivo:// in the beginning of string
        vp.set_who(self.v, date=datetime.datetime.utcnow(),
                   author_ivorn=re.sub('^ivo://', '', self.event['ivorn']))
        # Delete the voevent-parse tag that gets added to the Who skeleton
        if hasattr(self.v.Who, 'Description'):
            del self.v.Who.Description
        # set author
        self.set_author()

    def set_author(self):
        '''
        Add author section to voevent object
        '''
        # TODO: placeholder, not in database; one of author details need
        # to be specified for a valid voevent 2.0 file
        self.event['contact_name'] = 'placeholder'
        vp.set_author(self.v,
                      title=self.event['title'],
                      shortName=self.event['short_name'],
                      logoURL=self.event['logo_url'],
                      contactName=self.event['contact_name'],
                      contactEmail=self.event['contact_email'],
                      contactPhone=self.event['contact_phone'])

    def set_what(self):
        '''
        Add What section to voevent object
        '''
        # Add radio observations params section
        self.rop_params()
        # Add radio measured params section
        self.rmp_params()

    def set_how(self):
        '''
        Add How section to voevent object
        '''
        # Describe the reference/telescope here
        # TODO: reference of telescope?
        vp.add_how(self.v, descriptions=self.event['telescope'],
                   references=vp.Reference(""))

    def set_wherewhen(self):
        '''
        Add WhereWhen section to voevent object
        '''
        # TODO: add coord system to database?
        # ra: right ascension; dec: declination; err: error radius
        vp.add_where_when(self.v,
                          coords=vp.Position2D
                          (ra=utils.dms2decdeg(self.event['raj']),
                           dec=utils.dms2decdeg(self.event['decj']),
                           err=self.event['pointing_error'], units='deg',
                           system=vp.definitions.sky_coord_system.utc_fk5_geo),
                          obs_time=self.event['utc'],
                          observatory_location=self.event['telescope'])

    def set_why(self):
        '''
        Add Why section to voevent object
        '''
        # Why section (optional) allows for speculation on probable
        # astrophysical cause
        if self.event['detected']:
            vp.add_why(self.v,
                       inferences=vp.Inference(relation='detected',
                                               name=self.event['name']))
        else:
            vp.add_why(self.v,
                       inferences=vp.Inference(name=self.event['name']))

    def save_xml(self, xmlname):
        '''
        Check the validity of the voevent xml file and save as xmlname
        '''
        # check if the created event is a valid VOEvent v2.0 event
        if vp.valid_as_v2_0(self.v):
            # save to VOEvent xml
            with open(xmlname, 'wb') as f:
                vp.dump(self.v, f, pretty_print=True)

    def rop_params(self):
        '''
        Add radio observations params section to voevent object
        '''
        # rop params in group 'radio observations params'
        rop_params = ['backend', 'beam', 'gl', 'gb', 'fwhm', 'sampling_time',
                      'bandwidth', 'centre_frequency', 'npol',
                      'channel_bandwidth', 'bits_per_sample', 'gain',
                      'tsys', 'ne2001_dm_limit', 'rop_note']
        rop_desc = VOEvent_params(param_type='rop')
        rop_param_list = self.createParamList(rop_params, rop_desc)
        self.v.What.append(vp.Group(params=rop_param_list,
                                    name='radio observations params'))

    def rmp_params(self):
        '''
        Add radio measured params section to voevent object
        '''
        rmp_params = ['dm', 'dm_error', 'snr', 'width', 'width_error_upper',
                      'width_error_lower', 'flux', 'flux_prefix',
                      'flux_error_upper', 'flux_error_lower',
                      'flux_calibrated', 'dm_index', 'dm_index_error',
                      'scattering_index', 'scattering_index_error',
                      'scattering_time', 'scattering_time_error',
                      'linear_poln_frac', 'linear_poln_frac_error',
                      'circular_poln_frac', 'circular_poln_frac_error',
                      'spectral_index', 'spectral_index_error', 'z_phot',
                      'z_phot_error', 'z_spec', 'z_spec_error', 'rank',
                      'rmp_note']
        rmp_desc = VOEvent_params(param_type='rmp')
        rmp_param_list = self.createParamList(rmp_params, rmp_desc)
        # rmp params in group 'radio measured params'
        self.v.What.append(vp.Group(params=rmp_param_list,
                           name='radio measured params'))

    def createParamList(self, params, param_desc):
        '''
        ceate a list of params, so these can be written as group
        '''
        # TODO: don't add params with no value
        for param in params:
            try:
                value = self.event[param]
            except KeyError:
                # key is not in database
                raise
            if value:
                # exctract param description 
                item_desc = param_desc.loc[param_desc[
                    'name'].str.lower()==param.lower()]
                try:
                    if not item_desc.empty:
                        paramList.extend(
                            vp.Param(name=param,
                                value=self.event[param],
                                unit=item_desc['unit'].values[0],
                                ucd=item_desc['ucd'].values[0]))
                    else:
                        paramList.extend(
                            vp.Param(name=param,
                                value=self.event[param]))
                except NameError:
                    if not item_desc.empty:
                        paramList = [vp.Param(name=param, value=self.event[param],
                                              unit=item_desc['unit'].values[0],
                                              ucd=item_desc['ucd'].values[0])]
                    else:
                        paramList = [vp.Param(name=param, value=self.event[param])]
        return paramList


def VOEvent_FRBCAT_mapping():
    '''
    Create a dictionary of dicts of VOEvent -> FRBCAT mapping
    new_event: boolean indicating if event is a new event,default=True
    '''
    # read mapping.txt into a pandas dataframe
    convert = {0: utils.strip, 1: utils.strip, 2: utils.strip,
               3: utils.strip, 4: utils.strip}
    # location of mapping.txt file
    mapping = os.path.join(os.path.dirname(sys.modules['pyfrbcatdb'].__file__),
                           'mapping.txt')
    df = pd.read_table(mapping, sep='\\', engine='c', header=0,
                       skiprows=[0], skip_blank_lines=True,
                       skipinitialspace=True,
                       converters=convert).fillna('None')
    # replace empty strings by None
    #df = df.replace([''], [None])    
    return df

def VOEvent_params(param_type=None):
    '''
    Read param txt file into a pandas dataframe
    '''
    convert = {0: utils.strip, 1: utils.strip, 2: utils.strip,
               3: utils.strip}
    # location of file containing parameter description
    if param_type == 'rop':  # radio observation param
        filename = 'rop_params.txt'
    elif param_type == 'rmp':  # radio measured param
        filename = 'rmp_params.txt'
    else:
        pass  # TODO: log warning, unknown param type
    pdesc = os.path.join(os.path.dirname(sys.modules['pyfrbcatdb'].__file__),
                         filename)  # path to file
    # create pandas dataframe
    df = pd.read_table(pdesc, sep='\\', engine='c', header=0,
                       skiprows=None, skip_blank_lines=True,
                       skipinitialspace=True,
                       converters=convert).fillna('None')
    # replace empty strings by None
    df = df.replace([''], [None])
    return df
