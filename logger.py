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
__major__ = 3       # for major interface/format changes
__minor__ = 2       # for minor interface/format changes
__release__ = 8     # for tweaks, bug-fixes, or development
__version__ = '%d.%d.%d' % (__major__, __minor__, __release__)
__version_info__ = tuple([int(num) for num in __version__.split('.')])
__author__ = 'Simon Schmid'


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
        return 1  # eq and hash not really needed but return True if comparing two instances, similar to Java

    def __eq__(self, other):
        try:
            return self.__dict__ is other.__dict__
        except:
            return 0


class Logger(Borg):

    def __init__(self, loglvl='ERROR', projectname=None, createlogfile=False, logpath=None, addtimestamp=False, suppressloggernotes=False):
        Borg.__init__(self)  # monostate

        # todo wenn neue instanz erstellt wird, dann werden auch alle attribute wieder von der neuen instanz übernommen auf alle anderen
        # es sollen aber die alten attribute in die neue instanz mitgenommen werden und nicht anders herum
        # immerhin werden attribute wenn nicht geändert auch beibehalten, nur wenn geändert, dann wird die veränderung mitgenommen
        # todo diesen hinweis mit in die help schreiben, bzw in die docstrings beider/der loggerklasse

        self.createlogfile = createlogfile
        if self.createlogfile:
            self.__logFileCreated = False
            self.__logFileBuffer = []
            self.logpath = logpath
        # self.logpath = os.path.normpath(os.path.abspath(logpath))
        self.addtimestamp = addtimestamp
        self.__projectname = projectname  # shown in topLine of logFile
        self.suppressloggernotes = suppressloggernotes

        # set loglvl, save as numeric value
        self.__possibleloglvl = {'OFF': 100, 'CRITICAL': 50, 'ERROR': 40, 'WARNING': 30, 'INFO': 20, 'DEBUG': 10, 'ALL': 0}
        self.__possibleloglvlltostring = {100: 'ALL', 50: 'CRITICAL', 40: 'ERROR', 30: 'WARNING', 20: 'INFO', 10: 'DEBUG', 0: 'ALL'}
        self.__defaultLogLvl = 'ERROR'  # if someone tries initializing without valid log level
        self.currloglvl = None
        self.set_log_lvl(loglvl)

        if '--debug' in sys.argv:
            self.set_log_lvl('ALL')
            self.add_to_log('INFO', "Enter Debug Mode: Turning all Logmessages on!", desc='Logger')
        if '--help' in sys.argv:  # show complete help
            self.help()

        if self.createlogfile:
            self.__init_log_file()

        # would maybe fail before this line but who knows ...
        if str(sys.version_info[0]) + '.' + str(sys.version_info[1]) != "3.7":
            if not self.suppressloggernotes:
                self.add_to_log('WARNING', "Designed for Python 3.7, might fail!", desc='Logger')

        if not self.suppressloggernotes:
            self.add_to_log('INFO', "Logger ready!", desc='Logger')

    def set_log_lvl(self, loglvl):
        """
        set current loglvl, input string of name or integer value
        """
        
        try:
            
            if self.currloglvl is None:
                
                if isinstance(loglvl, int) and loglvl in self.__possibleloglvlltostring:  # input integer
                    self.currloglvl = loglvl
                elif isinstance(loglvl, str) and loglvl.upper() in self.__possibleloglvl:  # input string
                    self.currloglvl = self.__possibleloglvl[loglvl.upper()]
                else:  # input not recognized or not a valid loglevel
                    self.set_log_lvl(self.__defaultLogLvl)
                    if not self.suppressloggernotes:
                        self.add_to_log('ERROR', "Input for desired log level not recognized! Took default log level: '{}'".format(self.__defaultLogLvl), desc='Logger')

            else:  # self.currloglvl is not None
            
                if isinstance(loglvl, int) and loglvl in self.__possibleloglvlltostring:  # input integer
                    if self.currloglvl == loglvl:
                        if not self.suppressloggernotes:
                            self.add_to_log('DEBUG', "Desired log level corresponds to the current one!", desc='Logger')
                        return
                    self.currloglvl = loglvl
                elif isinstance(loglvl, str) and loglvl.upper() in self.__possibleloglvl:  # input string
                    if self.currloglvl == self.__possibleloglvl[loglvl.upper()]:
                        if not self.suppressloggernotes:
                            self.add_to_log('DEBUG', "Desired log level corresponds to the current one!", desc='Logger')
                        return
                    self.currloglvl = self.__possibleloglvl[loglvl.upper()]
                else:  # input not recognized or not a valid loglevel
                    if not self.suppressloggernotes:
                        self.add_to_log('ERROR', "Input for desired log level not recognized!", desc='Logger')
                    return
                if not self.suppressloggernotes:
                    self.add_to_log('INFO', "Logger level set to: '{}' : {}".format(self.__possibleloglvlltostring[self.currloglvl], self.currloglvl), desc='Logger')
            
        except Exception as e:
            if not self.suppressloggernotes:
                self.add_to_log('CRITICAL', "Exception while setting log level!", desc='Logger')
                self.add_to_log('CRITICAL', "Exception: {}".format(e))
            else:
                pass
   
    def get_log_lvl(self):
        self.add_to_log('INFO', "Current Logger Level: ['{}', {}]".format(self.__possibleloglvlltostring[self.currloglvl], self.currloglvl), desc='Logger')
        return self.__possibleloglvlltostring[self.currloglvl], self.currloglvl
    
    def add_log_lvl(self, newloglvl):
        """
        used to add a custom logLvl provided as list with format: ['name', integerValue]
        """
        
        try:

            min_index_log_level = 0
            max_index_log_level = 100
            min_length_log_level_name = 1
            max_length_log_level_name = 25
           
            if not isinstance(newloglvl, list) or len(newloglvl) != 2:
                if not self.suppressloggernotes:
                    self.add_to_log('ERROR', "Wrong input argument, please provide list with following format: ['levelName', levelInInteger]!", desc='Logger | addLogLvl')
                return
            if not isinstance(newloglvl[0], str) or not isinstance(newloglvl[1], int):
                if not self.suppressloggernotes:
                    self.add_to_log('ERROR', "Wrong input argument, please provide list with following format: ['levelName', levelInInteger]!", desc='Logger | addLogLvl')
                return
            if not min_index_log_level < newloglvl[1] < max_index_log_level:
                if not self.suppressloggernotes:
                    self.add_to_log('ERROR', "Integer equivalent has to be an integer between {} and {}!".format(min_index_log_level, max_index_log_level), desc='Logger | addLogLvl')
                return
            if not min_length_log_level_name < len(newloglvl[0]) < max_length_log_level_name:
                if not self.suppressloggernotes:
                    self.add_to_log('ERROR', "Length of new logger level has to be between {} and {} symbols!".format(min_length_log_level_name, max_length_log_level_name), desc='Logger | addLogLvl')
                return
            if newloglvl[0] in self.__possibleloglvl or newloglvl[1] in self.__possibleloglvlltostring:
                if not self.suppressloggernotes:
                    self.add_to_log('ERROR', "New Logger level name or integer value already exists!", desc='Logger | addLogLvl')
                return
            
            self.__possibleloglvl.update({newloglvl[0].upper(): newloglvl[1]})
            self.__possibleloglvlltostring.update({newloglvl[1]: newloglvl[0].upper()})
            if not self.suppressloggernotes:
                self.add_to_log('INFO', "Added custom log level: ['{}', {}]".format(newloglvl[0].upper(), newloglvl[1]), desc='Logger')
            
        except Exception as e:
            if not self.suppressloggernotes:
                self.add_to_log('CRITICAL', "Exception while adding a custom log level!", desc='Logger')
                self.add_to_log('CRITICAL', "Exception: {}".format(e))
            else:
                pass
    
    def _remove_log_lvl(self, delloglvl):
        """
        deletes one loglevel, cant delete current log level, input string of name or int of integer equivalent or list with ['name', intValue]
        """
        
        try:
        
            # list with format ['name', int]
            if isinstance(delloglvl, list) and len(delloglvl) == 2 and isinstance(delloglvl[0], str) and isinstance(delloglvl[1], int):
                if delloglvl[0] in self.__possibleloglvl and delloglvl[1] in self.__possibleloglvlltostring:
                    if delloglvl[1] != self.currloglvl:
                        del(self.__possibleloglvl[delloglvl[0]])
                        del(self.__possibleloglvlltostring[delloglvl[1]])
                        if not self.suppressloggernotes:
                            self.add_to_log('INFO', "Deleted log level: {}".format(delloglvl), desc='Logger')
                        return
                    else:
                        if not self.suppressloggernotes:
                            self.add_to_log('WARNING', "Can't remove current log level!", desc='Logger')
                        return
                else:
                    if not self.suppressloggernotes:
                        self.add_to_log('WARNING', "Log level to delete does not exist!", desc='Logger')
                    return
            
            # input str
            if isinstance(delloglvl, str):
                if delloglvl in self.__possibleloglvl:
                    if self.__possibleloglvl[delloglvl] != self.currloglvl:
                        del(self.__possibleloglvlltostring[self.__possibleloglvl[delloglvl]])
                        del(self.__possibleloglvl[delloglvl])
                        if not self.suppressloggernotes:
                            self.add_to_log('INFO', "Deleted log level: {}".format(delloglvl), desc='Logger')
                        return
                    else:
                        if not self.suppressloggernotes:
                            self.add_to_log('WARNING', "Can't remove current log level!", desc='Logger')
                        return
                else:
                    if not self.suppressloggernotes:
                        self.add_to_log('WARNING', "Log level to delete does not exist!", desc='Logger')
                    return
            
            # input int
            if isinstance(delloglvl, int):
                if delloglvl in self.__possibleloglvlltostring:
                    if delloglvl != self.currloglvl:
                        del(self.__possibleloglvl[self.__possibleloglvlltostring[delloglvl]])
                        del(self.__possibleloglvlltostring[delloglvl])
                        if not self.suppressloggernotes:
                            self.add_to_log('INFO', "Deleted log level: {}".format(delloglvl), desc='Logger')
                        return
                    else:
                        if not self.suppressloggernotes:
                            self.add_to_log('WARNING', "Can't remove current log level!", desc='Logger')
                        return
                else:
                    if not self.suppressloggernotes:
                        self.add_to_log('WARNING', "Log level to delete does not exist!", desc='Logger')
                    return
                    
        except Exception as e:
            if not self.suppressloggernotes:
                self.add_to_log('CRITICAL', "Exception while removing log level!", desc='Logger')
                self.add_to_log('CRITICAL', "Exception: {}".format(e))
            else:
                pass

    # @property
    # def currloglvl(self):
    #     self.add_to_log('INFO',"Current Logger Level: ['{}', {}]".format(self.__possibleloglvlltostring[self.currloglvl],self.currloglvl), desc='Logger')
    #     return self.__possibleloglvlltostring[self.currloglvl], self.currloglvl

    @property
    def possible_log_lvl(self):
        self.add_to_log('INFO', "possibleLogLvl:", desc='Logger')
        for lvl in self.__possibleloglvl:
            self.add_to_log('INFO', "\t'{}' : {}".format(lvl, self.__possibleloglvl[lvl]))
        return self.__possibleloglvl
        
    @property
    def possible_log_lvl_tostring(self):
        self.add_to_log('INFO', "possibleLogLvlToString:", desc='Logger')
        for lvl in self.__possibleloglvlltostring:
            self.add_to_log('INFO', "\t'{}' : {}".format(lvl, self.__possibleloglvlltostring[lvl]))
        return self.__possibleloglvlltostring

    def __init_log_file(self):

        try:
            if self.logpath is None:  # then take default path: skriptpath + 'logs'
                self.logpath = os.path.normpath(os.path.join(os.getcwd(), 'logs'))
                if not os.path.exists(self.logpath):
                    os.mkdir(self.logpath)  # create folder if not existing
                    if os.path.exists(self.logpath):
                        if not self.suppressloggernotes:
                            self.add_to_log('INFO', "Created folder 'logs' at '{}'".format(os.getcwd()), desc='Logger')
                    else:
                        self.createlogfile = False
                        if not self.suppressloggernotes:
                            self.add_to_log('ERROR', "Could not create folder 'logs' at '{}'. Will not create a log file!".format(os.getcwd()), desc='Logger')
                        return
            else:  # create all subfolder needed
                sub_folder_list = self.logpath.split("\\")
                delim = '\\'
                for folder in range(len(sub_folder_list)):
                    if not os.path.exists(os.path.normpath(delim.join(sub_folder_list[:folder + 1]))):
                        os.mkdir(os.path.normpath(delim.join(sub_folder_list[:folder + 1])))
                        if os.path.exists(os.path.normpath(delim.join(sub_folder_list[:folder + 1]))):
                            if not self.suppressloggernotes:
                                # self.addToLog('DEBUG',"Created folder: {}".format(folder), desc='Logger')
                                self.add_to_log('DEBUG', "Created folder: '{}' at: '{}'".format(sub_folder_list[folder], delim.join(sub_folder_list[:folder])), desc='Logger')
                        else:
                            self.createlogfile = False
                            if not self.suppressloggernotes:
                                self.add_to_log('ERROR', "Could not create folder '{}' at '{}'! Will not create log file!".format(sub_folder_list[folder], delim.join(sub_folder_list[:folder])), desc='Logger')
                            return

            # evaluate __logFileName
            now = datetime.datetime.now()
            if self.__projectname is not None:
                self.__logFileName = self.__projectname + '_' + now.strftime("%d-%m-%Y") + '.txt'
            else:
                self.__logFileName = now.strftime("%d-%m-%Y") + '.txt'
            if self.__logFileName in os.listdir(self.logpath):  # if file with name already exists add '_X' and count X until not existing
                counter = 1
                while True:
                    if self.__projectname is not None:
                        self.__logFileName = self.__projectname + '_' + now.strftime("%d-%m-%Y") + '_' + str(counter) + '.txt'
                    else:
                        self.__logFileName = now.strftime("%d-%m-%Y") + '_' + str(counter) + '.txt'
                    if self.__logFileName in os.listdir(self.logpath):
                        counter += 1
                    else:
                        break
            
            # init logfile
            with open(os.path.join(self.logpath, self.__logFileName), 'w+') as logFile:
                if self.__projectname is not None:
                    logFile.write('---------------- {} - Log File vom {} um {} Uhr ----------------\n\n'.format(self.__projectname, now.strftime("%d-%m-%Y"), now.strftime("%H:%M")))
                else:
                    logFile.write('---------------- Log File vom {} um {} Uhr ----------------\n\n'.format(now.strftime("%d-%m-%Y"), now.strftime("%H:%M")))
                    
            if not os.path.isfile(os.path.join(self.logpath, self.__logFileName)):  # could not create file
                self.createlogfile = False
                if not self.suppressloggernotes:
                    self.add_to_log('ERROR', "Could not create log file! Logger will not create any log file!", desc='Logger')
                return
            else:
                if not self.suppressloggernotes:
                    self.add_to_log('INFO', "Created log file '{}' at '{}'!".format(self.__logFileName, self.logpath), desc='Logger')
                self.__logFileCreated = True
                
            # print buffer
            if self.__logFileCreated and len(self.__logFileBuffer) > 0:
                for message in self.__logFileBuffer: 
                    self.add_to_log(message[0], message[1], desc=message[2], only_to_file=True)
                self.__logFileBuffer = []
                
        except Exception as e: 
            self.createlogfile = False
            if not self.suppressloggernotes:
                self.add_to_log('CRITICAL', "Excecution while creating log file! Logger will not create any log file!", desc='Logger')
                self.add_to_log('CRITICAL', "Exception: {}".format(e))

    def get_loglevelname_by_value(self, search_value):
        # todo test and docstring
        return [name for name, value in list.items() if value == search_value]

    def handle_excep(self, exception, with_tb=True):
        """ prints exception """
        # todo
        if not self.suppressloggernotes:
            print("CRITICAL: {}".format(exception))
            if with_tb:  # with traceback
                import traceback
                traceback.print_exc()
                print("")

    def set_debug(self):
        pass

    def set_info(self):
        pass

    def set_warning(self):
        pass

    def set_error(self):
        pass

    def set_critical(self):
        pass

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

    def add_to_log(self, lvl, message, desc='', only_to_file=False):
        """
        if lvl (string) is at least the set loglevel message is printed and logged in the logFile if one is created
        """
        
        try:
        
            min_length_message = 1
            max_length_message = 125
            max_desc_length = 25
            
            # check level
            if not isinstance(lvl, str):
                if not isinstance(lvl, int):
                    if not self.suppressloggernotes:
                        self.add_to_log('ERROR', "Given Logger Level type not supported! Please provide as string or integer!", desc='Logger | addToLog')
                    return
                else:
                    if lvl in self.__possibleloglvlltostring:
                        lvl = self.__possibleloglvlltostring[lvl]  # convert into string equivalent
                    else:
                        if not self.suppressloggernotes:
                            self.add_to_log('ERROR', "Given logger level not recognized!", desc='Logger | addToLog')
                        return 
            else:
                if lvl.upper() not in self.__possibleloglvl:
                    if not self.suppressloggernotes:
                        self.add_to_log('ERROR', "Given logger level not recognized!", desc='Logger | addToLog')
                    return
                   
            # only print messages with same or higher value
            if not self.__possibleloglvl[lvl.upper()] >= self.currloglvl:
                if 'DEBUG' in self.__possibleloglvl and self.currloglvl <= self.__possibleloglvl['DEBUG'] and not self.suppressloggernotes: # otherwise recursion error
                    self.add_to_log('DEBUG', "Message log level '{}' was lower than logger log level '{}'!".format(lvl, self.__possibleloglvlltostring[self.currloglvl]), desc='Logger')
                return
            
            # check message        
            if not min_length_message < len(message) < max_length_message:
                if not self.suppressloggernotes:
                    self.add_to_log('WARNING', "The message may only be between {} and {} characters long!".format(min_length_message, max_length_message), desc='Logger | addToLog')
                if len(message) > max_length_message:  # resize message if to long
                    message = message[:max_length_message] + ' ...'
                    if not self.suppressloggernotes:
                        self.add_to_log('DEBUG', "Message exceeds {}, message was resized!".format(max_length_message), desc='Logger | addToLog')
                if len(message) < min_length_message:  # return if to short
                    if not self.suppressloggernotes:
                        self.add_to_log('DEBUG', "Message length below {}, not sending any!".format(min_length_message), desc='Logger | addToLog')
                    return
            if len(desc) > max_desc_length:
                if not self.suppressloggernotes:
                    self.add_to_log('WARNING', "Maximum length of description length of {} exceeded!".format(max_desc_length), desc='Logger | addToLog')
                desc = ''

            # create logmessage
            desc = str(desc)
            if not desc == '' and desc[-3:] != ' | ':  # second part escpecially needed when printing logFileBuffer
                desc = desc + ' | '
            timestamp = ''
            if self.addtimestamp:
                now = datetime.datetime.now()
                timestamp = now.strftime('%d.%m.%Y') + ' ' + now.strftime('%H:%M') + ' | '
            logmessage = lvl.upper() + ' | ' + timestamp + desc + str(message)
                
            # print to console and write to logfile
            if not only_to_file:
                print(logmessage)
            if self.createlogfile and self.__logFileCreated:  # if logfile already created
                try:
                    with open(os.path.join(self.logpath, self.__logFileName), 'a') as logFile:
                        logFile.write(logmessage + '\n')
                except Exception as e:
                    if not self.suppressloggernotes:
                        self.add_to_log('CRITICAL', "Exception while writing to logFile!", desc='Logger')
                        self.add_to_log('CRITICAL', "Exception: {}".format(e))
                    else:
                        pass
            elif self.createlogfile and not self.__logFileCreated:  # write to buffer and write to file after creation
                self.__logFileBuffer.append((lvl, message, desc))
            
        except Exception as e:
            if not self.suppressloggernotes:
                self.add_to_log('CRITICAL', "Exception while adding data to log!", desc='Logger')
                self.add_to_log('CRITICAL', "Exception: {}".format(e))
            else:
                pass

    def __str__(self):
        # todo
        pass

    def __repr__(self):
        return '\n' + self.__str__() + '\n'