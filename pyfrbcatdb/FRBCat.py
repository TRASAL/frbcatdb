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
import pytz
import re
import psycopg2
import lxml
from xml.dom.minidom import parseString
import yaml


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
        ivorn = value[rows == 'ivorn']
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
        # try to insert into database / return frb id
        self.frb_id = self.insert_into_database(table, rows, value)
        # event is of type supersedes, so we need to update
        if self.event_type=='supersedes':
            self.update_database(table, rows, value)

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
        # try to insert into database / return observation id
        self.obs_id = self.insert_into_database(table, rows, value)
        # event is of type supersedes, so we need to update
        if self.event_type=='supersedes':
            self.update_database(table, rows, value)

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
        if self.event_type=='supersedes':
            self.update_database(table, rows, value)

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
        ivorn = value[rows == 'voevent_ivorn'][0]
        self.event_exists = self.check_event_exists(ivorn)
        # add event to the database if it does not exist yet
        self.rmp_id = self.insert_into_database(table, rows, value)
        if self.event_type=='supersedes':
            self.update_database(table, rows, value)

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
                # voevent_ivorn mus tbe unique
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

    def update_database(self, table, rows, value):
        '''
        for type supersedes we need to update existing table values
        '''
        row_sql = ', '.join(map(str, rows))
        parameters = '(' + ','.join(['%s' for i in value]) + ')'
        value = [x.text if isinstance(
                 x, lxml.objectify.StringElement) else x for x in value]
        value = nparray(value)
        if table == 'frbs':
            sql = "update {} SET ({}) = {} WHERE id='{}'".format(table, row_sql, parameters, self.frb_id)
        elif table == 'observations':
            sql = "update {} SET ({}) = {} WHERE id='{}'".format(table, row_sql, parameters, self.obs_id)
        elif table == 'radio_observations_params':
            sql = "update {} SET ({}) = {} WHERE id='{}'".format(table, row_sql, parameters, self.rop_id)
        elif table == 'radio_measured_params':
            sql = "update {} SET ({}) = {} WHERE id='{}'".format(table, row_sql, parameters, self.rmp_id)
        else:
            pass
        try:
            # execute sql statement
            self.cursor.execute(sql, tuple(value))
        except NameError:
            pass

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
            # extract rows that have values
            rows = [item.get('column') for item in self.mapping.get(table) if
                    item.get('value') is not None]
            values = [item.get('value') for item in self.mapping.get(table) if
                    item.get('value') is not None]
            if table == 'authors':
                self.add_authors(table, rows, values)
            if table == 'frbs':
                self.add_frbs(table, rows, values)
            if table == 'frbs_notes':
                self.add_frbs_notes(table, rows, values)
            if table == 'observations':
                self.add_observations(table, rows, values)
                # create first part of settings_id
                self.settings_id1 = str(values[rows=='telescope'][0]
                                        ) + ';' + str(values[rows=='utc'][0])
            if table == 'observations_notes':
                self.add_observations_notes(table, rows, values)
            if table == 'radio_observations_params':
                self.add_radio_observations_params(table, rows, values)
            if table == 'radio_observations_params_notes':
                self.add_radio_observations_params_notes(table, rows, values)
            if table == 'radio_measured_params':
                self.add_radio_measured_params(table, rows, values)
                if (self.event_exists and (self.event_type!='supersedes')):
                    # event exists already and is not of type supersedes
                    break  # don't want to add already existing event
            if table == 'radio_measured_params_notes':
                self.add_radio_measured_params_notes(table, rows, values)
        if (self.event_exists and (self.event_type!='supersedes')):
            # event is already in database, rollback
            # TODO: is this what we want to do?
            self.connection.rollback()
        else:
            dbase.commitToDB(self.connection, self.cursor)
            #self.connection.rollback()
        dbase.closeDBConnection(self.connection, self.cursor)

    def retract(self):
        '''
        retracting event should set detected/verified to False in
        observations table
        '''
        # extract rows that have values
        table = 'radio_measured_params'
        rows = [item.get('column') for item in self.mapping.get(table) if
                item.get('value') is not None]
        values = [item.get('value') for item in self.mapping.get(table) if
                  item.get('value') is not None]
        voevent_ivorn = values[rows=='voevent_ivorn']
        sql = "select o.id from radio_measured_params rmp join radio_observations_params rop ON rmp.rop_id=rop.id join observations o on rop.obs_id=o.id join frbs on o.frb_id=frbs.id join authors on frbs.author_id=authors.id where voevent_ivorn='{}'".format(voevent_ivorn)
        try:
            # execute sql statement
            self.cursor.execute(sql)
        except NameError:
            pass
        # get id in the observations table
        obs_id = self.cursor.fetchone()
        if obs_id:
            # observation is indeed in the database
            row_sql = ', '.join(map(str, ['detected', 'verified']))
            parameters = ', '.join(map(str, [False, False]))
            sql = "update {} SET ({}) = ({}) WHERE id='{}'".format('observations', row_sql, parameters, obs_id)
            try:
                # execute sql statement
                self.cursor.execute(sql)
            except NameError:
                pass
            # commit changes to database
            dbase.commitToDB(self.connection, self.cursor)
        # close database connection
        dbase.closeDBConnection(self.connection, self.cursor)

