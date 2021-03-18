import telebot
import argparse
import sys
import time

import pymysql.cursors


from configobj import ConfigObj

##################
# parsing arguments
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--cfile", help="configfile", type=str, default="config.ini")
parser.add_argument('message', help="Message to send", type=str, default="config.ini")
args = parser.parse_args()

##################
# read inifile
try:
    config = ConfigObj(args.cfile)
    apitoken = config.get('token')
    db = config['dbname']
    dbhost = config['dbhost']
    dbport = config.get('dbport', '3306')
    dbuser = config['dbuser']
    dbpassword = config['dbpassword']
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
# get bot information
bot = telebot.TeleBot(apitoken)
try:
    botident = bot.get_me()
    botname = botident.username
    botcallname = botident.first_name
    botid = botident.id
    try:
        cursor.execute("insert into bot values ('%s','%s')" % (botid, botname))
    except:
        pass
except:
    print("Error in Telegram. Can not find Botname and ID")
    raise

##################
#
def sendtelegram(chatid, msg):
#    try:
    splitted_text = telebot.util.split_string(msg, 4096)
    for text in splitted_text:
        try:
            bot.send_message(chatid, text, parse_mode="markdown")
        except telebot.apihelper.ApiHTTPException as e:
            print("ConnectionError - Sending again after 5 seconds!!!")
            print("HTTP Error Code: {}".format(e.result))
            time.sleep(5)
            bot.send_message(chatid, text, parse_mode="markdown")
        except telebot.apihelper.ApiTelegramException:
            print("Telegram exception sending message to {}".format(chatid))
        except:
            print("ERROR IN SENDING TELEGRAM MESSAGE TO {}".format(chatid))
            print("Error: {}".format(sys.exc_info()[0]))


cursor.execute("select chatid FROM user where botid = '%s' and chatid not in (select chatid from userblock)" % (botid))

allchat = cursor.fetchall()

for chatid in allchat:
    sendtelegram(chatid[0],args.message)



