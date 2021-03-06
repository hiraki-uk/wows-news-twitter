import asyncio

import twitter
from twitter.twitter_utils import calc_expected_status_length as calc_status_length

from database import Database
from logger import Logger


class Tweet_news:
	def __init__(self, key, secret_key, token, token_secret, db_path, logger=None):
		self.latest_id = 0
		self.database = Database(db_path)
		self.api = twitter.Api(
			consumer_key = key,
			consumer_secret = secret_key,
			access_token_key = token,
			access_token_secret = token_secret
		)
		self.logger = Logger(__name__) if logger is None else logger


	async def start(self):
		"""
		super super driver a super driver
		"""
		self.logger.info('Starting tweet_news.py.')

		while 1:
			self.logger.info('Starting update.')
			try:
				self.update()
			except Exception as e:
				self.logger.critical(e)
			self.logger.info('Finished update.')
			await asyncio.sleep(60)


	def update(self):
			# get latest id in database
			self.logger.debug('Fetching latest id.')
			try:
				res = self.database.fetchone('SELECT id FROM wowsnews ORDER BY id DESC')
			except Exception as e:
				self.logger.critical(e)
				res = None
			if res is None:
				self.logger.debug(f'No data found.')
				return
			latest_id_db = res[0]

			self.logger.debug(f'Latest id in database is {latest_id_db}.')
			# if result is None return
			if latest_id_db is None:
				self.logger.debug(f'No data found.')
				return
			# if self.latest_id is 0, update to latest_id_db and return
			elif self.latest_id is 0:
				self.logger.debug(f'Initializing latest id.')
				self.latest_id = latest_id_db
				return
			# if self.latest_id is same with latest_id_db return
			elif self.latest_id is latest_id_db:
				self.logger.debug('Data up to date.')
				return
			# else, send posts
			else:
				self.logger.debug('Sending status.')
				for i in range(self.latest_id + 1, latest_id_db + 1):
					self.logger.debug(f'i is {i}, id is {self.latest_id}, latest_id_db is {latest_id_db}')
					self._tweet(i)
				self.latest_id = latest_id_db


	def _tweet(self, id_db:int):
		"""
		Tweet from data in database of a given id. 
		"""
		self.logger.debug('starting tweet')

		try:
			res = self.database.fetchone(f'SELECT * FROM wowsnews WHERE id==?', (id_db,))
		except Exception as e:
			self.logger.critical(e)
			res = None
		self.logger.debug(f'result: {res}')
		if res is None:
			self.logger.debug('No result found.')
			return None
		
		source = res[1]
		title = res[2]
		description = res[3]
		# img = res[5]
		url = res[4]

		status = source + '最新情報!\n\n'
		# if title:
		# 	if len(title) < 140:
		# 		status += title
		# 	else:
		# 		status += title[:130] + '...'
		# else:
		# 	self.logger.critical(f'No title for {res}')

		if title:
			status += title + '\n'
		if description:
			status += description + '\n'
		if not url:
			self.logger.critical('No url found.')
			return
		elif not status:
			self.logger.critical('No title or description found.')
			return
		
		final_status = _create_final_status(status, url)

		# in case status length goes crazy
		assert calc_status_length(final_status) <= 280
		
		self.logger.debug(f'tweeting {status}')
		self.api.PostUpdate(final_status)
		self.logger.debug('tweeted.')


def _create_final_status(status, url):
	temp_status = f'{status}\n{url}'
	# if over 280 limit shorten status
	if not calc_status_length(temp_status) < 270:
		# using while as removing exceed_length not always work 
		# due to 2 length letters and 1 length letters
		while 270 < calc_status_length(temp_status):
			exceed_length = (270 - calc_status_length(temp_status)) // 2
			status = status[:exceed_length]

			temp_status = f'{status}...\n{url}'	
	final_status = temp_status
	return final_status