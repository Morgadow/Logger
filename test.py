# -*- coding: utf-8 -*-

import logger
import os
import time


# # logger = Logger(loglvl='DEBUG', addtimestamp=True, suppressloggernotes=False, createlogfile=True, logpath=os.path.normpath("C:\Users\QXY5145\Desktop\Python_INI_Skript_V2"))
# logger = Logger(loglvl='DEBUG', addtimestamp=True, suppressloggernotes=False, projectname="INI_TESTING BMU_R18", createlogfile=True, logpath=os.path.normpath("C:\\Users\\QXY5145\\Desktop\\Python_INI_Skript_V2\\logs"))
# logger.info("ich bin ein Promi")
# logger.warning("holt mich hier raus!")
# logger.set_error()
# logger.warning("HUHU ich bin eine warnung")
# logger.critical("scheise ich bin critical")

# print("logger 1")
# print(logger.__dict__)


# print("logger1")
# print(logger.get_log_level())
# print(logger._log_file)
# print(logger.create_log_file)
#
# print("logger2")
# logger2 = Logger()
# print(logger2.get_log_level())
# print(logger2._log_file)
# print(logger2.create_log_file)
#
# print("logger1")
# print(logger.get_log_level())



# # logger 1
# # logger1 = Logger(level='DEBUG', suppressloggernotes=False)
# logger1 = Logger()
# print("logger1 level " + logger1.get_level()[0])
# print("suppresloggernotes logger1: " + str(logger1.suppress_logger_notes))
# # logger2 = Logger(level="ERROR")
# # logger2 = Logger(level="ERROR")
# logger3 = Logger(suppressloggernotes=False)
# logger2 = Logger(level="INFO")
# # logger2 = Logger()
# print("logger1 level " + logger1.get_level()[0])
# print("logger2 level " + logger2.get_level()[0])

# # logger1 = Logger(level="DEBUG", createlogfile=True, projectname='Just_Testing')
# logger1 = Logger(level="DEBUG", addtimestamp=True)
# # logger2 = Logger(level="ERROR")
# print("logger1 : " + str(logger1.get_level()[0]))
# # logger1.info("hier ist eine nachricht die länger als die maximal zulässige nachrichten länge ist, beziehungsweise hoffe ich das in diesem fall!")
# logger1.formatter(delim=' : ')
# print(logger1._format)

# test method rename logfile
# logger1 = logger.Logger(level=logger.DEBUG, createlogfile=True)
# logger1 = logger.Logger(level='debug', createlogfile=True, logpath="C:\\Users\\Simon\\Desktop\\Projekte\\Python\\Logger\\logs")
# logger.static_debug("debug message", desc="Loggerino")
# logger1.rename_logfile("new_log_file_name2.log", char_restiction=False)

# test input logfile
# logger2 = logger.Logger(level='DEBUG', logfile="C:\\Users\\Simon\\Desktop\\Projekte\\Python\\Logger\\logs\\TestFile.txt")

os.system("cls")

logger1 = logger.Logger(logger.DEBUG, logfile=os.path.join(os.getcwd(), 'logs', 'neuelogfile.log'))