import json
import os
from pathlib import Path
from typing import Any, Optional, Union

from utils.logger import Logger


class Config:
	def __init__(
		self,
		logger: Logger,
		path: Union[str, os.PathLike, Path],
		default: dict = {},
	) -> None:
		self.log = logger
		self.cfg_path: Path = Path(path)
		self.default: dict = default
		self.config: dict = self.load_config(path)

	def load_config(self, path: Union[str, os.PathLike, Path]) -> dict:
		path = self.cfg_path

		# create path if doesn't exist
		if not path.exists():
			path.touch()

		# load the config file
		try:
			with open(path, "r", encoding="utf8") as f:
				config = json.loads(f.read())
		except json.JSONDecodeError:
			config = self.default
		except FileNotFoundError:
			self.config = self.default
			self.write_config()
			self.log.error("Config file not found, creating a new one. Please fill it out and restart the bot.")
			os._exit(1)

		self.config = deep_merge(self.default, config)
		self.write_config()

		# return the config file
		return self.config

	def write_config(
		self,
		format: Optional[str] = "pretty",
		sort_keys: Optional[bool] = False
	) -> None:
		# set the indent level and separators based on the format provided
		indent_level = 2 if format == "pretty" else None
		separators = None if format == "pretty" else (",", ":")
		sort_keys = sort_keys if isinstance(sort_keys, bool) else False
		path = self.cfg_path

		# if the path doesn't exist, create it
		if not path.exists():
			path.touch()

		# write the config file
		with open(path, "w", encoding="utf8") as f:
			f.write(
				json.dumps(
					self.config,
					indent=indent_level,
					separators=separators,
					sort_keys=sort_keys,
			))

	def getter(self, key, obj=None):
		keys = key.split(".")

		if not obj or not isinstance(obj, dict):
			return None

		if len(keys) == 1:
			return obj.get(key)

		new_key = keys[1:]
		return self.getter(".".join(new_key), obj.get(keys[0]))

	def setter(self, key, value, obj):
		keys = key.split(".")

		if len(keys) == 1:
			obj[key] = value

		else:
			newKey = keys[0]
			obj[newKey] = self.setter(".".join(keys[1:]), value, obj.get(newKey))

		return obj

	def get(self, key) -> Any:
		self.config = deep_merge(self.default, self.config)
		self.write_config()
		return self.getter(key, self.config)

	def set(self, key, value):
		self.config = deep_merge(self.default, self.config)
		self.config = self.setter(key, value, self.config)
		self.write_config()


def deep_merge(obj1, obj2):
	# create new object that we merge to
	merged_object = {}

	# iterate over the first objects keys
	for key, val in obj2.items():
		# if key is in second object, and it's another object, merge them recursively
		if key in obj1 and isinstance(val, dict) and isinstance(obj1[key], dict):
			merged_object[key] = deep_merge(obj1[key], val)

		# if key is not in second object, or it's not a object/list, add it to the merged object
		else:
			merged_object[key] = val

	# iterate over the second objects keys
	for key, val in obj1.items():
		# If the key is not already in the merged object, add it
		if key not in merged_object:
			merged_object[key] = val

	return merged_object