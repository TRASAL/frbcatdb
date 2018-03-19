'''
description:    FRBCat functionality for pyfrbcatdb
license:        APACHE 2.0
author:         Ronald van Haren, NLeSC (r.vanharen@esciencecenter.nl)
'''
from pyfrbcatdb import dbase as dbase
import os
import sys
from numpy import append as npappend
from numpy import array as nparray
import voeventparse as vp
import datetime
import pytz
import re
import psycopg2
import lxml
from xml.dom.minidom import parseString
import yaml
from astropy import units as u
from astropy.coordinates import SkyCoord


class FRBCat_add:
    '''
    Class module that adds a decoded VOEvent file to the FRBCat
    database.

    :param connection: database connection
    :param cursor: database cursor object
    :param mapping: mapping between database entry and VOEvent value.
    :param event_type: type of VOEvent
    :type connection: psycopg2.extensions.connection
    :type cursor: psycopg2.extras.DictCursor
    :type mapping: dict
    :type event_type: str
    '''
    def __init__(self, connection, cursor, mapping, event_type):
        self.connection = connection
        self.cursor = cursor
        self.mapping = mapping
        self.event_type = event_type

    def check_author_exists(self, ivorn):
        '''
        Check if author already exists in the database.
        If the author is found, set self.author_id to the id
        found in the database.

        :param ivorn: author ivorn from VOEvent file
        :type ivorn: string
        :returns: boolean if author is found or not
        :rtype: bool
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
        Check if event ivorn already exists in database.
        If the event is found, set self.event_id to the id
        found in the database.

        :param ivorn: event ivorn from VOEvent file
        :type ivorn: string
        :returns: boolean if event is found or not
        :rtype: bool
        '''
        # check if the event ivorn is already in the database
        event_id = dbase.extract_from_db_sql(
            self.cursor, 'radio_measured_params', 'id', 'voevent_ivorn', ivorn)
        if not event_id:  # did not find the event ivorn
            return False
        else:  # set self.event_id to the id of the ivorn in the database
            self.event_id = event_id['id']
            return True

    def set_rank(self):
        '''
        Return the rank for the event to be inserted.
        First event of an FRB is rank=1, each next event increments it by 1.

        :returns: next_rank, rank of the event to be inserted
        :rtype: int
        '''
        sql = ("select rmp.rank from radio_measured_params rmp join " +
               "radio_observations_params rop ON rmp.rop_id=rop.id join " +
               "observations o on rop.obs_id=o.id join frbs on " +
               "o.frb_id=frbs.id where frbs.id={}").format(self.frb_id)
        self.cursor.execute(sql)
        ranks = self.cursor.fetchall()
        try:
            max_rank = max([x[0] for x in ranks])
            next_rank = max_rank + 1
        except ValueError:
            # first entry of this FRB
            next_rank = 1
        return next_rank

    def add_authors(self, table, cols, value):
        '''
        Add author to the database if the ivorn is not in the authors table.

        :param table: name of database table
        :param cols: cols in database table that need to be added
        :param value: values to be set for the cols
        :type table: str
        :type cols: list
        :type value: list
        '''
        # check if author already exists in database
        ivorn = value[cols == 'ivorn']
        author_exists = self.check_author_exists(ivorn)
        # add author to database if author does not yet exist in db
        if not author_exists:
            self.author_id = self.insert_into_database(table, cols, value)

    def add_frbs(self, table, cols, value):
        '''
        Add event to the frbs table.

        :param table: name of database table
        :param cols: cols in database table that need to be added
        :param value: values to be set for the cols
        :type table: str
        :type cols: list
        :type value: list
        '''
        cols = npappend(cols, 'author_id')
        value = npappend(value, self.author_id)
        # try to insert into database / return frb id
        self.frb_id = self.insert_into_database(table, cols, value)
        # update database if type is supersedes
        self.update_database(table, cols, value)

    def add_observations(self, table, cols, value):
        '''
        Add event to the observations table.

        :param table: name of database table
        :param cols: cols in database table that need to be added
        :param value: values to be set for the cols
        :type table: str
        :type cols: list
        :type value: list
        '''
        cols = npappend(cols, ('frb_id', 'author_id'))
        value = npappend(value, (self.frb_id, self.author_id))
        # try to insert into database / return observation id
        self.obs_id = self.insert_into_database(table, cols, value)
        # update database if type is supersedes
        self.update_database(table, cols, value)

    def add_radio_observations_params(self, table, cols, value):
        '''
        Add event to the radio_observations_params table.

        :param table: name of database table
        :param cols: cols in database table that need to be added
        :param value: values to be set for the cols
        :type table: str
        :type cols: list
        :type value: list
        '''
        # create settigns_id if we don't have one yet
        if 'settings_id' not in cols:
            settings_id2 = str(nparray(value)[nparray(cols) == 'raj'][0]
                               ) + ';' + str(
                                 nparray(value)[nparray(cols) == 'decj'][0])
            settings_id = self.settings_id1 + ';' + settings_id2
        cols = npappend(cols, ('obs_id', 'author_id', 'settings_id'))
        value = npappend(value, (self.obs_id, self.author_id, settings_id))
        self.rop_id = self.insert_into_database(table, cols, value)
        # update database if type is supersedes
        self.update_database(table, cols, value)

    def add_radio_observations_params_notes(self, table, cols, notes):
        '''
        Add event to the radio_observations_params_notes table.

        :param table: name of database table
        :param cols: cols in database table that need to be added
        :param notes: list of notes (each note is a string)
        :type table: str
        :type cols: list
        :type notes: list
        '''

        for idx, note in enumerate(notes):  # loop over all notes
            cols_i = npappend(cols[idx], ('rop_id', 'last_modified', 'author'))
            value_i = npappend(note, (self.rop_id, self.authortime,
                                      self.authorname))
            self.insert_into_database(table, cols_i, value_i)

    def add_radio_measured_params(self, table, cols, value):
        '''
        Add event to the radio_measured_params table

        :param table: name of database table
        :param cols: cols in database table that need to be added
        :param value: values to be set for the cols
        :type table: str
        :type cols: list
        :type value: list
        '''
        rank = self.set_rank()
        cols = npappend(cols, ('rop_id', 'author_id', 'rank'))
        value = npappend(value, (self.rop_id, self.author_id, rank))
        ivorn = value[cols == 'voevent_ivorn'][0]
        self.event_exists = self.check_event_exists(ivorn)
        # add event to the database if it does not exist yet
        self.rmp_id = self.insert_into_database(table, cols, value)
        # update database if type is supersedes
        self.update_database(table, cols, value)

    def add_radio_measured_params_notes(self, table, cols, notes):
        '''
        Add event to the radio_measured_params_notes table.

        :param table: name of database table
        :param cols: cols in database table that need to be added
        :param notes: list of notes (each note is a string)
        :type table: str
        :type cols: list
        :type notes: list
        '''
        for idx, note in enumerate(notes):  # loop over all notes
            cols_i = npappend(cols[idx], ('rmp_id', 'last_modified', 'author'))
            value_i = npappend(note, (self.rmp_id, self.authortime,
                                      self.authorname))
            self.insert_into_database(table, cols_i, value_i)

    def insert_into_database(self, table, cols, value):
        '''
        Insert event into the database. This method runs sql command.
        If not all required parameters are specified, assume this is an
        update event and return the id for the entry in the table,
        else return the id of the insert.

        :param table: name of database table
        :param cols: cols in database table that need to be added
        :param value: values to be set for the cols
        :type table: str
        :type cols: list
        :type value: list
        :returns: id of insert or id of existing entry in table
        :rtype: int
        '''
        try:
            # remove cols with empty values
            cols = nparray([i for i, j in zip(cols, value) if j])
            value = nparray([j for j in value if j]).flatten()
            # define sql params
            col_sql, parameters, value = self.define_sql_params(cols, value)
            # check if VOEVent passes the not null constraints of database
            if (((table == 'radio_measured_params') and
                 (set(['voevent_ivorn',
                       'dm', 'snr', 'width']) < set(cols))) or
                ((table == 'radio_observations_params') and
                 (set(['raj', 'decj']) < set(cols))) or
                ((table == 'observations') and
                 (set(['telescope', 'verified']) < set(cols))) or
                ((table == 'frbs') and
                 (set(['name', 'utc']) < set(cols))) or
                ((table == 'authors') and
                 (set(['ivorn']) < set(cols))) or
                (table == 'radio_measured_params_notes') or (
                  table == 'radio_observations_params_notes')):
                # define sql statement
                sql = """INSERT INTO {} ({}) VALUES {}  ON CONFLICT DO NOTHING
                         RETURNING id""".format(table, col_sql, parameters)
                # execute sql statement, try to insert into database
                self.cursor.execute(sql, tuple(value))
                try:
                    # return id from insert
                    return self.cursor.fetchone()[0]  # return last insert id
                except TypeError:
                    # insert did not happen due to already existing entry
                    # in database, return id of the existing entry
                    return self.get_id_existing(table, cols, value)
            else:
                # not all required parameters are in voevent xml file
                # return id if it is already in the database
                return self.get_id_existing(table, cols, value)
        except psycopg2.IntegrityError:
            # rollback changes
            self.connection.rollback()
            # re-raise exception
            raise

    def get_authortime(self):
        '''
        Get time voevent file was authored from mapping dictionary.

        :returns: datetime string of format '%Y-%m-%d %H:%M:%S'
        :rtype: str
        '''
        try:
            return [item.get('value') for item in
                    self.mapping.get('radio_observations_params_notes')
                    if item.get('type') == 'authortime'][0]
        except IndexError:
            try:
                return[item.get('value') for item in
                       self.mapping.get('radio_measured_params_notes')
                       if item.get('type') == 'authortime'][0]
            except IndexError:
                # fall back to insert datetime
                return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def get_id_existing(self, table, cols, value):
        '''
        Get id of an existing entry in database table.

        :param table: name of database table
        :param cols: cols in database table that need to be added
        :param value: values to be set for the cols
        :type table: str
        :type cols: list
        :type value: list
        :returns: id of existing entry in table
        :rtype: int
        '''
        if table == 'authors':
            # authors table should have unique ivorn
            sql = "select id from {} WHERE ivorn = '{}'".format(
                table, value[cols == 'ivorn'][0])
        elif table == 'frbs':
            # frbs table should have unique name
            sql = "select id from {} WHERE name = '{}'".format(
                table, value[cols == 'name'][0])
        elif table == 'observations':
            # observation table should have an unique combination of
            # frb_id, telescope, utc
            sql = """select id from {} WHERE frb_id = '{}' AND
                    telescope = '{}' AND utc = '{}'""".format(
                      table, value[cols == 'frb_id'][0],
                      value[cols == 'telescope'][0],
                      value[cols == 'utc'][0])
        elif table == 'radio_observations_params':
            # rop table should have an unique combination of
            # obs_id, settings_id
            sql = """select id from {} WHERE obs_id = '{}' AND settings_id =
                    '{}'""".format(table,
                                   value[cols == 'obs_id'][0],
                                   value[cols == 'settings_id'][0])
        elif table == 'radio_measured_params':
            # voevent_ivorn mus tbe unique
            sql = "select id from {} WHERE voevent_ivorn = '{}'".format(
                table, value[cols == 'voevent_ivorn'][0])
        else:
            # raise IntegrityError
            raise psycopg2.IntegrityError(
              "Unable database table: {}".format(table))
        # get the id
        self.cursor.execute(sql)
        return_id = self.cursor.fetchone()
        if not return_id:
            # Could not get the id from the database
            # re-raise IntegrityError
            raise psycopg2.IntegrityError(
              "Unable to get id from database: {}".format(sql))
        else:
            return return_id['id']

    def update_database(self, table, cols, value):
        '''
        If type supersedes we need to update existing table values,
        else do nothing. This method executes the sql statement.

        :param table: name of database table
        :param cols: cols in database table that need to be added
        :param value: values to be set for the cols
        :type table: str
        :type cols: list
        :type value: list

        '''
        # remove cols with empty values
        cols = nparray([i for i, j in zip(cols, value) if j])
        value = nparray([j for j in value if j]).flatten()
        if (self.event_type == 'supersedes'):
            # event is of type supersedes, so we need to update
            col_sql, parameters, value = self.define_sql_params(cols, value)
            # define sql statments
            if table == 'frbs':
                sql = "update {} SET ({}) = {} WHERE id='{}'".format(
                  table, col_sql, parameters, self.frb_id)
            elif table == 'observations':
                sql = "update {} SET ({}) = {} WHERE id='{}'".format(
                  table, col_sql, parameters, self.obs_id)
            elif table == 'radio_observations_params':
                sql = "update {} SET ({}) = {} WHERE id='{}'".format(
                  table, col_sql, parameters, self.rop_id)
            elif table == 'radio_measured_params':
                sql = "update {} SET ({}) = {} WHERE id='{}'".format(
                  table, col_sql, parameters, self.rmp_id)
            else:
                pass
            try:
                # execute sql statement
                self.cursor.execute(sql, tuple(value))
            except NameError:
                pass
        else:
            pass

    def add_VOEvent_to_FRBCat(self):
        '''
        Add a VOEvent to the FRBCat database. This is the main
        method that iterates over all tables and calls the
        respective method for each table.
        Finally, the database changes are committed and the
        database connection is closed.
        '''
        # define database tables in the order they need to be filled
        tables = ['authors', 'frbs', 'observations',
                  'radio_observations_params',
                  'radio_observations_params_notes',
                  'radio_measured_params', 'radio_measured_params_notes']
        # get time voevent file was authored
        self.authortime = self.get_authortime()
        # loop over defined tables
        for table in tables:
            # extract cols that have values
            cols = [item.get('column') for item in self.mapping.get(table) if
                    item.get('value') is not None]
            values = [item.get('value') for item in self.mapping.get(table) if
                      item.get('value') is not None]
            if table in ['radio_measured_params_notes',
                         'radio_observations_params_notes']:
                notes = [item.get('note') for item in self.mapping.get(table)
                         if item.get('note') is not None]
            if table == 'authors':
                self.add_authors(table, cols, values)
                try:
                    # set authorname, needed for notes
                    self.authorname = values[cols.index('contact_name')]
                except ValueError:
                    self.authorname = 'FRBCat insert'
            if table == 'frbs':
                self.add_frbs(table, cols, values)
            if table == 'frbs_notes':
                self.add_frbs_notes(table, cols, values)
            if table == 'observations':
                self.add_observations(table, cols, values)
                # create first part of settings_id
                self.settings_id1 = str(values[cols == 'telescope'][0]
                                        ) + ';' + str(values[cols == 'utc'][0])
            if table == 'observations_notes':
                self.add_observations_notes(table, cols, values)
            if table == 'radio_observations_params':
                self.add_radio_observations_params(table, cols, values)
            if table == 'radio_observations_params_notes':
                self.add_radio_observations_params_notes(table, cols, notes)
            if table == 'radio_measured_params':
                self.add_radio_measured_params(table, cols, values)
                if (self.event_exists and (self.event_type != 'supersedes')):
                    # event exists already and is not of type supersedes
                    break  # don't want to add already existing event
            if table == 'radio_measured_params_notes':
                self.add_radio_measured_params_notes(table, cols, notes)
        if (self.event_exists and (self.event_type != 'supersedes')):
            # event is already in database, rollback
            self.connection.rollback()
        else:
            dbase.commitToDB(self.connection, self.cursor)
        dbase.closeDBConnection(self.connection, self.cursor)

    def retract(self, voevent_cited):
        '''
        Retract event with the ivorn given by voevent_cited.
        Retracting event should set detected/verified to False in
        observations table. Database changes are committed and
        database connection is closed.

        :param voevent_cited: event ivorn to be retracted
        :type voevent_cited: str
        '''
        sql = ("select o.id from radio_measured_params rmp join " +
               "radio_observations_params rop ON rmp.rop_id=rop.id join " +
               "observations o on rop.obs_id=o.id join frbs on " +
               "o.frb_id=frbs.id join authors on frbs.author_id=authors.id " +
               "where voevent_ivorn='{}'").format(voevent_cited)
        try:
            # execute sql statement
            self.cursor.execute(sql)
        except NameError:
            pass
        # get id in the observations table
        obs_id = self.cursor.fetchone()
        if obs_id:
            # observation is indeed in the database
            col_sql = ', '.join(map(str, ['detected', 'verified']))
            parameters = ', '.join(map(str, [False, False]))
            sql = "update {} SET ({}) = ({}) WHERE id='{}'".format(
              'observations', col_sql, parameters, obs_id[0])
            try:
                # execute sql statement
                self.cursor.execute(sql)
            except NameError:
                pass
            # commit changes to database
            dbase.commitToDB(self.connection, self.cursor)
        # close database connection
        dbase.closeDBConnection(self.connection, self.cursor)

    @staticmethod
    def define_sql_params(cols, value):
        '''
        Format sql params for the sql command from the cols and values.

        :param cols: cols in the db table the sql command needs to operate on
        :param value: values of the col variables
        :type cols: numpy.ndarray
        :type value: numpy.ndarray
        :returns: col_sql (formatted cols array as a comma-seperated string),
            parameters (string of format (%s,%s,...), equal to the number of
            elements in cols),
            value (values of the col objects, converted to flattened
            regular numpy array)
        :rtype: str, str, numpy.ndarray
        '''
        # define sql params
        col_sql = ', '.join(map(str, cols))
        parameters = '(' + ','.join(['%s' for i in value]) + ')'
        value = [x.text if isinstance(
                 x, lxml.objectify.StringElement) else x for x in value]
        value = nparray(value)
        return col_sql, parameters, value


