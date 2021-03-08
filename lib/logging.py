##################
# Logging

import telebot
import logging
import logging.handlers

logfilename = 'log/monsterbot.log'
logger = logging.getLogger('monsterbot')
logger.setLevel(logging.INFO)

logfile = logging.handlers.RotatingFileHandler(logfilename, maxBytes=5000000, backupCount=5)
formatter = logging.Formatter('%(asctime)s|%(levelname)-8s|%(threadName)-15s|%(message)s')
logfile.setFormatter(formatter)
logger.addHandler(logfile)

telebot.logger.setLevel(logging.INFO)
telebot.logger.handlers = []
telebot.logger.addHandler(logfile)