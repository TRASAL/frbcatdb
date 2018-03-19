'''
description:    Create a db entry for a VOEvent
license:        APACHE 2.0
author:         Ronald van Haren, NLeSC (r.vanharen@esciencecenter.nl)
'''
from pyfrbcatdb.logger import logger
from pyfrbcatdb import dbase
import shutil
import os


class writeCSV(logger):
    '''
    Class module that write the FRBCat database to a CSV file

    :param CSV: CSV filename
    :param dbName: database name
    :param dbHost: database host
    :param dbPort: database port
    :param dbUser: database user name
    :param dbPassword: database user password
    :param logfile: name of log file
    :type CSV: str
    :type dbName: str
    :type dbHost: str, NoneType
    :type dbPort: str, NoneType
    :type dbUser: str, NoneType
    :type dbPassword: str, NoneType
    :type logfile: str
    '''

    def __init__(self, CSV, dbName, dbHost, dbPort, dbUser,
                 dbPassword, logfile):
        logger.__init__(self, logfile)
        self.dbName = dbName
        self.dbHost = dbHost
        self.dbPort = dbPort
        self.dbUser = dbUser
        self.dbPassword = dbPassword
        self.CSV = CSV
        self.writeToCSV()

    def writeToCSV(self):
        '''
        Dump database to CSV file
        '''
        connection, cursor = dbase.connectToDB(self.dbName,
                                               self.dbUser,
                                               self.dbPassword,
                                               self.dbHost,
                                               self.dbPort)
        # get the SQL statement to write database to CSV
        sql = self.defineSQLStatement()
        # open output file and write CSV file to it
        tmpfile = self.CSV + '.tmp'
        bakfile = self.CSV + '.bak'
        try:
            with open(tmpfile, 'w') as csvfile:
                cursor.copy_expert(sql, csvfile)
            # rename original CSV file to .bak
            try:
                shutil.move(self.CSV, bakfile)
            except FileNotFoundError:
                self.logger.debug("No existing CSV file to " +
                                  "backup: {}".format(self.CSV))
            # remove original CSV file if exists
            try:
                os.remove(self.CSV)
            except OSError:
                pass
            # rename tmpfile to original file
            shutil.move(tmpfile, self.CSV)
            # cleanup
            try:
                os.remove(bakfile)
            except OSError:
                pass
            self.logger.info("Succesfully written database to " +
                             "CSV file: {}".format(self.CSV))
        except (FileNotFoundError, PermissionError):
            self.logger.error("Failed to write database to " +
                              "CSV file: {}".format(self.CSV))
        # close db connection
        dbase.closeDBConnection(connection, cursor)

    def defineSQLStatement(self):
        '''
        Define SQL statement for creating CSV file
        '''
        sql = """COPY (SELECT f.name as FRB,
                o.telescope as telescope,
                to_char(o.utc, 'YYYY/MM/DD HH24:MI:SS.MS') as UTC,
                rop.raj as RAJ, rop.decj as DECJ,
                rop.gl as gl, rop.gb as gb,
                rop.receiver as receiver,
                rop.backend as backend,
                rop.beam_semi_major_axis as beam_semi_major_axis,
                rop.beam_semi_minor_axis as beam_semi_minor_axis,
                rop.beam_rotation_angle as beam_rotation_angle,
                rop.beam as beam,
                rop.sampling_time as sampling_time,
                rop.bandwidth as bandwidth,
                rop.centre_frequency as centre_frequency,
                rop.npol as npol,
                rop.bits_per_sample as bits_per_sample,
                rop.gain as gain,
                rop.tsys as tsys,
                rop.mw_dm_limit as mw_dm_limit,
                rop.galactic_electron_model as galactic_electron_model,
                rmp.voevent_ivorn as voevent_ivorn,
                rmp.dm as dm,
                rmp.dm_error as dm_error,
                rmp.dm_index as dm_index,
                rmp.snr as snr,
                regexp_replace(rmp.width::text,'-1','') as width,
                rmp.rank as rank,
                rmp.width_error_upper as width_error_upper,
                rmp.width_error_lower as width_error_lower,
                rmp.flux as flux,
                rmp.flux_error_upper as flux_error_upper,
                rmp.flux_error_lower as flux_error_lower,
                rmp.rm as rm,
                rmp.rm_error as rm_error,
                rmp.redshift_host as redshift_host,
                rmp.dispersion_smearing as dispersion_smearing,
                rmp.scattering_model as scattering_model,
                rmp.scattering_timescale as scattering_timescale,
                rmp.scattering as scattering,
                rmp.scattering_error as scattering_error,
                rmp.scattering_index as scattering_index,
                rmp.scattering_index_error as scattering_index_error,
                rmp.linear_poln_frac as linear_poln_frac,
                rmp.linear_poln_frac_error as linear_poln_frac_error,
                rmp.circular_poln_frac as circular_poln_frac,
                rmp.circular_poln_frac_error as circular_poln_frac_error,
                rmp.spectral_index as spectral_index,
                rmp.spectral_index_error as spectral_index_error
                FROM frbs f JOIN observations o ON (f.id = o.frb_id)
                JOIN radio_observations_params rop ON (o.id = rop.obs_id)
                JOIN radio_measured_params rmp ON (rop.id = rmp.rop_id)
                JOIN authors armp ON (rmp.author_id = armp.id)
                WHERE (f.private = FALSE AND o.verified = TRUE AND
                 o.detected = TRUE)
                ORDER BY f.name, o.utc)
                TO STDOUT DELIMITER ',' CSV HEADER"""
        return sql
