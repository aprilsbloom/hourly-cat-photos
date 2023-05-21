# Hourly Cat Photos

This repository serves as the source code for [@HourlyCatPhotos](https://twitter.com/HourlyCatPhotos), a Twitter bot I run that posts a new cat photo every hour.
It fetches images from [TheCatAPI](https://thecatapi.com/), and posts them to Twitter using the [Tweepy](https://www.tweepy.org/) library.

## Purpose

This repo serves as a learning experience for others who want to learn how to create a Twitter bot using Python.
It also serves as a code example of how to upload media to Twitter with only V2 of the Twitter API.

## Setup

Run `pip install -r requirements.txt` to install the required dependencies.

Then, run `main.py`. It will create a file by the name of `config.json`, which you will need to fill out with your own API keys.

Once you have filled out `config.json`, run `main.py` again - it will then post photos every hour.
