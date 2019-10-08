"""
Main python file.
English description is for developers, where Japanese ones will be desplayed to users.  
"""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from logger import Logger
from tweet_news import Tweet_news


def twitter_setup():
	# path to environment variables
	env_path = '.env'
	load_dotenv(dotenv_path=env_path)

	# get data from .env
	key = os.getenv('TWITTER_KEY')
	key_secret = os.getenv('TWITTER_KEY_SECRET')	
	token = os.getenv('TWITTER_TOKEN')
	token_secret = os.getenv('TWITTER_TOKEN_SECRET')	
	db_path = os.getenv('DB_PATH')

	return key, key_secret, token, token_secret, db_path
	

if __name__ == '__main__':
	key, key_s, token, token_s, db_path = twitter_setup()
	twitter_news = Tweet_news(key, key_s, token, token_s, db_path)

	loop = asyncio.get_event_loop()
	try:
		loop.run_until_complete(
				twitter_news.start()
		)
	except KeyboardInterrupt:
		# loop.run_until_complete(bot.logout())
		pass
	finally:
		loop.close()
