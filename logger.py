# -*- coding: utf-8 -*-

import os
import sys
import time
import datetime


#############################
# Author: Simon Schmid      #
# Date: 21.05.2019          #
#############################


########
# todo: create __exit__ function oder close() method
# todo: change loglevel name from currloglevel to loglevel or something similar
# todo: print loglevel returns String instead of int
# todo: logfilename aktuell: 11_11_2019.txt > log_PROJECTNAME_YYYYMMDD_HH_MM.txt
# todo .info, .warning, . ...
# todo cant delete default log classes
# todo handle excep as util method
# todo docstrings (!!!)
# todo help function, oder docstrings so ausfürhlich, dass da auch loglevels und so drinstehen
# todo logfile in .log file
# todo loglevel als klasse
# todo total rework for version 4
# todo methoden sollen einfacher werden, add loglevel and remove log level feste eingabewerte, nicht so viel zulassen wie bisher
# todo internal logfilebuffer, weiteres klassenattibut als string buffer der nicht in file geschrieben wird, ohne loglevel
# todo to string weg und sowas nutzen: mydict = {'george':16,'amber':19}
# print(list(mydict.keys())[list(mydict.values()).index(16)]) # Prints george
# siehe: https://stackoverflow.com/questions/8023306/get-key-by-value-in-dictionary
#  ########


#############################
# Documentation:
#    # INPUTS
#        # OPTIONAL logLvl
#            # default: 'ERROR' : 40
#            # Defines which messages are displayed and logged
#            # available ones displayed below, custom ones can be added via the addLogLvl method
#            # can be changed after initialisation with the setlogLvl method
#        # OPTIONAL projectName
#            # default: None
#            # Written in the logFile if defined and if logFile is created
#        # OPTIONAL createLogFile
#            # default: False
#            # if set to True, a logFile .txt is created and saved
#        # OPTIONAL logPath
#            # default: skript directory
#            # place where logFile is saved if one is desired
#        # OPTIONAL addTimeStamp
#            # default: False
#            # enables timestamp in logmessages, helpful for projects with longer runtime
#
#    # METHODS
#        # help()
#        # getLogLvl()
#        # setLogLvl()
#        # addLogLvl()
#        # _removeLogLvl()
#        # __init_log_file()
#        # addToLog()
#
#    # DEFAULT LOG LEVELS:
#        # OFF       :   100
#        # CRITICAL  :   50
#        # ERROR     :   40
#        # WARNING   :   30
#        # INFO      :   20
#        # DEBUG     :   10
#        # ALL       :   0
#        # add more with the addLogLvl method
#############################

# version
__major__ = 4       # for major interface/format changes
__minor__ = 0       # for minor interface/format changes
__release__ = 0     # for tweaks, bug-fixes, or development
__version__ = '%d.%d.%d' % (__major__, __minor__, __release__)
__version_info__ = tuple([int(num) for num in __version__.split('.')])
__author__ = 'Simon Schmid'


MIN_LOG_LEVEL_VALUE = 0
MAX_LOG_LEVEL_VALUE = 100
DEFAULT_LOG_LEVEL = 'INFO'


"""
Hint: 
For more information and a detailed discussion about how and how not to declare singeltons visit:
https://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletonspython

I decided to use the Borg pattern instead because of numerous reasons which can be found in the discussion as well
"""


class Borg:
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state

    def __hash__(self):
        return 1  # hash not really needed but return True if comparing two instances, similar to Java

    def __eq__(self, other):
        try:
            return self.__dict__ is other.__dict__
        except:
            return 0


class LogLevel:
    def __init__(self, name, value):
        """
        Loglevel
        :param name: String, name of log level, will be converted to uppercase
        :param value: Integer, Value representative
        """

        if not isinstance(name, str):
            raise TypeError('Name of log level should be a string!')
        if not isinstance(value, int):
            raise TypeError('Value of log level should be a integer!')

        self.name = name.upper()
        self.value = value

    def __str__(self):
        return "Log Level - Name: {}, Value: {}".format(self.name, self.value)

    def __repr__(self):
        return '\n' + self.__str__() + '\n'


