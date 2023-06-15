#!/usr/bin/env python3

import sys
import logging
import re
import os
import subprocess
from pydub import AudioSegment
from pydub.playback import play
from pyrogram import Client, filters

# Logger initalizer
logging.basicConfig(format="%(asctime)s %(message)s")
logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stderr))

app_id = os.environ.get("TELEGRAM_API_ID")
app_hash = os.environ.get("TELEGRAM_API_HASH")
phone = os.environ.get("TELEGRAM_PHONE_NUMBER").replace(" ", "").strip()
pattern = os.environ.get("TELEGRAM_MESSAGE_REGEX")
session_name = '.tg'  # Choose a name for your session
tg_group = os.environ.get("TELEGRAM_MONITOR_GROUP")
action = os.environ.get("ACTION")

message_regex = re.compile(pattern, re.IGNORECASE)

sound = AudioSegment.from_mp3(os.path.join(os.path.dirname(__file__), "alarm.mp3")) # Sound file

app = Client(session_name, app_id, app_hash, phone_number=phone)

@app.on_message(filters.chat(tg_group) & filters.regex(message_regex))
def handle_message(client, message):
    logger.debug("Received message: %r", message)
    play(sound)
    if action:
        subprocess.call(["sh", "-c", action])

while True:
    try:
        logger.info("Starting monitor for %s in %s", pattern, tg_group)
        app.run()
    except InterruptedError:
        break
    except Exception as e:
        logger.error(e)
        play(sound)
        time.sleep(30)
        continue
