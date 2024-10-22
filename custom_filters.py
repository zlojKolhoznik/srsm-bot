from aiogram.filters import Filter
from aiogram.types import Message


class PrivateChat(Filter):
    async def __call__(self, message: Message):
        return message.chat.type == "private"


class GroupChat(Filter):
    async def __call__(self, message: Message):
        return message.chat.type == "group" or message.chat.type == "supergroup"


class ChatId(Filter):
    def __init__(self, chat_id: int):
        self.chat_id = chat_id

    async def __call__(self, message: Message):
        return message.chat.id == self.chat_id


class ReplyTo(Filter):
    def __init__(self, user_id: int):
        self.user_id = user_id

    async def __call__(self, message: Message):
        return message.reply_to_message is not None and message.reply_to_message.from_user.id == self.user_id