class Logger(Borg):

    def __init__(self, loglvl=DEFAULT_LOG_LEVEL, projectname=None, createlogfile=False, logpath=None, addtimestamp=False, suppressloggernotes=False):
        Borg.__init__(self)  # monostate

        # todo wenn neue instanz erstellt wird, dann werden auch alle attribute wieder von der neuen instanz übernommen auf alle anderen
        # es sollen aber die alten attribute in die neue instanz mitgenommen werden und nicht anders herum
        # immerhin werden attribute wenn nicht geändert auch beibehalten, nur wenn geändert, dann wird die veränderung mitgenommen
        # todo diesen hinweis mit in die help schreiben, bzw in die docstrings beider/der loggerklasse

        self.OFF = LogLevel('OFF', MIN_LOG_LEVEL_VALUE)
        self.DEBUG = LogLevel('DEBUG', 10)
        self.INFO = LogLevel('INFO', 20)
        self.WARNING = LogLevel('WARNING', 30)
        self.ERROR = LogLevel('ERROR', 40)
        self.CRITICAL = LogLevel('CRITICAL', 50)
        self.ALL = LogLevel('ALL', MAX_LOG_LEVEL_VALUE)

        self.suppress_logger_notes = suppressloggernotes  # todo nach unten? eher nicht
        self.current_log_level = None

        result = self.set_log_lvl(loglvl)
        if not result:
            self.set_log_lvl(DEFAULT_LOG_LEVEL)

        # self.createlogfile = createlogfile
        # if self.createlogfile:
        #     self.__logFileCreated = False
        #     self.__logFileBuffer = []
        #     self.logpath = os.path.normpath(os.path.abspath(logpath))
        # self.time_stamp = addtimestamp
        # self.__projectname = projectname  # shown in topLine of logFile
        # self.suppress_logger_notes = suppressloggernotes
        #
        # # set loglvl, save as numeric value
        # self.__defaultLogLvl = self.INFO  # if someone tries initializing without valid log level
        # self.current_log_level = None
        # self.set_log_lvl(loglvl)
        #
        # if '--debug' in sys.argv:
        #     self.set_log_lvl('ALL')
        #     self.add_to_log('INFO', "Enter Debug Mode: Turning all Logmessages on!", desc='Logger')
        #
        # if self.createlogfile:
        #     self.__init_log_file()
        #
        # # would maybe fail before this line but who knows ...
        # if str(sys.version_info[0]) + '.' + str(sys.version_info[1]) != "3.7":
        #     if not self.suppress_logger_notes:
        #         self.add_to_log('WARNING', "Designed for Python 3.7, might fail!", desc='Logger')
        #
        # if not self.suppress_logger_notes:  # todo raus
        #     self.add_to_log('INFO', "Logger ready!", desc='Logger')

    def set_log_lvl(self, loglvl):
        """
        Sets log level to new level
        :param loglvl: String, name of new log level, must be the name of a LogLevel class instance
        :return: Boolean, true if set to new level
        """
        if loglvl not in vars(self) or not isinstance(vars(self)[loglvl], LogLevel):  # nicer approach than invoking __dict__
            self.logger_note('ERROR', "Unknown log level: {}".format(loglvl))
            return False
        self.current_log_level = vars(self)[loglvl]
        self.logger_note('INFO', "Set Log level to {}".format(self.current_log_level.name))
        return True



    def log_level(self):
        """ Returns current log level """
        return self.current_log_level.name, self.current_log_level.value

    def add_log_lvl(self, newloglvl):
        """
        used to add a custom logLvl provided as list with format: ['name', integerValue]
        """
        
        min_index_log_level = 0
        max_index_log_level = 100
        min_length_log_level_name = 1
        max_length_log_level_name = 25
           
        #todo
    
    def _remove_log_lvl(self, delloglvl):
        # todo
        pass

    def __init_log_file(self):
        #todo
        pass

    def handle_excep(self, exception, with_tb=True):
        """ prints exception """
        # todo
        if not self.suppress_logger_notes:
            print("CRITICAL: {}".format(exception))
            if with_tb:  # with traceback
                import traceback
                traceback.print_exc()
                print("")

    def set_all(self):
        """ Sets logger level to ALL level """
        self.current_log_level = self.ALL
        self.logger_note("Set log level to '{}' with value of {}. Displaying all log messages!".format(self.current_log_level.name, self.current_log_level.value))

    def set_debug(self):
        """ Sets logger level to DEBUG level """
        self.current_log_level = self.DEBUG
        self.logger_note("Set log level to '{}' with value of {}".format(self.current_log_level.name, self.current_log_level.value))

    def set_info(self):
        """ Sets logger level to INFO level """
        self.current_log_level = self.INFO
        self.logger_note("Set log level to '{}' with value of {}".format(self.current_log_level.name, self.current_log_level.value))

    def set_warning(self):
        """ Sets logger level to WARNING level """
        self.current_log_level = self.WARNING
        self.logger_note("Set log level to '{}' with value of {}".format(self.current_log_level.name, self.current_log_level.value))

    def set_error(self):
        """ Sets logger level to ERROR level """
        self.current_log_level = self.ERROR
        self.logger_note("Set log level to '{}' with value of {}".format(self.current_log_level.name, self.current_log_level.value))

    def set_critical(self):
        """ Sets logger level to CRITICAL level """
        self.current_log_level = self.CRITICAL
        self.logger_note("Set log level to '{}' with value of {}".format(self.current_log_level.name, self.current_log_level.value))

    def turn_off(self):
        """ Sets logger level to OFF level """
        self.current_log_level = self.OFF
        self.logger_note("Set log level to '{}' with value of {}. So log messages are disabled!".format(self.current_log_level.name, self.current_log_level.value))

    def debug(self):
        pass

    def info(self):
        pass

    def warning(self):
        pass

    def error(self):
        pass

    def critical(self):
        pass

    def logger_note(self, loglevel, message, desc='Logger'):
        """ Used for logger own messages to avoid asking for supress_logger_notes all along the line """
        if not self.suppress_logger_notes:
            self.add_to_log(loglevel, message, desc)

    def add_to_log(self, loglevel, message, desc='', only_to_file=False):
        """
        if lvl (string) is at least the set loglevel message is printed and logged in the logFile if one is created
        """
        
        min_length_message = 1
        max_length_message = 125
        max_desc_length = 25

        print(loglevel + ' | ' + desc + ' | ' + message)

    def __str__(self):
        # todo
        pass

    def __repr__(self):
        return '\n' + self.__str__() + '\n'
