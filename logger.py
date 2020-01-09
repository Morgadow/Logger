# -*- coding: utf-8 -*-

import os
import sys
import time
import datetime


#############################
# Author: Simon Schmid      #
# Date: 21.05.2019          #
#############################


# todo add custom log level
# todo remove custom log level
# todo type testing not ok, better raise errors: https://stackoverflow.com/questions/19684434/best-way-to-check-function-arguments-in-python
# todo formatter especially how time is printed, which delim und in welcher reihenfolge die teile kommen
# todo test for other class using borg pattern --> raise runtimeError
# todo logfilename
# todo logfile with full path accepted as input, sets path and filename

# version
__major__ = 4       # for major interface/format changes
__minor__ = 0       # for minor interface/format changes
__release__ = 6     # for tweaks, bug-fixes, or development
__version__ = '%d.%d.%d' % (__major__, __minor__, __release__)
__version_info__ = tuple([int(num) for num in __version__.split('.')])
__author__ = 'Simon Schmid'


##################
# Default logger settings
DEFAULT_LOG_LEVEL = 'INFO'
DEFAULT_PROJECT_NAME = None
DEFAULT_CREATE_LOG_FILE = False
DEFAULT_LOG_PATH = None
DEFAULT_ADD_TIME_STAMP = False
DEFAULT_SUPRESS_LOGGER_NOTES = False

MIN_LOG_LEVEL_VALUE = 0
MAX_LOG_LEVEL_VALUE = 100
MAX_LOG_MESSAGE_LENGTH = 0  # number of characters, 0 for unlimited
##################



class Borg:
    """
    Borg monostate pattern for same logger class in whole project
    Hint:
    For more information and a detailed discussion about how and how not to declare singeltons visit:
    https://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletonspython

    I decided to use the Borg pattern instead because of numerous reasons which can be found in the discussion as well
    """
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


class MetaBorg(type):
    """
    Borg monostate pattern for same logger class in whole project
    Hint:
    This is a different approach corresponding to: https://baites.github.io/computer-science/patterns/2018/06/11/python-borg-and-the-new-metaborg.html

    Using the MetaBorg class skips init of logger/MetaBorg class if a instance already exists. In this case it is possible to use default var values
    for first initialisation.

    """
    _state = {"__skip_init__": False}

    def __call__(cls, *args, **kwargs):
        if cls._state['__skip_init__']:
            cls.__check_args(*args, **kwargs)
        instance = object().__new__(cls, *args, **kwargs)
        instance.__dict__ = cls._state
        if not cls._state['__skip_init__']:
            instance.__init__(*args, **kwargs)
            cls._state['__skip_init__'] = True
        return instance


class LogLevel:
    """ Holding possible log level with name and numeric equivalent """

    def __init__(self, name, value):
        """
        :param name: String, name of log level, will be converted to uppercase
        :param value: Integer, Value representative
        """

        if not isinstance(name, str):
            raise TypeError('Name of log level should be a string!')
        if not isinstance(value, int) or value < 0:
            raise TypeError('Value of log level should be a positive integer!')

        self.name = name.upper()
        self.value = value

    def __str__(self):
        return "Log Level - Name: {}, Value: {}".format(self.name, self.value)

    def __repr__(self):
        return '\n' + self.__str__() + '\n'


