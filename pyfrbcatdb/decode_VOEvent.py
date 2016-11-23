'''
description:    Create a db entry for a VOEvent
license:        APACHE 2.0
author:         Ronald van Haren, NLeSC (r.vanharen@esciencecenter.nl)
'''
import voeventparse as vp
import pandas
from pyfrbcatdb import dbase
from pytz import timezone
from pyfrbcatdb.FRBCat import *
from pyfrbcatdb import utils


class decode_VOEvent:
    def __init__(self, voevent, DB_NAME, DB_HOST, DB_PORT, USER_NAME, 
                 USER_PASSWORD):
        self.DB_NAME = DB_NAME
        self.DB_HOST = DB_HOST
        self.DB_PORT = DB_PORT
        self.USER_NAME = USER_NAME
        self.USER_PASSWORD = USER_PASSWORD
        self.process_VOEvent(voevent)
    
    def process_VOEvent(self, voevent):
        # load mapping VOEvent -> FRBCAT
        mapping = VOEvent_FRBCAT_mapping()
        # parse VOEvent xml file
        vo_dict, event_type = self.parse_VOEvent(voevent, mapping)
        # create/delete a new FRBCat entry
        self.update_FRBCat(vo_dict, event_type)

    def get_param(self, param_data, mapping, idx):
        '''
        Get param data for a given attribute
        '''
        # mapping['VOEvent TYPE'][idx] not in ['Param', 'Coord', 'ISOTime']
        try:
            return (param_data[mapping['FRBCAT TABLE'].iloc[idx].replace('_',' ')]
                    [mapping['FRBCAT COLUMN'].iloc[idx]])['value']
        except KeyError:
            return None

    def get_coord(self, v, mapping, idx):
        '''
        Get astro coordinates
        '''
        switcher = {
            'raj': 'ra',
            'decj': 'dec',
            'gl': 'gl',
            'gb': 'gb',
            'pointing_error': 'err',
        }
        try:
            utils.decdeg2dms(vp.pull_astro_coords(v, index=0).ra)
            key = switcher[[mapping['FRBCAT COLUMN'].iloc[idx]][0]]
            if key in ['raj', 'decj', 'ra', 'dec']:
                return utils.decdeg2dms(getattr(vp.pull_astro_coords(v, index=0),
                                        key))
            else:
                return getattr(vp.pull_astro_coords(v, index=0),
                            key)
        except AttributeError:
            return None
        except KeyError:
            return None

    def get_attrib(self, v, mapping, idx):
        '''
        Get xml attributes
        '''
        try:
            return v.attrib[mapping['VOEvent'].iloc[idx]]
        except ValueError:
            return None
        except KeyError:
            return None

    def get_utc_time_str(self, v):
        '''
        Get time in UTC
        Return string 'YYYY-MM-DD HH:MM:SS'
        '''
        isotime = vp.pull_isotime(v, index=0)
        # convert to UTC
        utctime = isotime.astimezone(timezone('UTC'))
        # return time in UTC string
        return utctime.strftime("%Y-%m-%d %H:%M:%S")

    def get_value(self, v, param_data, mapping, idx):
        switcher = {
            'Param':    self.get_param(param_data, mapping, idx),
            'Coord':    self.get_coord(v, mapping, idx),
            'ISOTime':  self.get_utc_time_str(v),
            'XML':      vp.dumps(v),
            'attrib':   self.get_attrib(v, mapping, idx),
            '':         None
        }
        # get function from switcher dictionary
        return switcher[mapping['VOEvent TYPE'].iloc[idx]]

    def parse_VOEvent(self, voevent, mapping):
        '''
        parse VOEvent xml file
            input:
            - voevent: VOEvent xml file
            - mapping: mapping dictionary voevent -> FRBCAT
            returns vo_dict, mapping
            - vo_dict: dictionary vo_event: value
            - mapping: dictionary vo_event: FRBCAT location
        '''
        # load VOEvent xml file
        try:
            v = vp.load(voevent)
        except AttributeError:
            f = open(voevent, "rb")
            v = vp.load(f)
            f.close()
            
        # assert if xml file is a valid VOEvent
        vp.assert_valid_as_v2_0(v)
        # Check if the event is a new VOEvent
        # For a new VOEvent there should be no citations
        try:
            event_type = (v.xpath('Citations')[0].EventIVORN.attrib['cite'],
                        v.xpath('Citations')[0].EventIVORN.text)
        except IndexError:
            event_type = ('new', None)
        mapping = VOEvent_FRBCAT_mapping()
        # use the mapping to get required data from VOEvent xml
        # if a path is not found in the xml it gets an empty list which is
        # removed in the next step
        # puts all params into dict param_data[group][param_name]
        param_data = vp.pull_params(v)
        vo_data = (lambda v=v, mapping=mapping: (
                [v.xpath('.//' + event.replace('.', '/')) if mapping[
                    'VOEvent TYPE'].iloc[idx] not in [
                    'Param', 'Coord', 'ISOTime', 'XML', 'attrib']
                    and event else self.get_value(
                    v, param_data, mapping, idx) for idx, event in
                    enumerate(mapping['VOEvent'])]))()
        vo_data = [None if not a else a for a in vo_data]
        vo_alta = (lambda v=v, mapping=mapping: (
                [v.xpath('.//' + event.replace('.', '/')) if mapping[
                    'VOEvent TYPE'].iloc[idx] not in [
                    'Param', 'Coord', 'ISOTime', 'XML', 'attrib']
                    and event else self.get_value(
                    v, param_data, mapping, idx) for idx, event in
                    enumerate(mapping['VOEvent_alt'])]))()
        vo_alta = [None if not a else a for a in vo_alta]
        # TODO: merging is a placeholder:
        # some things may depend on new/not new event
        merged = (lambda vo_data=vo_data, vo_alta=vo_alta: ([vo_data[idx] if
                vo_data[idx] else vo_alta[idx] for idx in
                range(0, len(vo_alta))]))()
        # make sure we don't have any lists here
        merged = [x[0] if isinstance(x, list) else x for x in merged]
        # add to pandas dataframe as a new column
        mapping.loc[:, 'value'] = pandas.Series(merged, index=mapping.index)
        # need to add xml file to database as well
        return mapping, event_type

    def update_FRBCat(self, mapping, event_type):
        '''
        Add new FRBCat entry
        '''
        # connect to database
        # TODO: add connection details
        connection, cursor = dbase.connectToDB(self.DB_NAME, self.USER_NAME,
                                               self.USER_PASSWORD, self.DB_HOST,
                                               self.DB_PORT)
        if event_type[0] in ['retraction', 'supersedes']:
            # for retraction or supersedes we need to remove the entry from FRBCat
            FRBCat = FRBCat_remove(connection, cursor, mapping, event_type)
            FRBCat = FRBCat.remove_entry()
        if event_type[0] in ['new', 'followup', 'supersedes']:
            # for new, followup, supersedes we need to add an entry to FRBCat
            FRBCat = FRBCat_add(connection, cursor, mapping, event_type)
            FRBCat.add_VOEvent_to_FRBCat()
