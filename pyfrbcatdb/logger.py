'''
description:    Logging functionality for pyfrbcatdb
license:        APACHE 2.0
author:         Ronald van Haren, NLeSC (r.vanharen@esciencecenter.nl)
'''

import logging
from logging.handlers import RotatingFileHandler


class logger:
    '''
    Logger class.

    :param filename: log filename
    :param DEFAULT_LOG_LEVEL: default log level
    :param DEFAULT_LOG_LEVEL_C: default log level to console
    :type filename: str
    :type DEFAULT_LOG_LEVEL: str
    :type DEFAULT_LOG_LEVEL_C: str
    '''
    def __init__(self, filename, DEFAULT_LOG_LEVEL='debug',
                 DEFAULT_LOG_LEVEL_C='warning'):
        # define global LOG variables
        self.filename = filename
        self.level = DEFAULT_LOG_LEVEL
        self.level_c = DEFAULT_LOG_LEVEL_C
        self.LOG_LEVELS = {'debug': logging.DEBUG,
                           'info': logging.INFO,
                           'warning': logging.WARNING,
                           'error': logging.ERROR,
                           'critical': logging.CRITICAL}
        self.LOG_LEVELS_LIST = self.LOG_LEVELS.keys()
        self.LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
        self.DATE_FORMAT = "%Y/%m/%d/%H:%M:%S"
        self.start_logging()

    def start_logging(self):
        '''
        Start logging with given filename and level.
        '''
        try:
            self.logger
        except AttributeError:
            self.logger = logging.getLogger()
        else:  # wish there was a logger.close()
            for handler in self.logger.handlers[:]:  # make a copy of the list
                self.logger.removeHandler(handler)
        self.logger.setLevel(self.LOG_LEVELS[self.level])
        formatter = logging.Formatter(self.LOG_FORMAT,
                                      datefmt=self.DATE_FORMAT)
        # Define and add file handler
        fh = RotatingFileHandler(self.filename,
                                 maxBytes=(10*1024*1024),
                                 backupCount=7)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        # Define a handler which writes messages level_c or higher to std_err
        console = logging.StreamHandler()
        console.setLevel(self.LOG_LEVELS[self.level_c])
        # set a format which is simpler for console use
        formatter = logging.Formatter(
          '%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        # add the handler to the root logger
        self.logger.addHandler(console)