class FRBCat_create:
    def __init__(self, connection, cursor, frbs_id):
        self.connection = connection
        self.cursor = cursor
        self.frbs_id = frbs_id

    def create_VOEvent_from_FRBCat(self):
        '''
        Create a VOEvent from the FRBCat database
          output:
            VOEvent XML file
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
        self.save_xml(xmlname, force_pretty_print=True)

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
        mapping = parse_mapping()
        super_dict = {}
        # flatten the mapping dictionary into a list of dicts
        try:
          values = mapping.itervalues()  # python 2 compatibility
        except AttributeError:
          values = mapping.values()
        for value in values:
          try:
              supermapping += value
          except NameError:
              supermapping = value
        self.add_params(supermapping)

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
                          obs_time=pytz.utc.localize(self.event['utc']),
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

    def save_xml(self, xmlname, force_pretty_print=False):
        '''
        Check the validity of the voevent xml file and save as xmlname
        '''
        # check if the created event is a valid VOEvent v2.0 event
        if vp.valid_as_v2_0(self.v):
            # save to VOEvent xml
            if force_pretty_print:
                with open(xmlname, 'w') as f:
                 if force_pretty_print:
                     # use xml.dom.minidom to force pretty printing xml
                     vp.voevent._return_to_standard_xml(self.v)
                     txt = lxml.etree.tostring(self.v)
                     f.write(parseString(txt).toprettyxml())
            else:
                with open(xmlname, 'wb') as f:
                    # lxml pretty printing often does not work
                    # workaround use force_pretty_print=True
                    vp.dump(self.v, f, pretty_print=True)

    def createParamList(self, params):
        '''
        ceate a list of params, so these can be written as group
        '''
        for param in params:
            # get value from database
            value = self.event[param.get('column')]
            if value:
                # extract param description
                # TODO: set Description as well
                try:
                    paramList.extend(
                      vp.Param(name=param.get('param_name'),
                      value=self.event[param.get('column')],
                      unit=param.get('unit'),
                      ucd=param.get('ucd')))
                except NameError:
                    paramList = vp.Param(name=param.get('param_name'),
                                         value=self.event[param.get('column')],
                                         unit=param.get('unit'),
                                         ucd=param.get('ucd'))
        return paramList

    def add_params(self, supermapping):
        '''
        Add radio observations params section to voevent object
        '''
        param_groups = ['observatory parameters',
                        'event parameters', 'advanced parameters']
        for group in param_groups:
            params = [param for param in supermapping if
                      param.get('param_group')==group]
            param_list = self.createParamList(params)
            self.v.What.append(vp.Group(params=param_list,
                                        name=group))

def parse_mapping():
    '''
    read mapping from json file
    '''
    # define path to mapping.json file
    filename = "mapping.json"
    mfile = os.path.join(os.path.dirname(sys.modules['pyfrbcatdb'].__file__),
                         filename)  # path to file
    with open(mfile) as f:
      mapping = yaml.safe_load(f)
    return mapping
