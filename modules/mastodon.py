import traceback

from mastodon import Mastodon
from tenacity import retry, retry_if_result, stop_after_attempt

from utils.globals import cfg, log


@retry(stop=stop_after_attempt(3), retry = retry_if_result(lambda result: not result))
def mastodon():
	try:
		mastodon = Mastodon(
			api_base_url = cfg.get('mastodon.api_url'),
			client_id = cfg.get('mastodon.client_id'),
			client_secret = cfg.get('mastodon.client_secret'),
			access_token = cfg.get('mastodon.access_token')
		)
	except Exception:
		log.error(f'An error occurred while authenticating to Mastodon: {traceback.format_exc()}')
		log.info('Trying again...\n')
		return

	log.info('Posting image to Mastodon')

	try:
		media = mastodon.media_post('img.jpg')
		post = mastodon.status_post(status="", media_ids=media)
		log.success(f'Posted image to Mastodon! Link: {post["url"]}\n')
		return True
	except Exception:
		log.error(f'An error occurred while posting the image on Mastodon: {traceback.format_exc()}')
		log.info('Trying again...\n')
		return