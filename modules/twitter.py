import traceback

import tweepy
from tenacity import retry, retry_if_result, stop_after_attempt

from utils.globals import cfg, log


@retry(stop=stop_after_attempt(3), retry = retry_if_result(lambda result: not result))
def twitter():
	try:
		consumer_key = cfg.get('twitter.consumer_key')
		consumer_secret = cfg.get('twitter.consumer_secret')
		access_token = cfg.get('twitter.access_token')
		access_token_secret = cfg.get('twitter.access_token_secret')

		auth = tweepy.OAuth1UserHandler(
			consumer_key = consumer_key,
			consumer_secret = consumer_secret,
			access_token = access_token,
			access_token_secret = access_token_secret
		)

		v1 = tweepy.API(auth, wait_on_rate_limit=True)
		v2 = tweepy.Client(
			consumer_key=consumer_key,
			consumer_secret=consumer_secret,
			access_token=access_token,
			access_token_secret=access_token_secret
		)
	except Exception:
		log.error(f'Error while authenticating to Twitter: {traceback.format_exc()}')
		log.info('Trying again...\n')
		return

	log.info('Uploading image to Twitter')

	try:
		img = v1.chunked_upload(filename='img.jpg', media_category="tweet_image").media_id_string
	except Exception:
		log.error(f'An error occured while uploading the image to Twitter: {traceback.format_exc()}')
		log.info('Trying again...\n')
		return

	log.info('Posting image to Twitter')
	try:
		response = v2.create_tweet(text = "", media_ids = [ img ])
	except Exception:
		log.error(f'An error occured while posting the image on Twitter: {traceback.format_exc()}')
		log.info('Trying again...\n')
		return

	if response.data and response.errors == []: # type: ignore
		log.success(f'Tweeted image! Link: https://twitter.com/i/status/{response.data["id"]}') # type: ignore
		return True
	else:
		log.error('Error while posting the image!')
		log.error(f'Error: {response.errors}\n') # type: ignore
		return