class FRBCat_create:
    '''
    Class module that creates a VOEvent file from the FRBCat
    database.

    :param connection: database connection
    :param cursor: database cursor object
    :param frbs_id: id in frbs table of FRB to be extracted
    :type connection: psycopg2.extensions.connection
    :type cursor: psycopg2.extras.DictCursor
    :type frbs_id: int
    '''
    def __init__(self, connection, cursor, frbs_id):
        self.connection = connection
        self.cursor = cursor
        self.frbs_id = frbs_id

    def create_VOEvent_from_FRBCat(self):
        '''
        Create a VOEvent from the FRBCat database. Method gets
        all information from the database, sets and output name
        for the VOEvent and calls the create_xml method.
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
        Create VOEvent xml file from extracted database values.
        Calls all the methods to set the different sections and
        finally calls the save_xml method.

        :param xmlname: name of the output file
        :type xmlname: str
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
        # save VOEvent file
        self.save_xml(xmlname, force_pretty_print=True)

    def init_voevent(self):
        '''
        Initialize voevent.
        '''
        stream = self.event['voevent_ivorn'].lstrip('ivo://')
        stream_id = 1
        role = vp.definitions.roles.test
        self.v = vp.Voevent(stream=stream, stream_id=stream_id, role=role)

    def set_who(self):
        '''
        Add who section to voevent object.
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
        Add author section to voevent object.
        '''
        # set a plactholder if none of the contact details are in the database
        # for some of the original entries
        if not any([self.event['title'], self.event['short_name'],
                    self.event['contact_name'], self.event['contact_email'],
                    self.event['contact_phone']]):
            self.event['contact_name'] = 'frbcatdb_extracted'
        # set author section
        vp.set_author(self.v,
                      title=self.event['title'],
                      shortName=self.event['short_name'],
                      logoURL=self.event['logo_url'],
                      contactName=self.event['contact_name'],
                      contactEmail=self.event['contact_email'],
                      contactPhone=self.event['contact_phone'])

    def set_what(self):
        '''
        Add What section to voevent object.
        '''
        mapping = parse_mapping()
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
        Add How section to voevent object.
        '''
        # Describe the reference/telescope here
        # TODO: reference of telescope?
        vp.add_how(self.v, descriptions=self.event['telescope'],
                   references=vp.Reference(""))

    def set_wherewhen(self):
        '''
        Add WhereWhen section to voevent object.
        '''
        # use astropy to convert raj and decj angles to degrees
        skcoord = SkyCoord(ra=self.event['raj'], dec=self.event['decj'],
                           unit=(u.hourangle, u.deg))
        raj = skcoord.ra.deg
        decj = skcoord.dec.deg
        # ra: right ascension; dec: declination; err: error radius
        if self.event['beam_semi_major_axis']:
            vp.add_where_when(
                self.v,
                coords=vp.Position2D
                (ra=raj,
                 dec=decj,
                 err=self.event['beam_semi_major_axis'],
                 units='deg',
                 system=vp.definitions.sky_coord_system.utc_fk5_geo),
                obs_time=pytz.utc.localize(self.event['utc']),
                observatory_location=self.event['telescope'])
        else:
            # some of the original database entries do not have a value
            # for beam_semi_major_axis, set to 0
            vp.add_where_when(
                self.v,
                coords=vp.Position2D
                (ra=raj,
                 dec=decj,
                 err=0, units='deg',
                 system=vp.definitions.sky_coord_system.utc_fk5_geo),
                obs_time=pytz.utc.localize(self.event['utc']),
                observatory_location=self.event['telescope'])

    def set_why(self):
        '''
        Add Why section to voevent object.
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
        Check the validity of the voevent xml file and save as xmlname.
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
        Ceate a list of params, so these can be written as group.

        :param params: List of params (list of dicts). Each dict
            contains the information for one parameter.
        :type params: list
        :returns: paramList, list of lxml.objectify.ObjectifiedElements
        :rtype: list
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
                    paramList = [
                        vp.Param(name=param.get('param_name'),
                                 value=self.event[param.get('column')],
                                 unit=param.get('unit'),
                                 ucd=param.get('ucd'))]
        return paramList

    def add_params(self, supermapping):
        '''
        Add radio observations params section to voevent object.

        :param supermapping: flattened mapping dictionary in list of dicts
        :type supermapping: list
        '''
        param_groups = ['observatory parameters',
                        'event parameters', 'advanced parameters']
        for group in param_groups:
            params = [param for param in supermapping if
                      param.get('param_group') == group]
            param_list = self.createParamList(params)
            self.v.What.append(vp.Group(params=param_list,
                                        name=group))


def parse_mapping():
    '''
    Read mapping from json file.

    :returns: mapping dictionary from mapping.json data file
    :rtype: dict
    '''
    # define path to mapping.json file
    filename = "mapping.json"
    mfile = os.path.join(os.path.dirname(sys.modules['pyfrbcatdb'].__file__),
                         filename)  # path to file
    with open(mfile) as f:
        mapping = yaml.safe_load(f)
    return mapping
