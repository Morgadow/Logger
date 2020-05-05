# -*- coding: utf-8 -*-

import os
import sys
import time
import datetime


#############################
# Author: Simon Schmid      #
# Date: 21.05.2019          #
#############################

# todo test dauer static_debug vs debug

# todo add custom log level
# todo remove custom log level

# todo formatter especially how time is printed, which delim und in welcher reihenfolge die teile kommen, delim als input
# todo test for other class using borg pattern --> raise runtimeError --> keine lösung gefunden wie das gehen soll
# todo handler log file removed while progress

# todo startlogfile handler --> file removed, no file
# todo append mode wenn logfile exist aber fix path given
# todo delete project name  --> nur noch project header
# todo delete split_string
# todo raus: projectname, log_file_name

"""
NOTE: Written in Python 3.7.1
"""

# version
__major__ = 4       # for major interface/format changes
__minor__ = 3       # for minor interface/format changes
__release__ = 1     # for tweaks, bug-fixes, or development
__version__ = '%d.%d.%d' % (__major__, __minor__, __release__)
__version_info__ = tuple([int(num) for num in __version__.split('.')])
__author__ = 'Simon Schmid'
__date__ = '21.05.2019'


##################
# Default logger settings
DEFAULT_LOG_LEVEL = 'INFO'

MIN_LOG_LEVEL_VALUE = 0
MAX_LOG_LEVEL_VALUE = 100
MAX_LOG_MESSAGE_LENGTH = 0  # maximum number of characters, 0 for unlimited length, can't be less than 75
MAX_LENGTH_LOGFILE_NAME = 75  # maximum length of new logfilename in method rename_logfile
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


# class MetaBorg(type):
#     """
#     Borg monostate pattern for same logger class in whole project
#     Hint:
#     This is a different approach corresponding to: https://baites.github.io/computer-science/patterns/2018/06/11/python-borg-and-the-new-metaborg.html
#
#     Using the MetaBorg class skips init of logger/MetaBorg class if a instance already exists. In this case it is possible to use default var values
#     for first initialisation.
#
#     """
#     _state = {"__skip_init__": False}
#
#     def __call__(cls, *args, **kwargs):
#         if cls._state['__skip_init__']:
#             cls.__check_args(*args, **kwargs)
#         instance = object().__new__(cls, *args, **kwargs)
#         instance.__dict__ = cls._state
#         if not cls._state['__skip_init__']:
#             instance.__init__(*args, **kwargs)
#             cls._state['__skip_init__'] = True
#         return instance


# class SettingsGroup:
#     """ Some Dummy class for grouping settings """
#
#     def __str__(self):
#         str_eq = ''
#         for elem in self.__dict__:
#             str_eq = str_eq + elem + ': ' + str(self.__dict__[elem]) + '\n'
#         return str_eq
#
#     def __repr__(self):
#         return '\n' + str(self.__str__()) + '\n'


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
            raise TypeError('Value of log level must be a positive integer!')

        self.name = name.upper()
        self.value = value

    def __str__(self):
        return "Log Level - Name: {}, Value: {}".format(self.name, self.value)

    def __repr__(self):
        return '\n' + self.__str__() + '\n'


def create_path(path, delim='\\'):
    """
    Creates path with all subfolders needed, raises RuntimeError
    :param path: Path, path to create
    :param delim: String, delimiter for path to split at
    :return:
    """
    sub_folder = path.split(delim)
    for folder in range(len(sub_folder)):
        if not os.path.exists(os.path.normpath(delim.join(sub_folder[:folder + 1]))):
            os.mkdir(os.path.normpath(delim.join(sub_folder[:folder + 1])))
            if os.path.exists(os.path.normpath(delim.join(sub_folder[:folder + 1]))):
                static_debug("Created folder: '{}' at: '{}'".format(sub_folder[folder], delim.join(sub_folder[:folder])))
            else:
                raise RuntimeError("Could not create folder '{}' at '{}'!".format(sub_folder[folder], delim.join(sub_folder[:folder])))

