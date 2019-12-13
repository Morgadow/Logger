# -*- coding: utf-8 -*-

from logger import Logger
import os



logger = Logger(loglvl='DEBUG', addtimestamp=True, suppressloggernotes=False)
logger.set_debug()
logger.set_debug()
logger.set_debug()
logger.info("ich bin ein Promi")
logger.warning("holt mich hier raus!")