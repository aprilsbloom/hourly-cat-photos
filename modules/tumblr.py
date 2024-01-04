import pytumblr
import traceback
from tenacity import retry, stop_after_attempt, retry_if_result
from utils.globals import CAT_TAGS, log, cfg

@retry(stop=stop_after_attempt(3), retry = retry_if_result(lambda result: result is False))
def tumblr():
	try:
		blogname = cfg.get('tumblr.blogname')
		tumblr = pytumblr.TumblrRestClient(
			consumer_key = cfg.get('tumblr.consumer_key'),
			consumer_secret = cfg.get('tumblr.consumer_secret'),
			oauth_token = cfg.get('tumblr.oauth_token'),
			oauth_secret = cfg.get('tumblr.oauth_token_secret')
		)
	except Exception as e:
		log.error(f'An error occurred while authenticating to Tumblr: {traceback.format_exc()}')
		log.info('Trying again...\n')
		return

	log.info('Posting image to Tumblr')

	try:
		response = tumblr.create_photo(
			blogname = blogname,
			state = "published",
			tags = CAT_TAGS,
			data = "img.jpg"
		)
		log.success(f'Posted image to Tumblr! Link: https://{blogname}.tumblr.com/post/{response["id"]}')
	except Exception as e:
		log.error(f'An error while posting the image on Tumblr: {traceback.format_exc()}')
		log.info('Trying again...\n')
		return

