#!/bin/bash

cd ~/MonsterBot

nohup ../MonsterBot_env/bin/python3 ./mtgbot.py >/dev/null 2>&1 &
