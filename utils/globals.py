from typing import Final

from utils.config import Config
from utils.logger import Logger

# ---- Misc ---- #
SIZE_LIMIT = 10000000  # Mastodon's file size limit is 10MB
CATBOX_URL = "https://catbox.moe/user/api.php"  # Catbox.moe API URL
CAT_TAGS = ["cat", "cat_photo", "cat_photographer", "cat_photography", "cat_photos", "catlife", "catlove", "catlover", "catlovers", "catoftheday", "catphoto", "catphotographer", "catphotography", "catphotos", "cats", "cats_of_instagram", "catsofinstagram", "catsoftheworld", "hourly_cat", "hourly_cat_photo", "hourly_cat_photography", "hourly_cat_photos", "hourly_cats", "hourlycat", "hourlycatphoto", "hourlycatphotography", "hourlycatphotos", "hourlycats"]
IMG_EXTENSIONS = ["jpg", "png", "jpeg", "webp"]

log = Logger()
cfg = Config(
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
  },
)

# ---- Requests ---- #
# Base browser headers for requests
BASE_HEADERS: Final = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
  "Accept": "*/*",
  "Accept-Encoding": "gzip, deflate, br",
  "Connection": "keep-alive",
}