class Logger(Borg):
    """
    Logger class with borg monostate pattern, so every instance shares same state throughout whole project.

    In order to be able to use default inputs and to avoid hadling inputs with **kwargs i decided to stick with the Borg
    pattern and to avoid changing settings through default inputs only the first instance sets input skip_init to true,
    every other instance is created with Logger() only!

    Default log levels:
    ALL         : 0
    DEBUG       : 10
    INFO        : 20
    WARNING     : 30
    ERROR       : 40
    CRITICAL    : 50
    OFF         : 100
    """

    # def __init__(self, *args, **kwargs):
    def __init__(self, level=DEFAULT_LOG_LEVEL, projectname=DEFAULT_PROJECT_NAME, createlogfile=DEFAULT_CREATE_LOG_FILE, logpath=DEFAULT_LOG_PATH, addtimestamp=DEFAULT_ADD_TIME_STAMP, suppressloggernotes=DEFAULT_SUPRESS_LOGGER_NOTES):

        Borg.__init__(self)  # monostate pattern
        if not self.__dict__:  # to avoid changing settings with every new instance through default values after one instance is created init will be skipped

            # default possible log levels
            self.ALL = LogLevel('ALL', MIN_LOG_LEVEL_VALUE)
            self.DEBUG = LogLevel('DEBUG', 10)
            self.INFO = LogLevel('INFO', 20)
            self.WARNING = LogLevel('WARNING', 30)
            self.ERROR = LogLevel('ERROR', 40)
            self.CRITICAL = LogLevel('CRITICAL', 50)
            self.OFF = LogLevel('OFF', MAX_LOG_LEVEL_VALUE)

            self.start_time = time.time()

            self.suppress_logger_notes = suppressloggernotes
            self.__log_file_buffer = []
            self.time_stamp = addtimestamp
            self.__project_name = projectname  # shown in top line of logfile and name of logfile

            # create logfile
            self.create_log_file = createlogfile
            self.__log_file_created = False
            if self.create_log_file:
                self.log_path = logpath
                if self.log_path is not None:
                    self.log_path = os.path.normpath(os.path.abspath(logpath))
                self.__log_file_name = None
                self._log_file = None
                self.__log_file_created = self.__init_log_file()

            # eval log level
            self.level = vars(self)[DEFAULT_LOG_LEVEL]  # set initial log level
            if not self.set_level(level):
                self._logger_note('INFO', "Set log level to default log level: " + str(self.level.name))

            # would propably fail before this line but who knows ...
            if str(sys.version_info[0]) + '.' + str(sys.version_info[1]) != "3.7":
                if not self.suppress_logger_notes:
                    self._logger_note('WARNING', "Designed for Python 3.7, might cause problems!")

            # print buffer
            if len(self.__log_file_buffer):
                for message in self.__log_file_buffer:
                    self._logger_note(message[0], message[1])
                self._logger_note('DEBUG', "Printed {} lines of log file buffer".format(len(self.__log_file_buffer)))
                self.__log_file_buffer = []
            self._logger_note('INFO', "Logger ready!")

        else:

            # check if user tried to create instance with different settings, print warning, dont use inputs
            input_found = False # todo change to dict or similar, this is not nice!
            if level.upper() != self.level.name:
                input_found = True
            if projectname != DEFAULT_PROJECT_NAME:
                input_found = True
            if createlogfile != DEFAULT_CREATE_LOG_FILE:
                input_found = True
            if logpath != DEFAULT_LOG_PATH:
                input_found = True
            if addtimestamp != DEFAULT_ADD_TIME_STAMP:
                input_found = True
            if suppressloggernotes != DEFAULT_SUPRESS_LOGGER_NOTES:
                input_found = True

            if input_found:
                self._logger_note('WARNING', "Attempt to create an instance with changed settings, but a borg version already exists. Inputs will be ignored!")

    def set_level(self, log_level):
        """
        Sets log level to new level
        :param log_level: String, name of new log level, must be the name of a LogLevel class instance
        :return: Boolean, true if set to new level
        """
        try:
            if not isinstance(log_level, str) or log_level.upper() not in vars(self) or not isinstance(vars(self)[log_level.upper()], LogLevel):  # nicer approach than invoking __dict__
                self._logger_note('ERROR', "Unknown log level: '{}'".format(log_level))
                return False
            self.level = vars(self)[log_level.upper()]
            self._logger_note('INFO', "Set Log level to '{}'".format(self.level.name))
            return True
        except Exception as e:
            self.__handle_excep(e)
            return False

    def get_level(self):
        """ Returns current log level """
        return self.level.name, self.level.value

    def __init_log_file(self):
        """
        Initializes log file, as logpath default is skriptpath + 'logs', filename is generated based on project name, time and date
        :return: Boolean, True if file is generated sucessfully
        """
        try:
            if self.log_path is None:  # then take default path:
                self.log_path = os.path.normpath(os.path.join(os.getcwd(), 'logs'))
                if not os.path.exists(self.log_path):
                    os.mkdir(self.log_path)  # create folder if not existing
                    if os.path.exists(self.log_path):
                        self.__log_file_buffer.append(('DEBUG', "Created folder 'logs' at '{}'".format(os.getcwd())))
                    else:
                        self.create_log_file = False
                        self.__log_file_buffer.append(('ERROR', "Could not create folder 'logs' at '{}'. Will not create a log file!".format(os.getcwd())))
                        return False

            else:  # create all subfolders needed
                delim = '\\'
                sub_folder_list = self.log_path.split(delim)
                for folder in range(len(sub_folder_list)):
                    if not os.path.exists(os.path.normpath(delim.join(sub_folder_list[:folder + 1]))):
                        os.mkdir(os.path.normpath(delim.join(sub_folder_list[:folder + 1])))
                        if os.path.exists(os.path.normpath(delim.join(sub_folder_list[:folder + 1]))):
                            self.__log_file_buffer.append(('DEBUG', "Created folder: '{}' at: '{}'".format(sub_folder_list[folder], delim.join(sub_folder_list[:folder]))))
                        else:
                            self.create_log_file = False
                            self.__log_file_buffer.append(('ERROR', "Could not create folder '{}' at '{}'! Will not create log file!".format(sub_folder_list[folder], delim.join(sub_folder_list[:folder]))))
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
            self.__log_file_buffer.append(('DEBUG', "Final log file name: {}".format(self.__log_file_name)))

            # init logfile
            with open(os.path.join(self.log_path, self.__log_file_name), 'w+') as log_file:
                if self.__project_name is not None:
                    log_file.write('---------------- {} - Log File vom {} um {} Uhr ----------------\n\n'.format(self.__project_name, now.strftime("%d-%m-%Y"), now.strftime("%H:%M")))
                else:
                    log_file.write('---------------- Log File vom {} um {} Uhr ----------------\n\n'.format(now.strftime("%d-%m-%Y"), now.strftime("%H:%M")))

            if not os.path.isfile(os.path.join(self.log_path, self.__log_file_name)):  # could not create file
                self.create_log_file = False
                self.__log_file_buffer.append(('ERROR', "Could not create log file! Logger will not create any log file!"))
                return False
            else:
                self.__log_file_buffer.append(('INFO', "Created log file '{}' at '{}'".format(self.__log_file_name, self.log_path)))
                self._log_file = os.path.join(self.log_path, self.__log_file_name)

            return True

        except Exception as e:
            self.create_log_file = False
            self.__handle_excep(e)
            return False

    def __handle_excep(self, exception, with_tb=True):
        """ prints exception """
        if not self.suppress_logger_notes:
            try:
                self._logger_note('CRITICAL', "{}".format(exception), desc='Logger')
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
        self.level = self.ALL
        # self.logger_note('INFO', "Set log level to '{}' with value of {}. Displaying all log messages!".format(self.level.name, self.level.value), desc='Logger')
        self._logger_note('INFO', "Set log level to '{}'. Displaying all log messages!".format(self.level.name))

    def set_debug(self):
        """ Sets logger level to DEBUG level """
        self.level = self.DEBUG
        # self.logger_note('INFO', "Set log level to '{}' with value of {}".format(self.level.name, self.level.value), desc='Logger')
        self._logger_note('INFO', "Set log level to '{}'".format(self.level.name))

    def set_info(self):
        """ Sets logger level to INFO level """
        self.level = self.INFO
        # self.logger_note('INFO', "Set log level to '{}' with value of {}".format(self.level.name, self.level.value), desc='Logger')
        self._logger_note('INFO', "Set log level to '{}'".format(self.level.name))

    def set_warning(self):
        """ Sets logger level to WARNING level """
        self.level = self.WARNING
        # self.logger_note('INFO', "Set log level to '{}' with value of {}".format(self.level.name, self.level.value), desc='Logger')
        self._logger_note('INFO', "Set log level to '{}'".format(self.level.name))

    def set_error(self):
        """ Sets logger level to ERROR level """
        self.level = self.ERROR
        # self.logger_note('INFO', "Set log level to '{}' with value of {}".format(self.level.name, self.level.value), desc='Logger')
        self._logger_note('INFO', "Set log level to '{}'".format(self.level.name))

    def set_critical(self):
        """ Sets logger level to CRITICAL level """
        self.level = self.CRITICAL
        # self.logger_note('INFO', "Set log level to '{}' with value of {}".format(self.level.name, self.level.value), desc='Logger')
        self._logger_note('INFO', "Set log level to '{}'".format(self.level.name))

    def turn_off(self):
        """ Sets logger level to OFF level """
        self.level = self.OFF
        # self.logger_note('INFO', "Set log level to '{}' with value of {}".format(self.level.name, self.level.value), desc='Logger')
        self._logger_note('INFO', "Set log level to '{}'. All log messages are disabled".format(self.level.name))

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

    def _logger_note(self, log_level, message, desc='Logger'):
        """
        Used for logger own messages to avoid asking for supress_logger_notes all along the line
        :param log_level: String, name of loglevel, decides if message is printed and saved
        :param message: String, message to print
        :param desc: String, small description to mark what type of message, default: 'Logger'
        :return: None
        """
        if not self.suppress_logger_notes:
            self.add_to_log(log_level, message, desc)

    def add_to_log(self, log_level, message, desc='', only_to_file=False):
        """
        Prints to screen and saves in log file
        :param log_level: String, name of loglevel, decides if message is printed and saved
        :param message: String, message to print
        :param desc: String, small description to mark what type of message, default: 'Logger'
        :param only_to_file: Boolean, prints only to file if True
        :return: None
        """

        # todo handler if message not utf-8 encoded

        if not isinstance(log_level, str) or log_level.upper() not in vars(self) or not isinstance(vars(self)[log_level.upper()], LogLevel):  # nicer approach than invoking __dict__
            self._logger_note('ERROR', "Unknown log level: {}".format(log_level))
            return

        if vars(self)[log_level.upper()].value < self.level.value:  # if loglevel not high enough
            return

        if MAX_LOG_MESSAGE_LENGTH != 0 and len(str(message)) > MAX_LOG_MESSAGE_LENGTH:
            message = message[:100]
            self._logger_note('DEBUG', "Log message exceeded maximum length of {} characters and was shorted".format(MAX_LOG_MESSAGE_LENGTH))

        # create log message
        delim = ' | '
        timestamp = ''
        if self.time_stamp:
            now = datetime.datetime.now()
            timestamp = now.strftime('%d.%m.%Y') + ' ' + now.strftime('%H:%M') + delim
        if not str(desc) == '' and str(desc)[-(len(delim)):] != delim:  # second part especially needed when printing logFileBuffer
            desc = str(desc) + delim
        log_message = timestamp + log_level + delim + desc + str(message)

        if not only_to_file:
            print(log_message)
        if self.create_log_file and self.__log_file_created:
            try:
                with open(self._log_file, 'a') as log_file:
                    log_file.write(log_message + '\n')
            except Exception as e:
                self.__handle_excep(e)

    def __str__(self):
        # todo
        return "Logger with settings: {}".format(self.__dict__)

    def __repr__(self):
        return '\n' + self.__str__() + '\n'
