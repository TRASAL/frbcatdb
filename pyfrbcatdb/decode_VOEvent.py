'''
description:    Create a db entry for a VOEvent
license:        APACHE 2.0
author:         Ronald van Haren, NLeSC (r.vanharen@esciencecenter.nl)
'''
import voeventparse as vp
from pyfrbcatdb import dbase
from pyfrbcatdb.FRBCat import FRBCat_add
from pyfrbcatdb.FRBCat import parse_mapping
from pyfrbcatdb.logger import logger
from dateutil import parser
from astropy import units as u
from astropy.coordinates import SkyCoord


class decode_VOEvent(logger):
    '''
    Class to decode a VOEvent file and insert it into the
    FRBCat database.

    :param voevent: filestream or filename
    :param dbName: database name
    :param dbHost: database host
    :param dbPort: database port
    :param dbUser: database user name
    :param dbPassword: database user password
    :param logfile: name of log file
    :type voevent: _io.BufferedReader, str
    :type dbName: str
    :type dbHost: str, NoneType
    :type dbPort: str, NoneType
    :type dbUser: str, NoneType
    :type dbPassword: str, NoneType
    :type logfile: str
    '''
    def __init__(self, voevent, dbName, dbHost, dbPort, dbUser,
                 dbPassword, logfile):
        logger.__init__(self, logfile)
        self.dbName = dbName
        self.dbHost = dbHost
        self.dbPort = dbPort
        self.dbUser = dbUser
        self.dbPassword = dbPassword
        self.process_VOEvent(voevent)

    def process_VOEvent(self, voevent):
        '''
        Main method to process the VOEvent.

        :param voevent: filestream or filename
        :type voevent: _io.BufferedReader, str
        '''
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
        try:
            self.logger.info("Finished file {}".format(voevent.name))
        except AttributeError:
            self.logger.info("Finished file {}".format(voevent))

    @staticmethod
    def get_param(param_data, param_group, param_name):
        '''
        Get param data for a given attribute.

        :param param_data: all param data from VOEvent file
        :param param_group: param group in VOEvent which holds param_name
        :param param_name: name of parameter to get value for
        :type param_data: orderedmultidict.orderedmultidict.omdict
        :type param_group: str
        :type param_name: str
        :returns: param value if defined in VOEvent, else None
        :rtype: str, float, int, NoneType
        '''
        try:
            # return value of the param if defined in the XML
            return param_data.get(param_group).get(param_name).get('value')
        except AttributeError:
            # return None for the ones that are not defined in the XML
            return None

    @staticmethod
    def get_description(v, item):
        '''
        Return description of parameter.

        :param v: VOEvent xml
        :param item: single dictionary item from mapping
        :type v: lxml.objectify.ObjectifiedElement
        :type item: dict
        :returns: Description on parameter is applicable, else None
        :rtype: str, NoneType
        '''
        param_group = item.get('param_group')
        param_name = item.get('param_name')
        try:
            note = v.find(".//Group[@name='{}']".format(param_group)).find(
              ".//Param[@name='{}']".format(param_name)).Description
            if note:
                return "[{}] {}".format(param_name, note)
            else:
                return None
        except AttributeError:
            return None

    @staticmethod
    def get_coord(v, coordname):
        '''
        Get coordinate from VOEvent file.
          - transform to HH:MM:SS if coordname=ra
          - transform to DD:HH:SS if coordname=dec

        :param v: VOEvent xml
        :param coordname: coordinate name ('ra' or 'dec')
        :type v: lxml.objectify.ObjectifiedElement
        :type coordname: str
        :returns: location string in HH:MM:SS.MS for coordname=ra
            or DD:HH:SS.MS for coordname=dec
        :rtype: str
        '''
        try:
            units = getattr(vp.get_event_position(v, index=0), 'units')
        except AttributeError:
            return None
        if not (units == 'deg'):
            raise AttributeError(
                'Unable to determine units for position: {}'.format(
                  vp.get_event_position(v, index=0)))
        position = vp.get_event_position(v, index=0)
        if (position.system == 'UTC-FK5-GEO'):
            skcoord = SkyCoord(ra=position.ra*u.degree,
                               dec=position.dec*u.degree, frame='fk5')
        else:
            # use default reference frame
            skcoord = SkyCoord(ra=position.ra*u.degree,
                               dec=position.dec*u.degree)
        if (coordname == 'ra'):
            # ra location is in hms
            coordloc = skcoord.ra.hms
        elif (coordname == 'dec'):
            # dec location is in dms
            coordloc = skcoord.dec.dms
        # format location tuple to string
        locstring = '{}:{}:{}'.format(
            str(int(round(coordloc[0]))).zfill(2),
            str(abs(int(round(coordloc[1])))).zfill(2),
            "{:.2f}".format(abs(coordloc[2])).zfill(5))
        return locstring

    @staticmethod
    def get_attrib(v, attribname):
        '''
        Get xml attributes.

        :param v: VOEvent xml
        :param attribname: attribute name
        :type v: lxml.objectify.ObjectifiedElement
        :type attribname: str
        :returns: v.attrib[attribname]
        :rtype: str
        '''
        try:
            return v.attrib[attribname]
        except ValueError:
            return None
        except KeyError:
            return None

    @staticmethod
    def get_utc_time_str(v):
        '''
        Get time in UTC.

        :param v: VOEvent xml
        :type v: lxml.objectify.ObjectifiedElement
        :returns: time as string 'YYYY-MM-DD HH:MM:SS.MS'
        :rtype: str
        '''
        utctime = vp.get_event_time_as_utc(v, index=0)
        return utctime.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    def get_value(self, v, param_data, item, event_type):
        '''
        Extract the value of item from VOEvent.

        :param v: VOEvent xml
        :param param_data: all param data from VOEvent file
        :param item: single dictionary item from mapping
        :param event_type: event type of VOEvent, including
            citation if applicable, e.g. ('new', None)
        :type v: lxml.objectify.ObjectifiedElement, str
        :type param_data: orderedmultidict.orderedmultidict.omdict
        :type item: dict
        :type event_type: tuple
        :returns: value for item
        :rtype: int, float, str, bool, NoneType
        '''
        itemtype = item.get('type')
        if itemtype == 'ivorn':
            if (event_type[0] == 'supersedes'):
                if event_type[1]:
                    # type supersedes with a valid ivorn citation
                    return event_type[1]
                else:
                    # type supersedes with no ivorn citation, use event ivorn
                    return self.get_attrib(v, item.get('name'))
            else:
                return self.get_attrib(v, item.get('name'))
        elif itemtype == 'Param':
            return self.get_param(param_data, item.get('param_group'),
                                  item.get('param_name'))
        elif itemtype == 'ISOTime':
            try:
                return self.get_utc_time_str(v)
            except AttributeError:
                # for type 'retraction' there is no time defined
                return None
        elif itemtype == 'authortime':
            try:
                timestr = v.xpath('.//' +
                                  item.get('voevent').replace('.', '/'))[0]
                return parser.parse(str(timestr)).strftime('%Y-%m-%d %H:%M:%S')
            except IndexError:
                return None
        elif itemtype == 'XML':
            return vp.dumps(v)
        elif itemtype == 'voevent':
            try:
                return v.xpath('.//' +
                               item.get('voevent').replace('.', '/'))[0]
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
        Parse VOEvent xml file.

        :param voevent: VOEvent xml file
        :param mapping: mapping from mapping.json
        :type voevent: lxml.objectify.ObjectifiedElement, str
        :type mapping: dict
        :returns:  mapping (mapping from mapping.json with values filled),
            event_type (event_type and citation if applicable)
        :rtype: dict, tuple
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
                # Add values from XML to dictionary
                mapping[table][idx]['value'] = self.get_value(v, param_data,
                                                              item, event_type)
                if item.get('description'):
                    note = self.get_description(v, item)
                    if note:
                        mapping[table][idx]['note'] = note
        return mapping, event_type

    def update_FRBCat(self, mapping, event_type):
        '''
        Add new FRBCat entry. Calls the FRBCat_add class.

        :param mapping: mapping from mapping.json
        :param event_type: event_type and citation if applicable
        :type mapping: dict
        :type event_type: tuple
        '''
        # connect to database
        connection, cursor = dbase.connectToDB(self.dbName,
                                               self.dbUser,
                                               self.dbPassword,
                                               self.dbHost,
                                               self.dbPort)
        FRBCat = FRBCat_add(connection, cursor, mapping, event_type[0])
        if event_type[0] in ['new', 'followup', 'supersedes']:
            # for new, followup, supersedes we need to add an entry to FRBCat
            FRBCat.add_VOEvent_to_FRBCat()
        elif event_type[0] in ['retraction']:
            # retract the event
            FRBCat.retract(event_type[1])
