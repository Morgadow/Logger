# -*- coding: utf-8 -*-

from logger import Logger
import os



# logger = Logger(loglvl='DEBUG', addtimestamp=True, suppressloggernotes=False, createlogfile=True, logpath=os.path.normpath("C:\Users\QXY5145\Desktop\Python_INI_Skript_V2"))
logger = Logger(loglvl='DEBUG', addtimestamp=True, suppressloggernotes=False, projectname="INI_TESTING BMU_R18", createlogfile=True, logpath=os.path.normpath("C:\\Users\\QXY5145\\Desktop\\Python_INI_Skript_V2\\logs"))
# logger = Logger(loglvl='DEBUG', addtimestamp=True, suppressloggernotes=False, createlogfile=True, logpath=os.path.normpath("C:\\Users\\QXY5145\\Desktop\\Python_INI_Skript_V2"))
# logger = Logger(loglvl='DEBUG', addtimestamp=True, suppressloggernotes=False, createlogfile=True)
logger.info("ich bin ein Promi")
logger.warning("holt mich hier raus!")
logger.set_error()
logger.warning("HUHU ich bin eine warnung")
logger.critical("scheise ich bin critical")


print("logger1")
print(logger.get_log_level())
print(logger._log_file)
print(logger.create_log_file)

print("logger2")
logger2 = Logger()
print(logger2.get_log_level())
print(logger2._log_file)
print(logger2.create_log_file)

print("logger1")
print(logger.get_log_level())