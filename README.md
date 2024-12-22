# GreetingHelperBOT

## Intro
Created it because I'm tired of sending the same "Happy new year" to all of the friends/relatives and sometimes I even forget about it. That's why this bot helps you to configure the mailing for custom holidays.

## Deployment 
Digital Ocean Droplet - postgreSQL and telegram bot as docker images.
Check it out in telegram - @GreetingHelperBOT

### docker commands to host yourself:
```bash
docker pull ghcr.io/nikitazuevblago/greetinghelperbot:latest
docker run -d --name greetinghelperbot --restart=always -e TZ="CET" ghcr.io/nikitazuevblago/greetinghelperbot:latest
```

## Installation and Setup 
```bash
git clone git@github.com:nikitazuevblago/GreetingHelperBOT.git
cd GreetingHelperBOT
pip install -r requirements.txt
python bot.py
```
* Don't forget to create .env file with necessary variables

## Technologies Used
* aiogram
* psycopg2
* pyrogram

## File structure
bot.py - bot structure
db_interaction.py - interaction with database
custom_logging.py - configured logger
user_account.py - interacting on telegram user behalf
