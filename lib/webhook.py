import telebot
import sys
import http.server
import json
import hashlib
import datetime
import matplotlib.path as mplPath

from time import sleep, time
from queue import Queue
from geopy import distance

from lib.logging import logger
from lib.geolocation import geo_reverse
from lib.auth import user_ok

duplicatemsg = {}
pkmn_queue = Queue()
weather = {
    "0": '',
    "1": u'\U00002600',
    "2": u'\U00002614',
    "3": u'\U000026C5',
    "4": u'\U00002601',
    "5": u'\U0001F343',
    "6": u'\U00002744',
    "7": u'\U0001F301'
    }


##################
# Bot was blocked
def bot_was_blocked(connection, botid, chat_id):
    cursor = connection.cursor()
    logger.info("Bot was blocked. Stopping ChatId {}".format(chat_id))
    cursor.execute("delete from user where botid = '%s' and chatid = '%s'" % (botid, chat_id))
    cursor.execute("select count(*) from user where chatid = '%s'" % (chat_id))
    result = cursor.fetchone()
    if result[0] == 0:
        cursor.execute("insert ignore into userstop values ('%s', CURRENT_TIMESTAMP)" % (chat_id))


##################
# convert Message
def textsub(text, message):
    text = text.replace("\\n", "\n")
    text = text.replace("<pkmn>", str(message['name']))
    text = text.replace("<pkmnid>", str(message['pokemon_id']))
    text = text.replace("<despawn>", str(message['despawn']))
    text = text.replace("<iv>", str(message['iv']))
    text = text.replace("<cp>", str(message['cp']))
    text = text.replace("<atk>", str(message['individual_attack']))
    text = text.replace("<def>", str(message['individual_defense']))
    text = text.replace("<sta>", str(message['individual_stamina']))
    text = text.replace("<lvl>", str(message['pokemon_level']))
    text = text.replace("<road>", str(message['road']))
    text = text.replace("<postcode>", str(message['postcode']))
    text = text.replace("<town>", str(message['town']))
    text = text.replace("<weather>", weather[str(message['boosted_weather'])])
    return (str(text))


