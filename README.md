# MonsterBot

![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)
![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)
![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)

Telegram Bot for individual selection

## Installation Guide:

```
pip install -r requirements.txt
```

### Install the Database

If you want to choose another schema please edit createdb.sql.

```
mysql -u <dbuser> < createdb.sql
```

### Upgrade the Database

To upgrade the Database please stop all bots and webhooks and execute

```
dbupdate.py
```

### Upgrade from an older Version

Save your config.ini  
Delete your Repository, and your virtual Environment  
Clone the new Version and create a new virtual Environment
Copy your config.ini back

### Telegram

Create a Telegram Bot and put the APIToken in the config.ini File.

### Customize config.ini

You can use the following text substitution in the Message strings:

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
```

```
token=xxxxxxxxxx      # Bot API Token
locale=de             # Language Settings

port=6000             # Port for webhook
reorgdays=180         # Days for reorg inactive users

dbname=tgbotdb        # Database name
dbhost=127.0.0.1      # Database hostname
dbport=3306           # Database port
dbuser=dbuser         # Database user
dbpassword=xxxxxxxxx  # Database user password

# startmsg=           # individual Startmessagefile default startmsg_<locale>.txt

venuetitle="<pkmn>(<pkmnid>)"
venuemsg="until <despawn>"

ivmsg="<pkmn>(<pkmnid>)\nIV:<iv> CP:<cp> L:<lvl>\nA:<atk>/D:<def>/S:<sta>\nuntil <despawn>"
```

You can also send the user a start message. Edit the files in "locales/startmsg_<locale>.txt".

## Programs:

1. **mtgbot.py** is the program for the Telegram bot commands. It manages the settings of the users.

   It knows the folowing commands:

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
   
   You can use this for the command list in Telegram ;-)  

   The Users Pokemonlist is shared between all the bots connected to the same Database. So a user can switch between the bots by stopping the one and starting another one. He can now use the same List on multiple Bots.  
   Just start mtgbot.py with Parameter -c < CONFIGFILE ><p>  
   If a user only wants pokemon within a radius, he can share a location via telegram and set a radius with /setdist  
   /setdist 0 disable this function
   

2. **userreorg.py** reorganize users who have not used the bot for a long time. Days are set in the inifile.

## Changes

### 13. Jan 2020

Initial Version.

### 08. Mar 2021

change to Python3

### 12 . Mar 2021

add distance for Pokemon

### 13. Mar 2021

add level for Pokemon