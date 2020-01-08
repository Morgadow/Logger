# -*- coding: utf-8 -*-

from logger import Logger
import os
import test2


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

logger1 = Logger(level='ERROR')
print("logger1 : " + str(logger1.get_level()[0]))
test2.call_new_logger()
print("logger1 : " + str(logger1.get_level()[0]))