##################
# send monster to user
def sendmonster(bot, config, connection, pkmn_loc, geoprovider, geofences, allowmode):
    cursor = connection.cursor()

    botid = bot.get_me().id
    venuetitle = config['venuetitle']
    venuemsg = str(config['venuemsg'])
    ivmsg = str(config['ivmsg'])
    tggroup = config.get('tggroup', '')

    while True:
        message = pkmn_queue.get()

        pkmn_id = (message['pokemon_id'])

        # set monster info
        #
        try:
            pkmn_name = pkmn_loc[str(pkmn_id)]["name"]
        except:
            pkmn_name = "{} NOTFOUND".format(str(pkmn_id))
            logger.warning("{} not found in monster.json".format(str(pkmn_id)))

        # check if in geofence
        #
        if geofences:
            inside = False
            for geofence in geofences.keys():
                mypath = mplPath.Path(geofences[geofence])
                if mypath.contains_points([tuple((message['latitude'], message['longitude']))]):
                    inside = True
                    break
            if not inside:
                logger.info("{}({}) outside geofence".format(pkmn_name, pkmn_id))
                continue

        pkmn_despawn = datetime.datetime.fromtimestamp(int(message['disappear_time'])).strftime('%H:%M:%S')
        logger.info("{}({}) until {} @ {},{}".format(pkmn_name, pkmn_id, pkmn_despawn, message['latitude'],
                                                     message['longitude']))

        # calculate IV if encounting
        #
        try:
            pkmn_iv = float(((message['individual_attack'] + message['individual_defense'] + message[
                'individual_stamina']) * 100 / 45)).__round__(2)
            logger.info("IV:{:.2f} CP:{:4d} ATT:{:2d} DEF:{:2d} STA:{:2d}".format(pkmn_iv, message['cp'],
                                                                                  message['individual_attack'],
                                                                                  message['individual_defense'],
                                                                                  message['individual_stamina']))
        except:
            pkmn_iv = "None"
            message['individual_attack'] = "??"
            message['individual_defense'] = "??"
            message['individual_stamina'] = "??"
            message['cp'] = "??"
            message['pokemon_level'] = "??"

        if not 'boosted_weather' in message:
            message['boosted_weather'] = 0

        # add missing data to message
        message['iv'] = pkmn_iv
        message['name'] = pkmn_name
        message['despawn'] = pkmn_despawn
        message['geo_ok'] = False

        # get all chatids for the monster
        # no blocked chat id
        #
        connection.ping(reconnect=True)
        cursor.execute("select chatid,iv,level from userassign where pkmnid = '%s' and \
                        chatid in (select chatid from user where botid = '%s')" % (pkmn_id, botid))
        result_pkmn = cursor.fetchall()

        if len(result_pkmn) > 0:

            # send monster message to all
            #
            for chat_id, iv, level in result_pkmn:

                if not user_ok(bot, connection, allowmode, tggroup, chat_id):
                    logger.warning("ChatID {} not allowed for this Bot but has assignments".format(chat_id))
                    continue

                # get the user details
                cursor.execute("select lat,lon,dist from user where chatid = '%s'" % (chat_id))
                latlon = cursor.fetchone()
                lat = float(latlon[0])
                lon = float(latlon[1])
                dist = float(latlon[2])

                # check distance
                dist_ok = True
                if dist > 0:
                    pkmn_dist = distance.distance((lat, lon), (message['latitude'], message['longitude'])).kilometers
                    if pkmn_dist > dist:
                        dist_ok = False
                        logger.info("{} long distance: dist: {}  pkmn_dist: {}".format(chat_id, dist, pkmn_dist))

                # check level
                if message['pokemon_level'] == '??':
                    level_ok = True
                elif int(message['pokemon_level']) >= level:
                    level_ok = True
                else:
                    level_ok = False

                if not (dist_ok and level_ok):
                    continue

                if message['iv'] == "None":
                    if iv == -1:
                        # get geo only if not set
                        if not message['geo_ok']:
                            geo = geo_reverse(geoprovider, message['latitude'], message['longitude'])
                            message['road'] = "{} {}".format(geo[0], geo[1])
                            message['postcode'] = geo[2]
                            message['town'] = geo[3]
                            message['geo_ok'] = True

                        venuetitle1 = textsub(venuetitle, message)
                        venuemsg1 = textsub(venuemsg, message)
                        try:
                            bot.send_venue(chat_id, message['latitude'], message['longitude'], venuetitle1,
                                           venuemsg1)
                            logger.info(
                                "Send Telegram message to {} Monster {}({})".format(chat_id, pkmn_name, pkmn_id))
                        except telebot.apihelper.ApiTelegramException as e:
                            if e.result_json['error_code'] == 403:
                                bot_was_blocked(connection, botid, chat_id)
                        except telebot.apihelper.ApiHTTPException as e:
                            logger.error("Connection Error")
                            logger.error("HTTP Error Code: {}".format(e.result))
                        except:
                            logger.error("ERROR IN SENDING TELEGRAM MESSAGE TO {}".format(chat_id))
                            logger.error("Error: {}".format(sys.exc_info()[0]))
                    else:
                        logger.info(
                            "No message send to {}. SearchIV set but Monster {}({}) not encountered".format(chat_id,
                                                                                                            pkmn_name,
                                                                                                            pkmn_id))
                elif message['iv'] >= iv:
                    try:
                        # get geo only if not set
                        if not message['geo_ok']:
                            geo = geo_reverse(geoprovider, message['latitude'], message['longitude'])
                            message['road'] = "{} {}".format(geo[0], geo[1])
                            message['postcode'] = geo[2]
                            message['town'] = geo[3]
                            message['geo_ok'] = True

                        ivmsg1 = textsub(ivmsg, message)

                        bot.send_message(chat_id, ivmsg1)
                        bot.send_location(chat_id, message['latitude'], message['longitude'])
                        logger.info(
                            "Send Telegram IV message to {} Monster {}({})".format(chat_id, pkmn_name, pkmn_id))
                    except telebot.apihelper.ApiTelegramException as e:
                        if e.result_json['error_code'] == 403:
                            bot_was_blocked(connection, botid, chat_id)
                    except telebot.apihelper.ApiHTTPException as e:
                        logger.error("Connection Error")
                        logger.error("HTTP Error Code: {}".format(e.result))
                    except:
                        logger.error("ERROR IN SENDING TELEGRAM MESSAGE TO {}".format(chat_id))
                        logger.error("Error: {}".format(sys.exc_info()[0]))
                else:
                    logger.info(
                        "No message send to {}. SearchIV to low for Monster {}({})".format(chat_id, pkmn_name,
                                                                                           pkmn_id))


##################
# Reorg duplicate messages
def reorg_duplicate():
    while True:
        deleted = 0
        reorgtime = int(time())
        for n in list(duplicatemsg):
            if duplicatemsg[n] < reorgtime:
                duplicatemsg.pop(n)
                deleted += 1
        logger.info("Reorg duplicate Messages. Deleting {}/{}".format(deleted, len(duplicatemsg.keys())))
        sleep(10)


##################
# Wbhook Class
class WebhookHandler(http.server.SimpleHTTPRequestHandler):

    def do_POST(self):
        content_len = int(self.headers['content-length'])
        self.send_response(200)
        self.end_headers()

        # Json formatting
        #
        jsonlist = self.rfile.read(content_len)
        messages = json.loads(jsonlist)

        # Loop over all messages
        #
        for message in messages:
            msgtype = (message['type'])

            if msgtype == "pokemon":

                message = message['message']

                # check duplicate message
                jdump = json.dumps(message, sort_keys=True).encode("utf-8")
                md5 = hashlib.md5(jdump).hexdigest()
                despawn = message['disappear_time']

                if md5 not in duplicatemsg:
                    pkmn_queue.put(message)
                    duplicatemsg[md5] = despawn

    def log_message(self, format, *args):
        return
