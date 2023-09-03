import re
import time
import filetype
import json
import os
import tweepy
import pytumblr
import requests
from datetime import datetime
from mastodon import Mastodon
from utils import fetch_data, write_data, Logger
from tenacity import retry, stop_after_attempt, retry_if_result


log = Logger()
config = fetch_data()
CATAPI_KEY = config["catapi-key"]


# Mastodon vars
MASTODON_CFG = {
    "api_url": config["mastodon"]["api_url"],
    "client_id": config["mastodon"]["client_id"],
    "client_secret": config["mastodon"]["client_secret"],
    "access_token": config["mastodon"]["access_token"]
}

mastodon = Mastodon(
    api_base_url = MASTODON_CFG["api_url"],
    client_id = MASTODON_CFG["client_id"],
    client_secret = MASTODON_CFG["client_secret"],
    access_token = MASTODON_CFG["access_token"]
)


# Tumblr vars
TUMBLR_CFG = {
    "blogname": config["tumblr"]["blogname"],
    "consumer_key": config["tumblr"]["consumer_key"],
    "consumer_secret": config["tumblr"]["consumer_secret"],
    "oauth_token": config["tumblr"]["oauth_token"],
    "oauth_token_secret": config["tumblr"]["oauth_token_secret"]
}

tumblr = pytumblr.TumblrRestClient(
    consumer_key = TUMBLR_CFG["consumer_key"],
    consumer_secret = TUMBLR_CFG["consumer_secret"],
    oauth_token = TUMBLR_CFG["oauth_token"],
    oauth_secret = TUMBLR_CFG["oauth_token_secret"]
)


# Twitter vars
TWITTER_CFG = {
    "username": config["twitter"]["username"],
    "consumer_key": config["twitter"]["consumer_key"],
    "consumer_secret": config["twitter"]["consumer_secret"],
    "access_token": config["twitter"]["access_token"],
    "access_token_secret": config["twitter"]["access_token_secret"]
}

tweepy_auth = tweepy.OAuth1UserHandler(
    consumer_key = TWITTER_CFG["consumer_key"],
    consumer_secret = TWITTER_CFG["consumer_secret"],
    access_token = TWITTER_CFG["access_token"],
    access_token_secret = TWITTER_CFG["access_token_secret"]
)


twitter_v1 = tweepy.API(tweepy_auth, wait_on_rate_limit=True)
twitter_v2 = tweepy.Client(consumer_key=TWITTER_CFG["consumer_key"], consumer_secret=TWITTER_CFG["consumer_secret"], access_token=TWITTER_CFG["access_token"], access_token_secret=TWITTER_CFG["access_token_secret"])

def fetch_img():
    log.info('Fetching image from https://thecatapi.com')

    orig_headers = {
        'x-api-key': CATAPI_KEY
    }
    orig_res = requests.get('https://api.thecatapi.com/v1/images/search?mime_types=jpg,png', headers=orig_headers)
    orig_data = orig_res.json()

    if isinstance(orig_data, list):
        orig_data = orig_data[0]

    img_url = orig_data['url']
    img_res = requests.get(img_url)

    if os.path.exists('img.jpg'):
        try:
            os.remove('img.jpg')
        except:
            log.error('Failed to remove img.jpg')

    with open('img.jpg', 'wb') as f:
        f.write(img_res.content)

    good_file_extensions = ['jpg', 'png', 'jpeg', 'webp']
    img_type = filetype.guess('img.jpg')

    if img_type.extension in good_file_extensions:
        log.success('Fetched image successfully!')
        post_twitter()
    else:
        log.error('Failed to fetch image!')
        return False

@retry(stop=stop_after_attempt(3), retry = retry_if_result(lambda result: result is False))
def post_twitter():
    log.info('Posting image to Twitter')

    try:
        img = twitter_v1.chunked_upload(filename='img.jpg', media_category="tweet_image").media_id_string
    except Exception as e:
        error_msg = str(e)
        log.error(f'Error while uploading image to Twitter: {error_msg}')
        log.info('Trying again...\n')
        return

    log.info('Tweeting image')
    try:
        response = twitter_v2.create_tweet(text="", media_ids=[img])
    except Exception as e:
        log.error(f'Error while tweeting image: {e}')
        log.info('Trying again...\n')
        return

    if response.data and response.errors == []:
        log.success(f'Tweeted image! Link: https://twitter.com/i/status/{response.data["id"]}')
    else:
        log.error('Error while tweeting image!')
        log.error(f'Error: {response.errors}\n')
        return

    post_tumblr()

@retry(stop=stop_after_attempt(3), retry = retry_if_result(lambda result: result is False))
def post_tumblr():
    log.info('Posting image to Tumblr')

    try:
        response = tumblr.create_photo(TUMBLR_CFG["blogname"], state="published", tags=['cat', 'cat_photo', 'cat_photographer', 'cat_photography', 'cat_photos', 'catlife', 'catlove', 'catlover', 'catlovers', 'catoftheday', 'catphoto', 'catphotographer', 'catphotography', 'catphotos', 'cats', 'cats_of_instagram', 'catsofinstagram', 'catsoftheworld','hourly_cat', 'hourly_cat_photo', 'hourly_cat_photography', 'hourly_cat_photos', 'hourly_cats', 'hourlycat', 'hourlycatphoto', 'hourlycatphotography', 'hourlycatphotos', 'hourlycats'], data="img.jpg")
        log.success(f'Posted image to Tumblr! Link: https://{TUMBLR_CFG["blogname"]}.tumblr.com/post/{response["id"]}')
        post_mastodon()
    except Exception as e:
        log.error(f'Error while posting image to Tumblr: {e}')
        log.info('Trying again...\n')
        return

@retry(stop=stop_after_attempt(3), retry = retry_if_result(lambda result: result is False))
def post_mastodon():
    log.info('Posting image to Mastodon')

    try:
        media = mastodon.media_post('img.jpg')
        post = mastodon.status_post(status="", media_ids=media)
        log.success(f'Posted image to Mastodon! Link: {post["url"]}\n')
        return
    except Exception as e:
        log.error(f'Error while posting image to Mastodon: {e}')
        log.info('Trying again...\n')
        return


# <-- Main -->
# Waiting for it to be a new hour
log.info('Waiting for it to be a new hour...')
previousHour = datetime.now().hour
while True:
    time.sleep(1)
    currentHour = datetime.now().hour
    if currentHour != previousHour:
        previousHour = currentHour
        log.info('New hour! Posting...\n')
        fetch_img()