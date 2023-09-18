import asyncio
import datetime
import asyncio
from telebot import async_telebot
from telebot.asyncio_storage import StateMemoryStorage
from bot_init import BOT_TOKEN
from Handlers.admin_handlers import db_updator, schedule_updator
from telebot.asyncio_filters import *
from Database.db_requests import create_db
from Handlers.menu_handlers import *

bot = async_telebot.AsyncTeleBot(BOT_TOKEN, state_storage=StateMemoryStorage())
lock = asyncio.Lock()


async def main():
    await asyncio.gather(
                        bot.infinity_polling(skip_pending=True),
                        db_updator(),
                        schedule_updator()
    )


if __name__ == "__main__":
    bot.register_callback_query_handler(set_group, func=lambda call: call.data.split("_")[0] == "group", pass_bot=True)
    bot.register_message_handler(start, commands=['start'], content_types=['text'], pass_bot=True)
    bot.register_message_handler(return_to_main_menu, func=lambda m: m.text == "Главное меню", content_types=['text'], pass_bot=True)
    bot.register_message_handler(get_help, commands=['help'], content_types=['text'], pass_bot=True)
    bot.register_message_handler(get_help, func=lambda m: m.text == "Помощь", content_types=['text'], pass_bot=True)
    bot.register_message_handler(get_schedule, func=lambda m: m.text == "Узнать расписание", content_types=['text'], pass_bot=True)
    bot.register_message_handler(get_settings, func=lambda m: m.text == "Настройки", content_types=['text'], pass_bot=True)
    bot.register_message_handler(get_subs, func=lambda m: m.text == "Управление подписками", content_types=['text'], pass_bot=True)
    bot.register_message_handler(chose_group, func=lambda m: m.text == "Выбрать группу", content_types=['text'], pass_bot=True)
    bot.register_message_handler(send_request, func=lambda m: m.text == "Предложить мероприятие", content_types=['text'], pass_bot=True)
    bot.register_message_handler(send_request, func=lambda m: m.text == "Сообщить об ошибке в расписании", content_types=['text'], pass_bot=True)

    try:
        create_db()
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(restore_users())
        # asyncio.run(bot.infinity_polling(skip_pending=True))
        asyncio.run(main())

    except KeyboardInterrupt:
        raise KeyboardInterrupt
