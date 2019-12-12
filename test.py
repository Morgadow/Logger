# -*- coding: utf-8 -*-

from logger import Logger
import os



# logger = Logger(loglvl='DEBUG', suppressloggernotes=False, createlogfile=True, logpath="C:\\Users\\Simon\\Desktop\\Projekte\\Python\\my_own_utils\\logs", addtimestamp=True, projectname='test')
# logger.help()

# logger.add_log_lvl(['Finest', 1])
# logger.currloglvl
# logger.get_log_lvl()

# logger.add_log_lvl(['TsdTsTEST', 1])
# logger.set_log_lvl(1)
# logger.set_log_lvl('TsdTsTEST')
# logger.set_log_lvl('TSDTSTEST')
# logger.currloglvl

# logger.possible_log_lvl_tostring
# logger.possible_log_lvl

# logger._remove_log_lvl('TsdTsTEST')

# logger.add_to_log("Info", "Das ist eine Testnachricht")
# logger.add_to_log("Info", "Das ist auchg eine Testnachricht", desc="2")
# logger.add_to_log("Info", "Das ist eine Testnachricht", onlytofile=True)

# logger.set_log_lvl("WARNing")

# logger.add_to_log("Info", "Das ist eine Testnachricht")
# logger.add_to_log("Info", "Das ist auchg eine Testnachricht", desc="2")
# logger.add_to_log("Info", "Das ist eine Testnachricht", onlytofile=True)

# logger.set_log_lvl("DEBUG")


logger = Logger(logpath=os.path.join(os.getcwd(), 'logs'), createlogfile=True, loglvl='DEBUG')
logger2 = Logger(loglvl="ERROR")

# print(logger.currloglvl)
# print(logger2.currloglvl)

print(logger.logpath)
print(logger2.logpath)