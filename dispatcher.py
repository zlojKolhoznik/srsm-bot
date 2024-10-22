import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import constants

logging.basicConfig(level=logging.INFO)

if not constants.PROD_BOT_TOKEN:
    exit('No bot token provided')

token = constants.PROD_BOT_TOKEN

bot = Bot(token=token, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
