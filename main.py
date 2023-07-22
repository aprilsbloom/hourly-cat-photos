# <-- Imports -->
import time
import filetype
import json
import os
import tweepy
import pytumblr
import requests
from datetime import datetime
from mastodon import Mastodon


# <-- Functions -->
def fetch_config():
    temp_config = {
        "catapi-key": "",
        "twitter": {
            "username": "",
            "consumer_key": "",
            "consumer_secret": "",
            "access_token": "",
            "access_token_secret": ""
        },
        "tumblr": {
            "blogname": "",
            "consumer_key": "",
            "consumer_secret": "",
            "oauth_token": "",
            "oauth_token_secret": ""
        },
        "mastodon": {
            "api_url": "",
            "client_id": "",
            "client_secret": "",
            "access_token": ""
        }
    }

    try:
        with open('config.json', 'r', encoding='utf8') as file:
            temp_config.update(json.load(file))
            write_config(temp_config)
            return temp_config
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        log.error('Config file not found! Creating one')
        write_config(temp_config)
        os._exit(0)


def write_config(data):
    with open('config.json', 'w', encoding='utf8') as file:
        file.write(json.dumps(data, indent=4))


def post_mastodon():
    log.info('Uploading image to Mastodon')

    try:
        media = mastodon_client.media_post('cat')
        post = mastodon_client.status_post(status="", media_ids=media)
        log.success(f'Posted image to Mastodon! Link: {post["url"]}\n')
        return

    except Exception as e:
        log.error(f'Error while posting image to Mastodon: {e}')
        log.info('Trying again...\n')
        post_mastodon()
        return


def post_tumblr():
    print('')
    log.info('Uploading image to Tumblr')
    try:
        response = tumblr_client.create_photo(blogname="hourlycatphotos", state="published", tags=["Cat"], data="cat")
        log.success(f'Posted image to Tumblr! Link: https://tumblr.com/{TUMBLR["blogname"]}/{response["id"]}\n')
        post_mastodon()
    except Exception as e:
        log.error(f'Error while posting image to Tumblr: {e}')
        log.info('Trying again...\n')
        post_tumblr()
        return


def post_twitter():
    print('')
    log.info('Uploading image to Twitter')

    try:
        img = twitter_v1.chunked_upload(filename='cat', media_category="tweet_image").media_id_string
    except tweepy.errors.BadRequest as e:
        error_msg = str(e)
        log.error(f'Error while uploading image to Twitter: {error_msg}')
        log.info('Trying again...\n')
        fetch_img()
        return


    log.info('Tweeting image')
    try:
        response = twitter_v2.tweet.create(media_ids=[img])
    except Exception as e:
        log.error(f'Error while tweeting image: {e}')
        log.info('Trying again...\n')
        fetch_img()
        return

    if response.status_code == 201:
        log.success(f'Tweeted image! Link: https://twitter.com/{TWITTER["username"]}/status/{response.json()["data"]["id"]}')
    else:
        log.error('Error while tweeting image!')
        log.error(f'Error: {response.json()}\n')
        fetch_img()
        return

    post_tumblr()


def fetch_img():
    log.info('Fetching image')
    img = requests.get('https://api.thecatapi.com/v1/images/search?mime_types=jpg,png', headers={'x-api-key': CATAPI_KEY})

    try:
        img_url = img.json()[0]['url']
    except:
        log.error('Error while fetching image! Trying again...\n')
        fetch_img()
        return

    response = requests.get(img_url)

    try:
        os.remove('cat')
    except:
        pass

    with open('cat', 'wb') as _file:
        _file.write(response.content)

    _file = filetype.guess('cat')
    good_extensions = ['jpg', 'png', 'jpeg', 'webp']

    if _file.extension in good_extensions:
        post_twitter()
    else:
        log.error('Image is a gif! Trying again...\n')
        fetch_img()
        return


# <-- Classes -->
class Logger:
   def __init__(self):
       self.red = '\033[91m'
       self.yellow = '\033[93m'
       self.green = '\033[92m'
       self.grey = '\033[90m'
       self.reset = '\033[37m'

   def info(self, text):
       time = datetime.now().strftime('%D %H:%M:%S')
       print(f'{self.grey}[+]{self.reset} {time} - {text}')

   def error(self, text):
       time = datetime.now().strftime('%D %H:%M:%S')
       print(f'{self.red}[-]{self.reset} {time} - {text}')

   def warning(self, text):
       time = datetime.now().strftime('%D %H:%M:%S')
       print(f'{self.yellow}[!]{self.reset} {time} - {text}')

   def success(self, text):
       time = datetime.now().strftime('%D %H:%M:%S')
       print(f'{self.green}[+]{self.reset} {time} - {text}')


# <-- Variables -->
# Base
log = Logger()
config = fetch_config()
CATAPI_KEY = config["catapi-key"]


# Mastodon vars
MASTODON = {
    "api_url": config["mastodon"]["api_url"],
    "client_id": config["mastodon"]["client_id"],
    "client_secret": config["mastodon"]["client_secret"],
    "access_token": config["mastodon"]["access_token"]
}

mastodon_client = Mastodon(
    api_base_url = MASTODON["api_url"],
    client_id = MASTODON["client_id"],
    client_secret = MASTODON["client_secret"],
    access_token = MASTODON["access_token"]
)


# Tumblr vars
TUMBLR = {
    "blogname": config["tumblr"]["blogname"],
    "consumer_key": config["tumblr"]["consumer_key"],
    "consumer_secret": config["tumblr"]["consumer_secret"],
    "oauth_token": config["tumblr"]["oauth_token"],
    "oauth_token_secret": config["tumblr"]["oauth_token_secret"]
}

tumblr_client = pytumblr.TumblrRestClient(
    consumer_key = TUMBLR["consumer_key"],
    consumer_secret =TUMBLR["consumer_secret"],
    oauth_token = TUMBLR["oauth_token"],
    oauth_secret = TUMBLR["oauth_token_secret"]
)


# Twitter vars
TWITTER = {
    "username": config["twitter"]["username"],
    "consumer_key": config["twitter"]["consumer_key"],
    "consumer_secret": config["twitter"]["consumer_secret"],
    "access_token": config["twitter"]["access_token"],
    "access_token_secret": config["twitter"]["access_token_secret"]
}

tweepy_auth = tweepy.OAuth1UserHandler(
    consumer_key=TWITTER["consumer_key"],
    consumer_secret=TWITTER["consumer_secret"],
    access_token=TWITTER["access_token"],
    access_token_secret=TWITTER["access_token_secret"]
)


twitter_v1 = tweepy.API(tweepy_auth, wait_on_rate_limit=True)
twitter_v2 = tweepy.Client(consumer_key=TWITTER["consumer_key"], consumer_secret=TWITTER["consumer_secret"], access_token=TWITTER["access_token"], access_token_secret=TWITTER["access_token_secret"])


# <-- Main -->
# Waiting for it to be a new hour
previousHour = datetime.now().hour
while True:
    time.sleep(1)
    currentHour = datetime.now().hour
    if currentHour != previousHour:
        previousHour = currentHour
        fetch_img()
