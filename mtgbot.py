import telebot

import pymysql.cursors
import json

from configobj import ConfigObj
from threading import Thread
from time import time
from http.server import HTTPServer

from lib.dbcheck import db_need_update
from lib.logging import logger
from lib.webhook import reorg_duplicate, sendmonster, WebhookHandler


##################
# read inifile
try:
    config = ConfigObj("config.ini")
    apitoken = config.get('token')
    db = config['dbname']
    dbhost = config['dbhost']
    dbport = config.get('dbport', '3306')
    dbuser = config['dbuser']
    dbpassword = config['dbpassword']
    locale = config.get('locale', 'de')
    whport = int(config.get('port', '6000'))
    invstartmsg = config.get('startmsg', "locales/startmsg_" + locale + ".txt")
except:
    logger.error("Error in config.ini")
    quit()


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
    logger.error("can not connect to database")
    quit()


##################
# check DB-Version
if db_need_update(connection.cursor()):
    logger.error("Your DB-Version is to low. Please start dbupdate.py first")
    quit()


##################
# enable middleware Handler
telebot.apihelper.ENABLE_MIDDLEWARE = True


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
    logger.error("Error in Telegram. Can not find Botname and ID")
    quit()


##################
#
def sendtelegram(chatid, msg):
    try:
        splitted_text = telebot.util.split_string(msg, 4096)
        for text in splitted_text:
            try:
                bot.send_message(chatid, text, parse_mode="markdown")
            except (ConnectionAbortedError, ConnectionResetError, ConnectionRefusedError, ConnectionError):
                logger.warning("ConnectionError - Sending again after 5 seconds!!!")
                time.sleep(5)
                bot.send_message(chatid, text, parse_mode="markdown")
            except:
                raise

    except:
        logger.error("ERROR IN SENDING TELEGRAM MESSAGE TO {}".format(chatid))


##################
# Log all messages send to the bot
@bot.middleware_handler(update_types=['message'])
def log_message(bot_instance, message):
    logger.info("Message from ID:{}:{}:{}".format(message.from_user.id, message.from_user.username, message.text))
    bot_instance.userok = True

    try:
        connection.ping(reconnect=True)
        cursor.execute("select count(*) from userblock where chatid = '%s'" % (message.chat.id))
        result = cursor.fetchone()
        if result[0] == 1:
            sendtelegram(message.chat.id, msg_loc["19"])
            bot_instance.userok = False
    except:
        sendtelegram(message.chat.id, msg_loc["6"])
        bot_instance.userok = False


##################
# Handle start
@bot.message_handler(commands=['start'])
def handle_start(message):
    if bot.userok:
        msg = ""

        startmsg = open(invstartmsg, "r")
        for line in startmsg:
            msg = msg + "{}".format(line)
        sendtelegram(message.chat.id, msg)
        startmsg.close()

        try:  # delete chatid from Stop Table
            cursor.execute("delete from userstop where chatid = '%s'" % (message.chat.id))
        except:
            pass
        try:  # insert users information and the bot id
            cursor.execute("insert into user values ('%s','%s','%s','%s','%s',current_timestamp)" % (
                botid, message.chat.username, message.chat.first_name, message.chat.last_name, message.chat.id))
        except:
            pass

        sendtelegram(message.chat.id, msg_loc["2"])


##################
# Handle help
@bot.message_handler(commands=['help'])
def handle_help(message):
    if bot.userok:
        msg = msg_loc["1"]
        sendtelegram(message.chat.id, msg)


##################
# Handle stop
@bot.message_handler(commands=['stop'])
def handle_stop(message):
    if bot.userok:
        try:  # delete user data
            cursor.execute("delete from user where botid = '%s' and chatid = '%s'" % (botid, message.chat.id))
        except:
            pass
        try:  # and if no bot left insert chatid in stop table for reorg
            cursor.execute("select count(*) from user where chatid = '%s'" % (message.chat.id))
            result = cursor.fetchone()
            if result[0] == 0:
                cursor.execute("insert ignore into userstop values ('%s', CURRENT_TIMESTAMP)" % (message.chat.id))
        except:
            pass
        sendtelegram(message.chat.id, msg_loc["3"])


##################
# Handle status
@bot.message_handler(commands=['status'])
def handle_status(message):
    if bot.userok:
        cursor.execute("select count(*) from user where botid = '%s' and chatid = '%s'" % (botid, message.chat.id))
        result = cursor.fetchone()
        if result[0] > 0:
            sendtelegram(message.chat.id, msg_loc["4"])
        else:
            sendtelegram(message.chat.id, msg_loc["5"])


##################
# Handle mydata
@bot.message_handler(commands=['mydata'])
def handle_mydata(message):
    if bot.userok:
        cursor.execute("select botid,username,vorname,nachname,chatid from user where chatid = '%s'" % (message.chat.id))
        result = cursor.fetchall()
        if result:
            for row in result:
                cursor.execute("select botname from bot where botid = '%s'" % (row[0]))
                botname = cursor.fetchone()
                msg = str(msg_loc["21"].format(row[1], row[2], row[3], row[4]))
                sendtelegram(message.chat.id, msg)
        else:
            sendtelegram(message.chat.id, msg_loc["22"])


