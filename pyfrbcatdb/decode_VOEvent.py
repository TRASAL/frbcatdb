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
from pyfrbcatdb.logger import logger

class decode_VOEvent(logger):
    def __init__(self, voevent, DB_NAME, DB_HOST, DB_PORT, USER_NAME, 
                 USER_PASSWORD, LOG_FILE):
        logger.__init__(self, LOG_FILE)
        self.DB_NAME = DB_NAME
        self.DB_HOST = DB_HOST
        self.DB_PORT = DB_PORT
        self.USER_NAME = USER_NAME
        self.USER_PASSWORD = USER_PASSWORD
        self.process_VOEvent(voevent)

    def process_VOEvent(self, voevent):
        try:
            self.logger.info("Processing file {}".format(voevent.name))
        except AttributeError:
            self.logger.info("Processing file {}".format(voevent))
        # load mapping VOEvent -> FRBCAT
        mapping = parse_mapping()
        # parse VOEvent xml file
        vo_dict, event_type = self.parse_VOEvent(voevent, mapping)
        # create/delete a new FRBCat entry
        self.update_FRBCat(vo_dict, event_type)

    def get_param(self, param_data, param_group, param_name):
        '''
        Get param data for a given attribute
        '''
        try:
            # return value of the param if defined in the XML
            return param_data.get(param_group).get(param_name).get('value')
        except AttributeError:
            # return None for the ones that are not defined in the XML
            return None

    def get_coord(self, v, coordname):
        try:
            units = getattr(vp.get_event_position(v, index=0), 'units')
        except AttributeError:
            units = None
        try:
            if (units == 'deg') and coordname in ['ra', 'dec']:
                return utils.decdeg2dms(getattr(vp.get_event_position(
                  v, index=0), coordname))
            else:
                return getattr(vp.get_event_position(v, index=0), coordname)
        except AttributeError:
            return None
        except KeyError:
            return None
        except TypeError:
            return None

    def get_coord2(self, v, mapping, idx):
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
            utils.decdeg2dms(vp.get_event_position(v, index=0).ra)
            key = switcher.get(mapping['FRBCAT COLUMN'].iloc[idx])
            if key in ['raj', 'decj', 'ra', 'dec']:
                return utils.decdeg2dms(getattr(
                    vp.get_event_position(v, index=0), key))
            else:
                return getattr(vp.get_event_position(v, index=0), key)
        except AttributeError:
            return None
        except KeyError:
            return None
        except TypeError:
            return None

    def get_attrib(self, v, attribname):
        '''
        Get xml attributes
        '''
        try:
            return v.attrib[attribname]
        except ValueError:
            return None
        except KeyError:
            return None

    def get_utc_time_str(self, v):
        '''
        Get time in UTC
        Return string 'YYYY-MM-DD HH:MM:SS'
        '''
        utctime = vp.get_event_time_as_utc(v, index=0)
        return utctime.strftime("%Y-%m-%d %H:%M:%S")

    def get_value(self, v, param_data, item, event_type):
        itemtype = item.get('type')
        if itemtype == 'ivorn':
            if (event_type[0]=='supersedes'):
                if event_type[1]:
                    # type supersedes with a valid ivorn citation
                    return event_type[1]
                else:
                    # type supersedes with no ivorn citation, use event ivorn
                    return self.get_attrib(v, item.get('name'))
            else:
                return self.get_attrib(v, item.get('name'))
        elif itemtype == 'Param':
            return self.get_param(param_data, item.get('param_group'), item.get('param_name'))
        elif itemtype == 'ISOTime':
            try:
                return self.get_utc_time_str(v)
            except AttributeError:
                # for type 'retraction' there is no time defined
                return None
        elif itemtype == 'XML':
            return vp.dumps(v)
        elif itemtype == 'voevent':
            try:
                return v.xpath('.//' + item.get('voevent').replace('.', '/'))[0]
            except IndexError:
                return None
        elif itemtype == 'Coord':
            return self.get_coord(v, item.get('name'))
        elif itemtype == 'verify':
            # get importance attribute from <Why> section
            importance = v.Why.attrib.get(item.get('name'))
            # for high importance set verified=True, else False
            try:
                if (float(importance) >= 0.95):
                    # high importance, so default to verified
                    return True
                else:
                    return False
            except TypeError:
                return False
        else:
            return None

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
        self.logger.info("Event of of type: {}".format(event_type))
        # use the mapping to get required data from VOEvent xml
        # if a path is not found in the xml it gets an empty list which is
        # removed in the next step
        # puts all params into dict param_data[group][param_name]
        try:
          param_data = vp.get_grouped_params(v)
        except AttributeError:
          # <What> section is not needed for retractions
          param_data = None
        for table in mapping.keys():  # iterate over all tables
            for idx, item in enumerate(mapping[table]):
                # validate item
                # TODO pass item to a validate function to check
                # Add values from XML to dictionary
                mapping[table][idx]['value'] = self.get_value(v, param_data, item, event_type)
        return mapping, event_type

    def update_FRBCat(self, mapping, event_type):
        '''
        Add new FRBCat entry
        '''
        # connect to database
        connection, cursor = dbase.connectToDB(self.DB_NAME, self.USER_NAME,
                                               self.USER_PASSWORD, self.DB_HOST,
                                               self.DB_PORT)
        FRBCat = FRBCat_add(connection, cursor, mapping, event_type[0])
        if event_type[0] in ['new', 'followup', 'supersedes']:
            # for new, followup, supersedes we need to add an entry to FRBCat
            FRBCat.add_VOEvent_to_FRBCat()
        elif event_type[0] in ['retraction']:
            # retract the event
            FRBCat.retract(event_type[1])
