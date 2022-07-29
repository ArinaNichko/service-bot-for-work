from aiogram.dispatcher.filters.state import StatesGroup, State


class ChatMode(StatesGroup):
   ChatId = State()
   price = State()
   user = State()
   event = State()


