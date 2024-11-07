from typing import Final

from utils.config import Config
from utils.logger import Logger

# ---- Misc ---- #
CAT_TAGS = ["cat", "cat_photo", "cat_photographer", "cat_photography", "cat_photos", "catlife", "catlove", "catlover", "catlovers", "catoftheday", "catphoto", "catphotographer", "catphotography", "catphotos", "cats", "cats_of_instagram", "catsofinstagram", "catsoftheworld", "hourly_cat", "hourly_cat_photo", "hourly_cat_photography", "hourly_cat_photos", "hourly_cats", "hourlycat", "hourlycatphoto", "hourlycatphotography", "hourlycatphotos", "hourlycats"]
IMG_EXTENSIONS = ["jpg", "png", "jpeg", "webp"]
IMG_PATH = 'img.jpg'
BASE_HEADERS: Final = {
	"User-Agent": "HourlyCatPhotos (https://github.com/aprilsbloom/hourly-cat-photos)",
	"Accept": "*/*",
	"Accept-Encoding": "gzip, deflate, br",
	"Connection": "keep-alive",
}

log = Logger()
cfg = Config(
	logger=log,
	path="config.json",
	default={
		"catapi-key": "",
		"twitter": {
			"enabled": False,
			"username": "",
			"consumer_key": "",
			"consumer_secret": "",
			"access_token": "",
			"access_token_secret": "",
		},
		"tumblr": {
			"enabled": False,
			"blogname": "",
			"consumer_key": "",
			"consumer_secret": "",
			"oauth_token": "",
			"oauth_token_secret": "",
		},
		"mastodon": {
			"enabled": False,
			"api_url": "",
			"client_id": "",
			"client_secret": "",
			"access_token": "",
		},
		"bluesky": {
			"enabled": False,
			"username": "",
			"app_password": "",
		}
	},
)
