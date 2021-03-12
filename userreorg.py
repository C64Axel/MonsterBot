import pymysql.cursors
import sys
import argparse

from configobj import ConfigObj

from lib.dbcheck import db_need_update
from lib.logging import logger


##################
# parsing arguments
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dry", help="dry run", action='store_true')
args = parser.parse_args()

dryrun = 0
try:
    if args.dry:
        dryrun = 1
        logger.info("Dryrun")
except:
    pass

# read inifile
#
try:
    config = ConfigObj("config.ini")
    db = config['dbname']
    dbhost = config['dbhost']
    dbport = config.get('dbport', '3306')
    dbuser = config['dbuser']
    dbpassword = config['dbpassword']
    reorgdays = int((config.get('reorgdays', '180')))
except:
    logger.error("Inifile not given or missing parameter")
    quit()


# connect to database
#
try:
    connection = pymysql.connect(host=dbhost,
                                 user=dbuser,
                                 password=dbpassword,
                                 db=db,
                                 port=int(dbport),
                                 charset='utf8mb4',
                                 autocommit='True')
    cursor = connection.cursor()
except:
    logger.error("can not connect to database")
    quit()

if db_need_update(cursor):
    logger.error("Your DB-Version is to low. Please start dbupdate.py first")
    quit()

cursor.execute("select chatid from userstop where timestampdiff(DAY,stopdate,CURRENT_TIMESTAMP) > '%s'" % (reorgdays))
result = cursor.fetchall()
for row in result:
    logger.info("Delete Chatid {}".format(row[0]))
    if dryrun == 0:
        try:
            cursor.execute("delete from userassign where chatid = '%s'" % (row[0]))
            cursor.execute("delete from userstop where chatid = '%s'" % (row[0]))
        except:
            logger.error("Error in deleting chatid from userassign")
