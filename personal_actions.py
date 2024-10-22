import asyncio

from aiogram import filters
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

import custom_filters
from constants import PROD_CHAT_ID, PROD_BOT_ID
from dispatcher import dp
from db import BotDB

from fsm import QuestionTypes

db = BotDB('users.db')


def make_row_keyboard(items: list[str]):
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], one_time_keyboard=True, resize_keyboard=True)


def make_inline_keyboard(items: dict[str, str], rows: list[int]):
    """
    :param items: Keyboard buttons, key - button text, value - callback data
    :param rows:  Number of buttons in each row
    :return:  InlineKeyboardMarkup
    """

    buttons = [InlineKeyboardButton(text=key, callback_data=value) for key, value in items.items()]
    keyboard = []
    for i in range(len(rows)):
        row = []
        for j in range(rows[i]):
            row.append(buttons[0])
            buttons = buttons[1:]
        keyboard.append(row)
    if len(buttons) > 0:
        keyboard.append(buttons)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


question_types = ['Еко НАУ 🌎', 'СР СМ ✈️', 'Інше ℹ️']
question_type_keyboard = make_row_keyboard(question_types)
back_to_types = 'Назад до тем ⬅️'
back_to_type_keyboard = make_row_keyboard([back_to_types])


@dp.message(filters.CommandStart())
async def start(message: Message, state: FSMContext):
    await message.bot.send_message(chat_id=message.chat.id,
                                   text='Привіт! 👋 \nЦей бот дасть тобі можливість поставити питання '
                                        'твоїй студраді! Для цього просто напиши питання боту і ми '
                                        'відправимо його студраді',
                                   reply_markup=question_type_keyboard)
    await state.set_state(QuestionTypes.choosing_type)


@dp.message(custom_filters.ChatId(PROD_CHAT_ID), filters.Command('activate_punkt'))
async def activate_punkt(message: Message, state: FSMContext):
    inactive_punkts = db.get_inactive_punkts()
    punkts_elements = dict()
    for punkt in inactive_punkts:
        punkts_elements[punkt[0]] = punkt[0]
    punkts_keyboard = make_inline_keyboard(punkts_elements, [2, 2])
    await message.bot.send_message(chat_id=message.chat.id, text='Оберіть номер пункту, який хочете активувати', reply_markup=punkts_keyboard)
    await state.set_state(QuestionTypes.choosing_activating_punkt)


@dp.message(custom_filters.PrivateChat(), StateFilter(QuestionTypes.choosing_type))
async def choose_question_type(message: Message, state: FSMContext):
    if message.text not in question_types:
        await message.bot.send_message(chat_id=message.chat.id,
                                       text='Невідома тема, будь ласка, оберіть одну із наявних тем',
                                       reply_markup=question_type_keyboard)
        return
    await state.update_data(question_type=message.text)
    await state.set_state(QuestionTypes.writing_question)
    await message.bot.send_message(chat_id=message.chat.id,
                                   text='Тему обрано! Тепер напишіть Ваше питання студраді',
                                   reply_markup=back_to_type_keyboard)


@dp.message(custom_filters.PrivateChat(), StateFilter(QuestionTypes.writing_question))
async def send_question(message: Message, state: FSMContext):
    # TODO: коли будемо запускати по всім гуртожиткам, тут треба буде додати щоб писало ще де людинка живе
    if message.text == back_to_types:
        await message.bot.send_message(chat_id=message.chat.id,
                                       text='Оберіть іншу тему питання',
                                       reply_markup=question_type_keyboard)
        await state.set_state(QuestionTypes.choosing_type)
        return
    state_data = await state.get_data()
    full_text = (f'Повідомлення по темі "{state_data["question_type"]}" (щоб надіслати відповідь, реплайніть це '
                 f'повідомлення):\n\n')
    contacts_string = f'👤 {message.from_user.full_name}, '
    if message.from_user.username is not None:
        contacts_string += f'тег: @{message.from_user.username}, '
    contacts_string += f'#id{message.from_user.id}.'
    if message.text is not None:
        full_text += f'<i>{message.text}\n\n</i>'
    full_text += contacts_string
    await message.bot.send_message(PROD_CHAT_ID, text=full_text)
    if message.text is None:
        await message.copy_to(PROD_CHAT_ID)
    sent_message = await message.bot.send_message(chat_id=message.chat.id,
                                                  text='Дякуємо! Ваше повідомлення доставлене до студради ✅\n'
                                                       'Очікуйте на відповідь! 📩',
                                                  reply_markup=question_type_keyboard)
    await state.clear()
    await state.set_state(QuestionTypes.choosing_type)


@dp.message(custom_filters.PrivateChat())
async def inform_about_types(message: Message, state: FSMContext):
    if message.text not in question_types:
        await message.bot.send_message(chat_id=message.chat.id,
                                       text='В боті наявні теми для питань, для того, щоб задати питання, '
                                            'спочатку оберіть тему нижче!',
                                       reply_markup=question_type_keyboard)
        await state.set_state(QuestionTypes.choosing_type)
    else:
        await state.update_data(question_type=message.text)
        await state.set_state(QuestionTypes.writing_question)
        await message.bot.send_message(chat_id=message.chat.id,
                                       text='Тему обрано! Тепер напишіть Ваше питання студраді',
                                       reply_markup=back_to_type_keyboard)


@dp.message(custom_filters.ChatId(PROD_CHAT_ID), custom_filters.ReplyTo(PROD_BOT_ID))
async def send_answer(message: Message):
    replied_message = message.reply_to_message
    user_id = get_user_id_from_message_text(replied_message.html_text)
    if user_id == -1:
        sent_message = await message.reply(text='😖 На жаль, не вдалось знайти, кому потрібно надіслати відповідь.'
                                                'Реплайніть повідомлення з посиланням на користувача '
                                                '(попереднє повідомлення бота). '
                                                'Якщо не допомогло, напишіть відповідь користувачу в особисті '
                                                'або зв\'яжіться з командою')
        await asyncio.sleep(15)
        await sent_message.delete()
        return
    reply_text = '✅ Вам надійшла відповідь на питання '
    rows = replied_message.text.split('\n')
    rows_count = len(rows)
    is_text_question = rows_count > 1 and rows[rows_count - 1] != ''
    if is_text_question:
        reply_text += '"<i>' + rows[rows_count - 1] + f'</i>":'
    else:
        reply_text += 'без тексту:'
    if message.text is not None:
        reply_text += f'\n<b>{message.text}</b>'
    await message.bot.send_message(chat_id=user_id, text=reply_text, reply_markup=question_type_keyboard)
    if message.text is None:
        await message.copy_to(chat_id=user_id)
    sent_message = await message.reply('✅ Відповідь успішно надіслано')
    await asyncio.sleep(10)
    await message.bot.delete_message(chat_id=message.chat.id, message_id=sent_message.message_id)


def get_user_id_from_message_text(html: str) -> int:
    anchor = '#id'
    if html.rfind(anchor) == -1:
        return -1
    user_id_index = html.find(anchor) + len(anchor)
    html = html[user_id_index:]
    end_id_index = html.rfind('.')
    user_id = html[:end_id_index]
    return int(user_id.strip())