# Standard loglevels
ALL = LogLevel('ALL', MIN_LOG_LEVEL_VALUE)
DEBUG = LogLevel('DEBUG', 10)
INFO = LogLevel('INFO', 20)
WARNING = LogLevel('WARNING', 30)
ERROR = LogLevel('ERROR', 40)
CRITICAL = LogLevel('CRITICAL', 50)
OFF = LogLevel('OFF', MAX_LOG_LEVEL_VALUE)


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

    def __init__(self, level=DEFAULT_LOG_LEVEL, project=None, createlogfile=False, logfile=None, logpath=None, addtimestamp=False, suppressloggernotes=False):
        """ Only creates instance with new settings if no instance was created in session, settings are stored in Borg superclass """

        Borg.__init__(self)  # initiate monostate pattern
        if not self.__dict__:  # to avoid changing settings with every new instance through default values after one instance is created init will be skipped

            self.__init_state = True  # until init is finished all notes are written into logfilebuffer and wont be printed directly
            self.__log_file_buffer = []   # buffer for messages while initstate
            self.start_time = time.time()
            self._suppress_logger_notes = suppressloggernotes

            # default possible log levels
            self.ALL = ALL
            self.DEBUG = DEBUG
            self.INFO = INFO
            self.WARNING = WARNING
            self.ERROR = ERROR
            self.CRITICAL = CRITICAL
            self.OFF = OFF

            # eval log level
            self.level = None
            self.set_level(level)

            # create logfile
            self.log_file, self.log_path = None, None
            if logfile is not None:  # overwrites createlogfile input
                if logpath is not None or not createlogfile:
                    self._logger_note(WARNING, "Input 'createlogfile' and 'logpath' overwritten by 'logfile'!")
                if os.path.isfile(logfile):  # first priority input, append mode if needed
                    self.log_file = os.path.normpath(logfile)
                    self.log_path = os.path.normpath(os.path.dirname(self.log_file))
                    if os.path.splitext(self.log_file)[1] not in ('.txt', '.log'):
                        self._logger_note(WARNING, "Expected logfile extension to be .txt or .log, got {}".format(os.path.splitext(self.log_file)[1]))
                    self._eval_file_header(project, self.log_file)
                else:
                    self.log_file = os.path.normpath(logfile)
                    self.log_path = os.path.normpath(os.path.dirname(self.log_file))
                    create_path(self.log_path)
                    self._eval_file_header(project, self.log_file)

            else:  # eval name and path, create new file
                if createlogfile:
                    if logpath is None:
                        self.log_path = os.path.join(os.getcwd(), 'logs')
                    else:
                        self.log_path = os.path.normpath(logpath)
                    create_path(self.log_path)
                    self.log_file = os.path.join(self.log_path, self._eval_file_name(self.log_path))
                    create_path(self.log_path)
                    self._eval_file_header(project, self.log_file)

            # logmessage format
            self.time_stamp = addtimestamp  # todo nach formatter verschieben und dann als privae machen
            # self.formatter()
            # self._format = SettingsGroup()  # todo rework with formatter integration
            # self._format = self.formatter()

            # print buffer
            self.__init_state = False
            if len(self.__log_file_buffer):
                for message in self.__log_file_buffer:
                    self._logger_note(message[0], message[1])
                self._logger_note(DEBUG, "Printed {} lines of log file buffer".format(len(self.__log_file_buffer)))
                self.__log_file_buffer = []
            self._logger_note(INFO, "Logger ready!")

    def set_level(self, new_level):
        """
        Sets log level to instance of LogLevel, failing throws ValueError
        :param new_level: LogLevel, new log level
        :return: Boolean, true if set to new level
        """
        if isinstance(new_level, LogLevel):  # input instance of LogLevel, probably standard level
            self.level = new_level
            self._logger_note(INFO, "Set Log level to: '{}'".format(self.level.name))
            return

        if not isinstance(new_level, str) or new_level.upper() not in vars(self) or not isinstance(vars(self)[new_level.upper()], LogLevel):  # nicer approach than invoking __dict__
            if self.__init_state:  # would throw another exepction
                self.level = vars(self)[DEFAULT_LOG_LEVEL]
            raise ValueError("Unknown log level: '{}'".format(new_level))

        # set new level
        self.level = vars(self)[new_level.upper()]
        self._logger_note(INFO, "Set Log level to: '{}'".format(self.level.name))

    def get_level(self):
        """ Returns current log level [String loglevel, Integer loglevel int equivalent]"""
        return self.level.name, self.level.value

    def _eval_file_header(self, project=None, file=None):
        """
        Creates header for log file
        :param project: String, name of project for first line in header
        :param file: Path, logfile header gets appended to, creates file if not found
        :return: String, log file header
        """
        now = datetime.datetime.now()
        if project is None:
            header = "---------------- Log File vom {} um {} Uhr ----------------\n\n".format(now.strftime("%d-%m-%Y"), now.strftime("%H:%M"))
        else:
            header = "---------------- {} - Log File vom {} um {} Uhr ----------------\n\n".format(project, now.strftime("%d-%m-%Y"), now.strftime("%H:%M"))
        print(header)
        if file is not None:
            if os.path.exists(file):
                with open(file, 'a') as logfile:
                    logfile.write('\n' + header)
            else:
                with open(file, 'w+') as logfile:
                    logfile.write(header)
                if os.path.isfile(file):
                    self._logger_note(INFO, "Created log file '{}' at '{}'".format(self.log_file.split('\\')[-1], os.path.dirname(self.log_file)))
        return header

    def _eval_file_name(self, folder, ext='.log'):
        """
        Evals log file name, current time and date, adds counter if exists
        :param folder: Path, containing folder
        :param ext: String, file extension, should be .txt or .log
        :return: String, filename
        """
        now = datetime.datetime.now()

        file_name = now.strftime("%d-%m-%Y") + ext
        counter = 1
        while file_name in os.listdir(folder):
            file_name = now.strftime("%d-%m-%Y") + '_' + str(counter) + ext
            counter += 1
        return file_name

    def rename_logfile(self, new_name, logfile_ext='.log', char_restiction=True):
        """
        Renames log file
        :param new_name: String, new name with a maximum length defined in MAX_LENGTH_LOGFILE_NAME
        :param logfile_ext: String, Optional log file extension, should be '.log'
        :param char_restiction: Boolean, if true restricts use of chars forbidden in windows filenames
        :return: None
        """
        if not isinstance(new_name, str) or len(new_name) > MAX_LENGTH_LOGFILE_NAME:
            raise ValueError("New logfile name must be a string with a maximum length of {}".format(MAX_LENGTH_LOGFILE_NAME))
        forbidden_chars = set("\\:'´`\"$§&/=")
        if char_restiction and any((c in forbidden_chars) for c in new_name):
            raise ValueError("Forbidden character in log file name: '{}'".format(new_name))

        # check given file extension
        try:
            if os.path.splitext(new_name)[1] not in ('.log', '.txt'):
                self._logger_note(WARNING, "Expected logfile extension to be .txt or .log, got {}".format(os.path.splitext(new_name)[1]))

            if os.path.exists(os.path.join(self.log_path, new_name)):
                self._logger_note(ERROR, "File '{}' already exists in directory! Can't rename logfile!".format(new_name))
                return

            # if file with this name already exists, count '_X'
            # if os.path.isfile(os.path.join(self.log_path, new_name)):
            #     counter = 1
            #     new_name = '.'.join(new_name.split('.')[:len(new_name.split('.')) - 1]) + '_' + str(counter) + logfile_ext
            #     while os.path.isfile(os.path.join(self.log_path, new_name)):
            #         basename = '.'.join(new_name.split('.')[:len(new_name.split('.'))-1])
            #         new_name = '_'.join(basename.split('_')[:len(basename.split('_'))-1]) + '_' + str(counter) + logfile_ext
            #         counter += 1

            os.rename(self.log_file, os.path.join(self.log_path, new_name))
            if not os.path.isfile(os.path.join(self.log_path, new_name)):
                self._logger_note(ERROR, "Could not rename log file to '{}'".format(new_name))
            else:
                self.log_file = os.path.join(self.log_path, new_name)
                self._logger_note(INFO, "Renamed logfile to '{}'".format(new_name))
        except Exception as e:
            self.__handle_excep(e)

    def __handle_excep(self, exception, with_tb=True):
        """ prints exception """
        try:
            self._logger_note(CRITICAL, "{}".format(exception), desc='Logger')
            if with_tb:  # with traceback
                import traceback
                self._logger_note(CRITICAL, traceback.format_exc())
                print("")
        except Exception as e:
            print("CRITICAL: While handling an exception another exception occurred, will only printed to screen: " + str(e))
            if with_tb:  # with traceback
                import traceback
                traceback.print_exc()
                print("")

    def set_all(self):
        """ Sets logger level to ALL level """
        self.level = self.ALL
        # self.logger_note(INFO, "Set log level to '{}' with value of {}. Displaying all log messages!".format(self.level.name, self.level.value), desc='Logger')
        self._logger_note(INFO, "Set log level to '{}'. Displaying all log messages!".format(self.level.name))

    def set_debug(self):
        """ Sets logger level to DEBUG level """
        self.level = self.DEBUG
        # self.logger_note(INFO, "Set log level to '{}' with value of {}".format(self.level.name, self.level.value), desc='Logger')
        self._logger_note(INFO, "Set log level to '{}'".format(self.level.name))

    def set_info(self):
        """ Sets logger level to INFO level """
        self.level = self.INFO
        # self.logger_note(INFO, "Set log level to '{}' with value of {}".format(self.level.name, self.level.value), desc='Logger')
        self._logger_note(INFO, "Set log level to '{}'".format(self.level.name))

    def set_warning(self):
        """ Sets logger level to WARNING level """
        self.level = self.WARNING
        # self.logger_note(INFO, "Set log level to '{}' with value of {}".format(self.level.name, self.level.value), desc='Logger')
        self._logger_note(INFO, "Set log level to '{}'".format(self.level.name))

    def set_error(self):
        """ Sets logger level to ERROR level """
        self.level = self.ERROR
        # self.logger_note(INFO, "Set log level to '{}' with value of {}".format(self.level.name, self.level.value), desc='Logger')
        self._logger_note(INFO, "Set log level to '{}'".format(self.level.name))

    def set_critical(self):
        """ Sets logger level to CRITICAL level """
        self.level = self.CRITICAL
        # self.logger_note(INFO, "Set log level to '{}' with value of {}".format(self.level.name, self.level.value), desc='Logger')
        self._logger_note(INFO, "Set log level to '{}'".format(self.level.name))

    def turn_off(self):
        """ Sets logger level to OFF level """
        self.level = self.OFF
        # self.logger_note(INFO, "Set log level to '{}' with value of {}".format(self.level.name, self.level.value), desc='Logger')
        self._logger_note(INFO, "Set log level to '{}'. All log messages are disabled".format(self.level.name))

    def debug(self, message, desc='', file_only=False):
        """ Adds log message with level DEBUG to log """
        self._add_to_log('DEBUG', message, desc=desc, file_only=file_only)

    def info(self, message, desc='', file_only=False):
        """ Adds log message with level INFO to log """
        self._add_to_log('INFO', message, desc=desc, file_only=file_only)

    def warning(self, message, desc='', file_only=False):
        """ Adds log message with level WARNING to log """
        self._add_to_log('WARNING', message, desc=desc, file_only=file_only)

    def error(self, message, desc='', file_only=False):
        """ Adds log message with level ERROR to log """
        self._add_to_log('ERROR', message, desc=desc, file_only=file_only)

    def critical(self, message, desc='', file_only=False):
        """ Adds log message with level CRITICAL log """
        self._add_to_log('CRITICAL', message, desc=desc, file_only=file_only)

    @staticmethod
    def static_debug(message, desc='', file_only=False):
        """ creates temp logger class instance and writes log message, should only used if a instance was created before """
        stat_logger = Logger()
        stat_logger.warning("Method is deprecated and will be removed in later releases, use module level methode instead!")
        stat_logger.debug(message, desc=desc, file_only=file_only)

    @staticmethod
    def static_info(message, desc='', file_only=False):
        """ creates temp logger class instance and writes log message, should only used if a instance was created before """
        stat_logger = Logger()
        stat_logger.warning("Method is deprecated and will be removed in later releases, use module level methode instead!")
        stat_logger.info(message, desc=desc, file_only=file_only)

    @staticmethod
    def static_warning(message, desc='', file_only=False):
        """ creates temp logger class instance and writes log message, should only used if a instance was created before """
        stat_logger = Logger()
        stat_logger.warning("Method is deprecated and will be removed in later releases, use module level methode instead!")
        stat_logger.warning(message, desc=desc, file_only=file_only)

    @staticmethod
    def static_error(message, desc='', file_only=False):
        """ creates temp logger class instance and writes log message, should only used if a instance was created before """
        stat_logger = Logger()
        stat_logger.warning("Method is deprecated and will be removed in later releases, use module level methode instead!")
        stat_logger.error(message, desc=desc, file_only=file_only)

    @staticmethod
    def static_critical(message, desc='', file_only=False):
        """ creates temp logger class instance and writes log message, should only used if a instance was created before """
        stat_logger = Logger()
        stat_logger.warning("Method is deprecated and will be removed in later releases, use module level methode instead!")
        stat_logger.critical(message, desc=desc, file_only=file_only)

    def _logger_note(self, log_level, message, desc='Logger'):
        """
        Used for logger own messages to avoid asking for supress_logger_notes all along the line
        :param log_level: String or LogLevel, name of loglevel, decides if message is printed and saved
        :param message: String, message to print
        :param desc: String, small description to mark what type of message, default: 'Logger'
        :return: None
        """
        if not self._suppress_logger_notes:
            if isinstance(log_level, LogLevel):
                self._add_to_log(log_level.name, message, desc)
            else:
                self._add_to_log(log_level, message, desc)

    def _add_to_log(self, log_level, message, desc='', file_only=False):
        """
        Prints to screen and saves in log file
        :param log_level: String, name of loglevel, decides if message is printed and saved
        :param message: String, message to print
        :param desc: String, small description to mark what type of message, default: 'Logger'
        :param file_only: Boolean, prints only to file if True
        :return: None
        """

        # todo handler if message not utf-8 encoded

        if self.__init_state:  # while in init state add to log file buffer
            self.__log_file_buffer.append((log_level, message, desc))
            return

        if not isinstance(log_level, str) or log_level.upper() not in vars(self) or not isinstance(vars(self)[log_level.upper()], LogLevel):  # nicer approach than invoking __dict__
            raise ValueError("Unknown log level: '{}'".format(log_level))

        if vars(self)[log_level.upper()].value < self.level.value:  # if loglevel not high enough
            return

        # messsage to long
        if 0 < MAX_LOG_MESSAGE_LENGTH < len(str(message)):
            message = message[:MAX_LOG_MESSAGE_LENGTH]
            self._logger_note(DEBUG, "Log message exceeded maximum length of {} characters and was shorted".format(MAX_LOG_MESSAGE_LENGTH))

        # create log message
        delim = ' | '
        timestamp = ''
        if self.time_stamp:
            now = datetime.datetime.now()
            timestamp = now.strftime('%d.%m.%Y') + ' ' + now.strftime('%H:%M') + delim
        if not str(desc) == '' and str(desc)[-(len(delim)):] != delim:  # second part especially needed when printing logFileBuffer
            desc = str(desc) + delim
        log_message = timestamp + log_level + delim + desc + str(message)

        if not file_only:
            print(log_message)
        if self.log_file is not None:
            try:
                with open(self.log_file, 'a') as log_file:
                    log_file.write(log_message + '\n')
            except FileNotFoundError:
                create_path(self.log_path)
                self._eval_file_header(file=self.log_file)
                self._logger_note(WARNING, "logfile was deleted, created new one!")
            except Exception as e:
                self.__handle_excep(e)

    def __str__(self):
        # todo better formatting
        return "Logger | {}".format(self.__dict__)

    def __repr__(self):
        return '\n' + self.__str__() + '\n'


def static_debug(message, desc='', file_only=False):
    """ creates temp logger class instance and writes log message, should only used if a instance was created before """
    stat_logger = Logger()
    stat_logger.debug(message, desc=desc, file_only=file_only)


def static_info(message, desc='', file_only=False):
    """ creates temp logger class instance and writes log message, should only used if a instance was created before """
    stat_logger = Logger()
    stat_logger.info(message, desc=desc, file_only=file_only)


def static_warning(message, desc='', file_only=False):
    """ creates temp logger class instance and writes log message, should only used if a instance was created before """
    stat_logger = Logger()
    stat_logger.warning(message, desc=desc, file_only=file_only)


def static_error(message, desc='', file_only=False):
    """ creates temp logger class instance and writes log message, should only used if a instance was created before """
    stat_logger = Logger()
    stat_logger.error(message, desc=desc, file_only=file_only)


def static_critical(message, desc='', file_only=False):
    """ creates temp logger class instance and writes log message, should only used if a instance was created before """
    stat_logger = Logger()
    stat_logger.critical(message, desc=desc, file_only=file_only)
