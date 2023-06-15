#!/usr/bin/env python3

import sys
import logging
import re
import os
import subprocess
import time
from pydub import AudioSegment
from pydub.playback import play
from pyrogram import Client, filters


logging.basicConfig(format="%(asctime)s %(message)s")
logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stderr))

class Config:
    def __init__(self):
        self.app_id = os.environ.get("TELEGRAM_API_ID")
        self.app_hash = os.environ.get("TELEGRAM_API_HASH")
        self.phone = os.environ.get("TELEGRAM_PHONE_NUMBER").replace(" ", "").strip()
        self.regex = os.environ.get("TELEGRAM_MESSAGE_REGEX")
        self.session_name = ".tg"
        self.tg_group = os.environ.get("TELEGRAM_MONITOR_GROUP")
        self.action = os.environ.get("ACTION")

config = Config()
sound_file = AudioSegment.from_mp3(os.path.join(os.path.dirname(__file__), "alarm.mp3"))
app = Client(config.session_name, config.app_id, config.app_hash, phone_number=config.phone)
message_regex = re.compile(config.regex, re.IGNORECASE)

@app.on_message(filters.chat(config.tg_group) & filters.regex(message_regex))
def handle_message(_client, message):
    logger.debug("Received message: %r", message)
    play(sound_file)
    if config.action:
        start_ts  = time.time()
        return_code = subprocess.call(["sh", "-c", config.action])
        logger.info('"%s" return code %d', config.action, return_code)

while True:
    try:
        logger.info("Starting monitor for %s in %s, phone %s, action command \"%s\"", config.regex, config.tg_group, config.phone, config.action)
        app.run()
    except KeyboardInterrupt:
        logging.info("Terminating...")
        break
    except Exception as e:
        logger.error(e)
        play(sound_file)
        time.sleep(30)
        continue
