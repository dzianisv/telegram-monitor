#!/usr/bin/env python3

import sys
import logging
import re
import os
import subprocess
import time
import argparse
import json
import dataclasses

from pydub import AudioSegment
from pydub.playback import play
from pyrogram import Client, filters



logging.basicConfig(format="%(asctime)s %(message)s")
logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stderr))


@dataclasses.dataclass
class Monitor:
    regex: str
    chat: str
    actions: list

class Config:
    def __init__(self, config_file: str):
        self.session_name = ".tg"
        self.monitors = []

        if os.environ.get("TELEGRAM_MESSAGE_REGEX"):
            m = Monitor(regex=re.compile(os.environ.get("TELEGRAM_MESSAGE_REGEX"), re.IGNORECASE), chat=os.environ.get("TELEGRAM_MONITOR_GROUP"), actions=[os.environ.get("ACTION")])
            self.monitors.append(m)

        if config_file:
            with open(config_file, 'r', encoding='utf8') as fd:
                config_obj = json.load(fd)

            for monitor in config_obj.get("monitors"):
                self.monitors.append(Monitor(
                    regex=re.compile(monitor["regex"], re.IGNORECASE),
                    chat=monitor["chat"],
                    actions=monitor["actions"]
                    )
                )

            if 'telegram' in config_obj:
                telegram_obj = config_obj['telegram']
                self.app_hash = telegram_obj.get('api_hash')
                self.app_id = telegram_obj.get('app_id')
                self.phone = telegram_obj.get('phone_number')

        self.app_id = os.environ.get("TELEGRAM_API_ID", self.app_id)
        self.app_hash = os.environ.get("TELEGRAM_API_HASH", self.app_hash)
        self.phone = os.environ.get("TELEGRAM_PHONE_NUMBER", self.phone).replace(" ", "").strip()


        if len(self.monitors) == 0:
            raise Exception("Monitors are not configured")

        if not self.app_hash or  not self.app_id or not self.phone:
            raise Exception("Telegram is not configured")

def play_ogg(file: str):
    sound_file = AudioSegment.from_ogg(os.path.join(os.path.dirname(__file__), "sounds", file))
    play(sound_file)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="config.json")
    args = parser.parse_args()

    config = Config(args.config)

    app = Client(config.session_name, config.app_id, config.app_hash, phone_number=config.phone)

    @app.on_message()
    def handle_message(_client, message):
        for m in config.monitors:
            if message.chat.username != m.chat or not m.regex.match(message.text):
                continue

            # message https://docs.pyrogram.org/api/types/Message
            logger.debug("Received message %r", message)

            actions = []
            env = os.environ.copy()
            env["TELEGRAM_MESSAGE"] = message.text
            env["TELEGRAM_CHAT"] = message.chat.username
            for action in m.actions:
                actions.append(subprocess.Popen(["sh", "-c", action], env=env))

            play_ogg("match.ogg")
            play_ogg("alarm.ogg")

            for a in actions:
                a.wait()

    while True:
        try:
            logger.info("Started")
            app.run()
            break
        except KeyboardInterrupt:
            logging.info("Terminating...")
            break
        except Exception as e:
            logger.error(e)
            play_ogg("error.ogg")
            time.sleep(30)
            continue

main()