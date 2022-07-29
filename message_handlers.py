import logging
import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.executor import start_webhook
from service_bot import states

from service_bot.states import ChatMode
from config import service_bot, dp, client_bot, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT
from service_bot.models import Event


admin = '@arrriinak'

@dp.message_handler(commands=["start"])
async def start(message: types.Message, state: FSMContext):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    exit_but = types.KeyboardButton("Вийти з чату")
    discuss_salary = types.KeyboardButton("Підтвердити ціну")
    markup.add(exit_but, discuss_salary)
    print('start')
    print(message.text)
    print(message.text[33:])
    print(re.match(r'^/start test(\d*)_e(\d+)$', message.text[33:]).groups())
    if len(message.text) > 7:
        await ChatMode.event.set()
        await ChatMode.ChatId.set()
        print(message.text)
        b = message.text[33:]
        print(re.match(r'^/start test(\d*)_e(\d+)$', b).groups())
        chat_id, event_id = re.match(r'^/start test(\d*)_e(\d+)$', b).groups()
        #print(chat_id)
        print(event_id)
        event = Event.get(event_id)
        await message.answer(
            f"Ласкаво просимо, {message.from_user.first_name}"
            f" {message.from_user.last_name}!"
        )

        #await service_bot.send_message(
         #   message.from_user.id,
         #   f'Ви відгункнулися на цей пост: \n{event.name}'
         #   f'\n{event.description}' f'\nЗарплата: {event.salary}'
        #)
        await message.answer(
            'Війшли в режим чату, напишіть ваше повідомлення',
            reply_markup=markup
            )
        async with state.proxy() as data:
            data['ChatId'] = chat_id
            data['event'] = event_id
    else:
        await message.answer(
            f"Ласкаво просимо, {message.from_user.first_name}"
            f" {message.from_user.last_name}!"
        )




@dp.message_handler(state=ChatMode.ChatId)
async def state_chatid(message: types.Message, state: FSMContext):
    markup = InlineKeyboardMarkup()
    async with state.proxy() as data:
        chat_id = data.get('ChatId')
    if message.text == 'Вийти з чату':
        await state.finish()
        return await message.answer('Ви завершили розмову', reply_markup=ReplyKeyboardRemove(True))
    if message.text == 'Підтвердити ціну':
        await message.answer("Підтвердіть ціну, написавши її тільки цифрами(Приклад: 100)")
        return await states.ChatMode.price.set()
    else:
        reply_button = InlineKeyboardButton('Відповісти', callback_data=f'user_id{message.from_user.id}')
        markup.add(reply_button)
        mess = f'Вам надійшло повідомлення (Якщо бажаєте працювати з даною людиною натисніть ' \
               f'"Відповісти", якщо ні, то проігноруйте. Домовтесь про ціну, після чого ' \
               f'робітник натисне клавішу "Підтвердити ціну" і' \
               f' ви зможете оплатити роботу):\n\n{message.text} \n\nВід: @{message.from_user.username}'
        await client_bot.send_message(
            chat_id,
            mess,
            reply_markup=markup
        )


@dp.message_handler(state=states.ChatMode.price)
async def price_state(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text
    async with state.proxy() as data:
        chat_id = data.get('ChatId')
        price = data.get('price')
        event_id = data.get('event')
    markup = InlineKeyboardMarkup()
    user = message.from_user.username
    yes_button = InlineKeyboardButton('Так', callback_data=f'yes_price{user}_e{price}_i{event_id}')
    #no_button = InlineKeyboardButton('Ні', callback_data=f'no_user_id{message.from_user.id}')
    markup.add(yes_button)
    await states.ChatMode.ChatId.set()
    return await client_bot.send_message(
        chat_id,
        f'Для підтвердження ціни натисність <b>Так</b>:'
        f'\n\n{price} \n\nВід: @{message.from_user.username}',
        reply_markup=markup,
        parse_mode='html'
    )


async def on_startup(dp):
    await service_bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    # insert code here to run it after start


async def on_shutdown(dp):
    logging.warning('Shutting down..')

    # insert code here to run it before shutdown

    # Remove webhook (not acceptable in some cases)
    await service_bot.delete_webhook()

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Bye!')

print(WEBHOOK_PATH)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )







