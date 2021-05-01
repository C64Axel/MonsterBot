import telebot
import sys

from lib.logging import logger
from datetime import datetime

is_member = ['creator', 'member', 'administrator']

# Telegram cache an timeout
tg_cache = {}
tg_cache_timeout = 5

def user_ok(bot, connection, allowmode, tggroup, chat_id):
    cursor = connection.cursor()

    # check if user is blocked
    cursor.execute("select count(*) from userblock where chatid = '%s'" % (chat_id))
    if cursor.fetchone()[0] == 1:
        return False

    if not allowmode:
        return True

    # check if user is in allow Table
    cursor.execute("select count(*) from userallow where chatid = '%s'" % (chat_id))
    if cursor.fetchone()[0] == 1:
        return True

    # check TGGroup
    if tggroup:
        try:
            if chat_id in tg_cache:
                time_delta = datetime.now() - tg_cache[chat_id]
                if time_delta.total_seconds()/60 < tg_cache_timeout:
                    return True
                else:
                    tg_cache.pop(chat_id)

            result = bot.get_chat_member(tggroup, chat_id)
            if result.status in is_member:
                tg_cache[chat_id]=datetime.now()
                return True
        except telebot.apihelper.ApiHTTPException as e:
            logger.warning("HTTP Error Code: {}".format(e.result))
        except:
            logger.error("ERROR IN GETTING MEMBER FROM GROUP {}".format(tggroup))
            logger.error("Error: {}".format(sys.exc_info()[0]))

    return False
