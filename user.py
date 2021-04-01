import argparse
import pymysql.cursors

from configobj import ConfigObj

from lib.dbcheck import db_need_update

##################
# parsing arguments
parser = argparse.ArgumentParser()
parser.add_argument("-c", dest='configfile', help="configfile", type=str, default="config.ini")
parser.add_argument("-s", help="show all allowed chatid (allow mode)", action="store_true", default=False)

group1 = parser.add_mutually_exclusive_group(required=False)
group1.add_argument("-a", help="add chatid (allow mode)", action="store_true", default=False)
group1.add_argument("-d", help="delete chatid (allow mode)", action="store_true", default=False)
group1.add_argument("-bl", help="toggle block chatid (free mode)", action="store_true", default=False)

parser.add_argument("chatid", help="ChatId", nargs='?', type=str)

args = parser.parse_args()


##################
# read inifile
try:
    config = ConfigObj(args.configfile)
    apitoken = config.get('token')
    db = config['dbname']
    dbhost = config['dbhost']
    dbport = config.get('dbport', '3306')
    dbuser = config['dbuser']
    dbpassword = config['dbpassword']
    allowmode = config.get('allowmode', False)
except:
    print("Error in config.ini")
    raise

##################
# connect to database
try:
    connection = pymysql.connect(
        host=dbhost,
        user=dbuser,
        password=dbpassword,
        db=db,
        port=int(dbport),
        charset='utf8mb4',
        autocommit='True')
    cursor = connection.cursor()
except:
    print("can not connect to database")
    raise


##################
# check DB-Version
if db_need_update(connection.cursor()):
    print("Your DB-Version is to low. Please start dbupdate.py first")
    quit()

if (args.a or args.d or args.bl) and args.chatid == None:
    print ("This Argument requires a ChatID")
    quit()

if args.a:
    try:
        cursor.execute("insert into userallow value('%s')" % args.chatid)
    except:
        pass
    print("Allow ChatId {}".format(args.chatid))
elif args.d:
    cursor.execute("delete from userallow where chatid = '%s'" % args.chatid)
    print("Disallow ChatId {}".format(args.chatid))
elif args.s:
    cursor.execute("(select user.chatid,user.username from user join userallow on userallow.chatid = user.chatid) union (select chatid, '' from userallow where chatid not in (select chatid from user) ) order by chatid")
    records = cursor.fetchall()
    print("allowed ChatId's:")
    print("|ChatId      |Name                     |")
    print("|------------|-------------------------|")
    for record in records:
        print("|{:12s}|{:25s}|".format(record[0],record[1]))
elif args.bl:
    cursor.execute("select count(*) from userblock where chatid = '%s'" % args.chatid)
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute("insert into userblock value('%s')" % args.chatid)
        print("Block ChatId {}".format(args.chatid))
    else:
        cursor.execute("delete from userblock where chatid = '%s'" % args.chatid)
        print("Unblock ChatId {}".format(args.chatid))
