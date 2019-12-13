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
# todo: logfilename aktuell: 11_11_2019.log > log_PROJECTNAME_YYYYMMDD_HH_MM.log
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

    def __init__(self, loglvl=DEFAULT_LOG_LEVEL, projectname=None, createlogfile=False, logpath=None, addtimestamp=False, suppress_logger_notes=False):
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

        self.suppress_logger_notes = suppress_logger_notes
        self.__project_name = projectname  # shown in topLine of logFile
        self.time_stamp = addtimestamp

        self.current_log_level = None  # set log level
        result = self.set_log_lvl(loglvl)
        if not result:
            self.current_log_level = vars(self)[DEFAULT_LOG_LEVEL]
            self.logger_note('INFO', "Set log level to default log level: " + str(self.current_log_level.name))

        self.create_log_file = createlogfile
        if self.create_log_file:
            self.__log_file_created = False
            self.__log_file_name = None
            self.__log_file_buffer = []
            self.log_path = os.path.normpath(os.path.abspath(logpath))
            self.__init_log_file()

        # would maybe fail before this line but who knows ...
        if str(sys.version_info[0]) + '.' + str(sys.version_info[1]) != "3.7":
            if not self.suppress_logger_notes:
                self.add_to_log('WARNING', "Designed for Python 3.7, might fail!", desc='Logger')

        self.logger_note('INFO', "Logger ready!", desc='Logger')

    def set_log_lvl(self, log_level):
        """
        Sets log level to new level
        :param log_level: String, name of new log level, must be the name of a LogLevel class instance
        :return: Boolean, true if set to new level
        """
        try:
            if not isinstance(log_level, str) or log_level.upper() not in vars(self) or not isinstance(vars(self)[log_level.upper()], LogLevel):  # nicer approach than invoking __dict__
                self.logger_note('ERROR', "Unknown log level: {}".format(log_level))
                return False
            self.current_log_level = vars(self)[log_level.upper()]
            self.logger_note('INFO', "Set Log level to {}".format(self.current_log_level.name))
            return True
        except Exception as e:
            self.__handle_excep(e)
            return False

    def get_log_level(self):
        """ Returns current log level """
        return self.current_log_level.name, self.current_log_level.value

    def __init_log_file(self):
        try:
            if self.log_path is None:  # then take default path: skriptpath + 'logs'
                self.log_path = os.path.normpath(os.path.join(os.getcwd(), 'logs'))
                if not os.path.exists(self.log_path):
                    os.mkdir(self.log_path)  # create folder if not existing
                    if os.path.exists(self.log_path):
                        self.logger_note('DEBUG', "Created folder 'logs' at '{}'".format(os.getcwd()))
                    else:
                        self.create_log_file = False
                        self.logger_note('ERROR', "Could not create folder 'logs' at '{}'. Will not create a log file!".format(os.getcwd()))
                        return False

            else:  # create all subfolders needed
                delim = '\\'
                sub_folder_list = self.log_path.split(delim)
                for folder in range(len(sub_folder_list)):
                    if not os.path.exists(os.path.normpath(delim.join(sub_folder_list[:folder + 1]))):
                        os.mkdir(os.path.normpath(delim.join(sub_folder_list[:folder + 1])))
                        if os.path.exists(os.path.normpath(delim.join(sub_folder_list[:folder + 1]))):
                            self.logger_note('DEBUG', "Created folder: '{}' at: '{}'".format(sub_folder_list[folder], delim.join(sub_folder_list[:folder])))
                        else:
                            self.create_log_file = False
                            self.logger_note('ERROR', "Could not create folder '{}' at '{}'! Will not create log file!".format(sub_folder_list[folder], delim.join(sub_folder_list[:folder])))
                            return False

            # evaluate __log_file_name
            now = datetime.datetime.now()
            if self.__project_name is not None:
                self.__log_file_name = self.__project_name + '_' + now.strftime("%d-%m-%Y") + '.log'
            else:
                self.__log_file_name = now.strftime("%d-%m-%Y") + '.log'
            if self.__log_file_name in os.listdir(self.log_path):  # if file with name already exists add '_X' and count X until not existing
                counter = 1
                while True:
                    if self.__project_name is not None:
                        self.__log_file_name = self.__project_name + '_' + now.strftime("%d-%m-%Y") + '_' + str(counter) + '.log'
                    else:
                        self.__log_file_name = now.strftime("%d-%m-%Y") + '_' + str(counter) + '.log'
                    if self.__log_file_name in os.listdir(self.log_path):
                        counter += 1
                    else:
                        break

            # init logfile
            with open(os.path.join(self.log_path, self.__log_file_name), 'w+') as log_file:
                if self.__project_name is not None:
                    log_file.write('---------------- {} - Log File vom {} um {} Uhr ----------------\n\n'.format(self.__project_name, now.strftime("%d-%m-%Y"), now.strftime("%H:%M")))
                else:
                    log_file.write('---------------- Log File vom {} um {} Uhr ----------------\n\n'.format(
                        now.strftime("%d-%m-%Y"), now.strftime("%H:%M")))

            if not os.path.isfile(os.path.join(self.log_path, self.__log_file_name)):  # could not create file
                self.create_log_file = False
                self.logger_note('ERROR', "Could not create log file! Logger will not create any log file!")
                return False
            else:
                self.logger_note('INFO', "Created log file '{}' at '{}'!".format(self.__log_file_name, self.log_path))
                self.__log_file_created = True

            # print buffer
            if self.__log_file_created and len(self.__logFileBuffer) > 0:
                for message in self.__logFileBuffer:
                    self.add_to_log(message[0], message[1], desc=message[2], onlytofile=True)
                self.__logFileBuffer = []

            return True

        except Exception as e:
            self.create_log_file = False
            self.__handle_excep(e)
            return False

    def __handle_excep(self, exception, with_tb=True):
        """ prints exception """
        if not self.suppress_logger_notes:
            try:
                self.logger_note('CRITICAL', "{}".format(exception), desc='Logger')
                if with_tb:  # with traceback
                    import traceback
                    traceback.print_exc()
                    print("")
            except Exception as e:
                print(e)
                if with_tb:  # with traceback
                    import traceback
                    traceback.print_exc()
                    print("")

    def set_all(self):
        """ Sets logger level to ALL level """
        self.current_log_level = self.ALL
        self.logger_note('INFO', "Set log level to '{}' with value of {}. Displaying all log messages!".format(self.current_log_level.name, self.current_log_level.value), desc='Logger')

    def set_debug(self):
        """ Sets logger level to DEBUG level """
        self.current_log_level = self.DEBUG
        self.logger_note('INFO', "Set log level to '{}' with value of {}".format(self.current_log_level.name, self.current_log_level.value), desc='Logger')

    def set_info(self):
        """ Sets logger level to INFO level """
        self.current_log_level = self.INFO
        self.logger_note('INFO', "Set log level to '{}' with value of {}".format(self.current_log_level.name, self.current_log_level.value), desc='Logger')

    def set_warning(self):
        """ Sets logger level to WARNING level """
        self.current_log_level = self.WARNING
        self.logger_note('INFO', "Set log level to '{}' with value of {}".format(self.current_log_level.name, self.current_log_level.value), desc='Logger')

    def set_error(self):
        """ Sets logger level to ERROR level """
        self.current_log_level = self.ERROR
        self.logger_note('INFO', "Set log level to '{}' with value of {}".format(self.current_log_level.name, self.current_log_level.value), desc='Logger')

    def set_critical(self):
        """ Sets logger level to CRITICAL level """
        self.current_log_level = self.CRITICAL
        self.logger_note('INFO', "Set log level to '{}' with value of {}".format(self.current_log_level.name, self.current_log_level.value), desc='Logger')

    def turn_off(self):
        """ Sets logger level to OFF level """
        self.current_log_level = self.OFF
        self.logger_note('INFO', "Set log level to '{}' with value of {}. All log messages are disabled!".format(self.current_log_level.name, self.current_log_level.value), desc='Logger')

    def debug(self, message, desc=''):
        self.add_to_log('DEBUG', message, desc)

    def info(self, message, desc=''):
        self.add_to_log('INFO', message, desc)

    def warning(self, message, desc=''):
        self.add_to_log('WARNING', message, desc)

    def error(self, message, desc=''):
        self.add_to_log('ERROR', message, desc)

    def critical(self, message, desc=''):
        self.add_to_log('CRITICAL', message, desc)

    def logger_note(self, log_level, message, desc='Logger'):
        """ Used for logger own messages to avoid asking for supress_logger_notes all along the line """
        if not self.suppress_logger_notes:
            self.add_to_log(log_level, message, desc)

    def add_to_log(self, log_level, message, desc='', only_to_file=False):

        if not isinstance(log_level, str) or log_level.upper() not in vars(self) or not isinstance(vars(self)[log_level.upper()], LogLevel):  # nicer approach than invoking __dict__
            self.logger_note('ERROR', "Unknown log level: {}".format(log_level))
            return False

        if vars(self)[log_level.upper()].value < self.current_log_level.value:  # if loglevel not high enough
            return

        # create log message
        timestamp = ''
        if self.time_stamp:
            now = datetime.datetime.now()
            timestamp = now.strftime('%d.%m.%Y') + ' ' + now.strftime('%H:%M') + ' | '
        if not str(desc) == '' and str(desc)[-3:] != ' | ':  # second part especially needed when printing logFileBuffer
            desc = str(desc) + ' | '

        print(timestamp + log_level + ' | ' + desc + str(message))
        # todo print to file

    def __str__(self):
        # todo
        pass

    def __repr__(self):
        return '\n' + self.__str__() + '\n'
