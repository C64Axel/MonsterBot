# MonsterBot

![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)
![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)
![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)

Telegram Bot for individual selection

## Installation Guide:

Clone the git repository.  
Create a virtual environment and install the requirements:  
```
apt install python-virtualenv

virtualenv -p python3 ~/Monsterbot_env

cd ~/Monsterbot

~/Monsterbot_env/bin/pip install -r requirements.txt
```

### Install the Database

If you want to choose another schema please edit createdb.sql.

```
mysql -u <dbuser> < createdb.sql
```

### Upgrade the Database

To upgrade the Database please stop all bots and execute

```
dbupdate.py
```

### Telegram

Create a Telegram Bot and put the APIToken in the config.ini File.

### Customize config.ini

config.example:  
```
token=xxxxxxxxxx      # Bot API Token
locale=de             # Language Settings

port=6000             # Port for webhook
reorgdays=180         # Days for reorg inactive users

allowmode=False       # toggle free/allow mode
tggroup=""            # Telegram group for allowed Users

dbname=tgbotdb        # Database name
dbhost=127.0.0.1      # Database hostname
dbport=3306           # Database port
dbuser=dbuser         # Database user
dbpassword=xxxxxxxxx  # Database user password

# startmsg=           # individual Startmessagefile default startmsg_<locale>.txt

venuetitle="<pkmn>(<pkmnid>) until <despawn>"
venuemsg="<road> <postcode> <town>"

ivmsg="<pkmn>(<pkmnid>)\nIV:<iv> CP:<cp> L:<lvl>\nA:<atk>/D:<def>/S:<sta>\nuntil <despawn>\n<road>\n<postcode> <town>"

nominatim=False                 # enable Nominatim = True
nominatim_scheme=""             # Schema for Nominatim, default https
nominatim_url=""                # Nominatim URL, default nominatim.openstreetmap.org
                                # use your own like '<user>:<password>@your.FQDN.domain'
gmaps=False                     # enable Google = True
gmaps_apikey=""                 # Google API Key

geofile=""                      # Filename of the geofence file
```
You can use the following text substitution in the venuetitle, venuemsg and ivmsg strings:
```
<pkmn>    : Pokemonname
<pkmnid>  : PokemonID
<despawn> : Despawntime 24h
<iv>      : Pokemon IV
<cp>      : Pokemon CP
<atk>     : Pokemon Attack
<def>     : Pokemon Defence
<sta>     : Pokemon Stamina
<lvl>     : Pokemon Level
<road>    : Street name and number of the location
<poscode> : Postcode of the location
<town>    : Town of the location
```
The geofile can have multiple entries like:
```
[geofence1]
lat,lon
lat,lon
lat.lon
[geofence2]
lat,lon
lat,lon
```

You can also send the user a start message. Edit the files in "locales/startmsg_&lt;locale&gt;.txt".


## Programs:

1. **mtgbot.py** is the program for the Telegram bot commands. It manages the settings of the users.

   It knows the following commands:

   ```
   help - : Help
   status - : Status of the Bot
   list - : list your Pokemon and Type List
   add - <PokedexID> [IV]: add a Pokemon to the List. IV is not necessary, default 0
   del - <PokedexID>: delete a Pokemon from the List
   setiv - <PokedexID> <IV>: set the min IV% for Pokemon, -1 ignore IV
   setdist - : set the distance for Pokemon, 0 disable
   setlvl - : set the min level for Pokemon
   stop - : deaktivate the Bot
   start - : aktivate the Bot
   mydata - : show your stored data like last position and distance
   deleteall - : delete all your data, no recover
   ```
   
   You can use this for the command list in Telegram ;-)<p>  
   The Users Pokemonlist is shared between all the bots connected to the same Database. So a user can switch between the bots by stopping the one and starting another one. He can now use the same List on multiple Bots.  
   For multiple instances just start mtgbot.py with Parameter -c &lt;CONFIGFILE&gt;<p>  
   If a user only wants pokemon within a radius, he can share a location via telegram and set a radius with /setdist  
   /setdist 0 disable this function<p>  
  

2. **userreorg.py**  
   reorganize users who have not used the bot for a long time. Days are set in the inifile.  


3. **sendallmsg.py "&lt;MESSAGE&gt;"**  
   A little tool to send a message to all users.  


4. **user.py**  
   This Bot has two modes. A Freemode and an Allowmode. You can toggle the mode with the allowmode Flag in the config.ini.<p>  
   In Freemode (allowmode=False) everyone can use the bot.    
   If you want certain people not to use the bot just block them with```user.py -bl <CHATID>```.  
   The same command unblock the ChatId if it was blocked.<p>  
   If you want to use the Allowmode, you can add all allowed ChatId's:  
   ```user.py -a <CHATID>``` add a ChatId to the userallow Table.  
   ```user.py -d <CHATID>``` delete a ChatId from the userallow Table.  
   ```user.py -s``` show all allowed ChatId's from the userallow Table.<p>  
   Another way to allow user to use the Bot ist the Authentication with a Telegram group.  
   To activate it, put the bot as admin in the group and set tggroup to the GroupChatID.  
   So any user within this group is also allowed to use this bot.  
   The bot cache the Membership for 5 minutes.  
   If a member leaves the group, his or her list is not deleted.<p>  
   So the order of authentication is: blocklist -no-> allowlist -no-> telegramgroup -no-> disallow use
   


## Changes
### 13. Jan 2020
Initial Version.
### 08. Mar 2021
change to Python3
### 12 . Mar 2021
add distance for Pokemon
### 13. Mar 2021
add level for Pokemon
### 14. Mar 2021
add reverse geocoding for Googel and Nominatim
### 18. Mar 2021
add geofence
### 21. Mar 2021
add allowmode
### 01. May 2021
add TelegramGroup allow