##################
# Handle deleteall
@bot.message_handler(commands=['deleteall'])
def handle_deleteall(message):
    if bot.userok:
        cursor.execute("delete from userassign where chatid = '%s'" % (message.chat.id))
        cursor.execute("delete from user where chatid = '%s'" % (message.chat.id))
        cursor.execute("delete from userstop where chatid = '%s'" % (message.chat.id))
        sendtelegram(message.chat.id, msg_loc["20"])


##################
# Handle list
@bot.message_handler(commands=['list'])
def handle_list(message):
    if bot.userok:
        cursor.execute("select pkmnid,iv from userassign where chatid = '%s'" % (message.chat.id))
        result_p = cursor.fetchall()

        msg = str(msg_loc["16"]) + "\n"
        for row in result_p:
            msg = msg + "{} : {} : {}\n".format(row[0], pkmn_loc[str(row[0])]["name"], row[1])
        while len(msg) > 0:  # cut message to telegram max messagesize
            msgcut = msg[:4096].rsplit("\n", 1)[0]
            sendtelegram(message.chat.id, msgcut)
            msg = msg[len(msgcut) + 1:]


##################
# Handle add
@bot.message_handler(commands=['add'])
def handle_add(message):
    if bot.userok:
        pkmniv = 0

        try:
            pkmnid = message.text.split(" ")[1]
        except:
            sendtelegram(message.chat.id, msg_loc["7"] + "/add")
            return

        try:
            pkmniv = int(message.text.split(" ")[2])
        except:
            pass

        if pkmniv > 100:
            pkmniv = 100
        if pkmniv < -1:
            pkmniv = -1

        try:
            pkname = pkmn_loc[str(pkmnid)]["name"]
            try:
                cursor.execute("insert into userassign values ('%s','%s','%s')" % (pkmnid, message.chat.id, pkmniv))
                sendtelegram(message.chat.id, pkname + msg_loc["8"])
            except:
                sendtelegram(message.chat.id, pkname + msg_loc["9"])
        except:
            sendtelegram(message.chat.id, str(pkmnid) + msg_loc["10"])


##################
# Handle delete
@bot.message_handler(commands=['del'])
def handle_del(message):
    if bot.userok:
        try:
            pkmnid = message.text.split(" ")[1]
        except:
            sendtelegram(message.chat.id, msg_loc["7"] + "/del")
            return

        try:
            pkname = pkmn_loc[str(pkmnid)]["name"]
            if cursor.execute("delete from userassign where chatid = '%s' and pkmnid = '%s'" % (message.chat.id, pkmnid)):
                sendtelegram(message.chat.id, pkname + msg_loc["12"])
            else:
                sendtelegram(message.chat.id, pkname + msg_loc["13"])
        except:
            sendtelegram(message.chat.id, str(pkmnid) + msg_loc["10"])


##################
# Handle setiv
@bot.message_handler(commands=['setiv'])
def handle_setiv(message):
    if bot.userok:
        try:
            pkmnid = int(message.text.split(" ")[1])
            pkmniv = int(message.text.split(" ")[2])
        except:
            sendtelegram(message.chat.id, msg_loc["14"])
            return

        if pkmniv > 100:
            pkmniv = 100

        try:
            pkname = pkmn_loc[str(pkmnid)]["name"]
            if cursor.execute("update userassign set iv = '%s' where chatid = '%s' and pkmnid = '%s'" % (
            pkmniv, message.chat.id, pkmnid)):
                sendtelegram(message.chat.id, msg_loc["15"].format(str(pkmniv), pkname))
            else:
                sendtelegram(message.chat.id, pkname + msg_loc["13"])
        except:
            sendtelegram(message.chat.id, str(pkmnid) + msg_loc["10"])


##################
# default handler for every other text
@bot.message_handler(func=lambda message: True, content_types=['text'])
def command_default(message):
    if bot.userok:
        sendtelegram(message.chat.id, message.text + msg_loc["17"])


##################
# Webhook handler
def start_webhook():
    logger.info("MonsterGBot {} serving at port {}".format(botname, whport))
    httpd.serve_forever()


##################

pkmn_loc = json.load(open("locales/monster_" + locale + ".json"))
msg_loc = json.load(open("locales/msg_" + locale + ".json"))

logger.info("Bot {} started".format(botname))
t1 = Thread(name='sendmonster', target=sendmonster, daemon=True, args=(bot, config, connection, pkmn_loc))
t1.start()

t2 = Thread(name='reorgdup', target=reorg_duplicate, daemon=True, args=())
t2.start()

httpd = HTTPServer(("", whport), WebhookHandler )
httpd.allow_reuse_address = True

t3 = Thread(name='webhook', target=start_webhook, daemon=True, args=())
t3.start()

bot.infinity_polling()
