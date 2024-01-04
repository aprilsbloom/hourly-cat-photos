import tweepy
import traceback
from tenacity import retry, stop_after_attempt, retry_if_result
from utils.globals import log, cfg

@retry(stop=stop_after_attempt(3), retry = retry_if_result(lambda result: result is False))
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
	except Exception as e:
		log.error(f'Error while authenticating to Twitter: {traceback.format_exc()}')
		log.info('Trying again...\n')
		return

	log.info('Uploading image to Twitter')

	try:
		img = v1.chunked_upload(filename='img.jpg', media_category="tweet_image").media_id_string
	except Exception as e:
		log.error(f'An error occured while uploading the image to Twitter: {traceback.format_exc()}')
		log.info('Trying again...\n')
		return

	log.info('Posting image to Twitter')
	try:
		response = v2.create_tweet(text = "", media_ids = [ img ])
	except Exception as e:
		log.error(f'An error occured while posting the image on Twitter: {traceback.format_exc()}')
		log.info('Trying again...\n')
		return

	if response.data and response.errors == []:
		log.success(f'Tweeted image! Link: https://twitter.com/i/status/{response.data["id"]}')
	else:
		log.error('Error while posting the image!')
		log.error(f'Error: {response.errors}\n')
		return