import asyncio
import os
from datetime import datetime, timedelta

import filetype
import requests

from modules import mastodon, tumblr, twitter
from utils.globals import IMG_EXTENSIONS, cfg, log

async def fetch_img():
	# ensure at least one site is enabled otherwise we're wasting our time
	if not cfg.get('twitter.enabled') and not cfg.get('mastodon.enabled') and not cfg.get('tumblr.enabled'):
		log.error('No sites are enabled. Please enable at least one site in config.json.')
		return

	log.info('Fetching image from https://thecatapi.com')
	res = requests.get(url = 'https://api.thecatapi.com/v1/images/search?mime_types=jpg,png', headers = { 'x-api-key': cfg.get('catapi-key') })
	data = res.json()

	# catapi sometimes returns things in a list for some reason
	if isinstance(data, list):
		data = data[0]

	# check if the request was successful by checking for the 'url' key
	url = data.get('url')
	if not url:
		log.error('Failed to fetch image.')
		return False

	# if everything is successful, fetch the image and write it to a file
	res = requests.get(url)
	if os.path.exists('img.jpg'):
		try:
			os.remove('img.jpg')
		except Exception:
			log.error('Failed to remove img.jpg.')

	try:
		with open('img.jpg', 'wb') as f:
			f.write(res.content)
	except Exception:
		log.error('Failed to write the fetched image.')
		return

	# check if the image is actually supported
	img_type = filetype.guess('img.jpg')
	if img_type is None or img_type.extension not in IMG_EXTENSIONS:
		log.error('TheCatAPI returned an invalid image.')
		return False

	# if everything is successful, post the image to all the platforms
	if cfg.get('twitter.enabled'):
		twitter()

	if cfg.get('mastodon.enabled'):
		mastodon()

	if cfg.get('tumblr.enabled'):
		tumblr()

async def main():
	while True:
		current_time = datetime.now()
		goal_timestamp = current_time + timedelta(hours = 1, minutes = -current_time.minute)
		log.info(f'Posting at: {goal_timestamp.strftime('%H:%M:%S')}')
		await asyncio.sleep((goal_timestamp - current_time).total_seconds())
		await fetch_img()

if __name__ == '__main__':
	asyncio.run(main())