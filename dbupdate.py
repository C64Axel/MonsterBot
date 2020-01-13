#! /usr/bin/python

import pymysql.cursors
import sys

from configobj import ConfigObj

from lib.dbcheck import check_db_version

def migrate_db():
	version = check_db_version(cursor)
	print("Old Version {}".format(version))

#	if version < 1:
#		cursor.execute("alter table `user` drop column 'paused'")
#		cursor.execute("update dbversion set version = '1'")

	version = check_db_version(cursor)
	print("New Version {}".format(version))
	print("Migration complete")

############# MAIN ################

# read inifile
try:
        inifile = sys.argv[1]
        config = ConfigObj(inifile)
        token=config.get('token')
        db = config['dbname']
        dbhost = config['dbhost']
        dbport = config.get('dbport', '3306')
        dbuser = config['dbuser']
        dbpassword = config['dbpassword']
except:
        print("Inifile not given")
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
        print("can not connect to database")
        quit()

migrate_db()
