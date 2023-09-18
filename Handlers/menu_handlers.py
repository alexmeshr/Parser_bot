from telebot.async_telebot import AsyncTeleBot
from telebot.types import *
from Database.db_requests import add_user, check_admin, get_users,upd_user,get_schedule_for_days, USERGROUP_IDX, SCHEDULE_TIME_IDX, SCHEDULE_EVENT_IDX
from Misc.keyboard import *
import datetime
import bot_init


async def start(message: Message, bot: AsyncTeleBot, *args):
    print(datetime.datetime.now().__str__(), " : start ", message.from_user.id)
    if message.chat.type in ("group", "supergroup"):
        await bot.send_message(message.chat.id, "Поддержка груповых чатов на данный момент находится в разработке",
                               reply_markup=None)
    else:
        add_user(message.chat.id, message.chat.username)
        await bot.send_message(message.chat.id, "Приветствую!\n"
            "Данный бот разрабатывается в целях упрощения жизни студентам МГУ Саров, каждое утро он парсит расписание с"
            " сайта филиала и перерабатывает в удобную и доступную форму.\nЧтобы узнать возможности бота, нажмите "
            "кнопку \"Помощь\" или отправьте команду /help",
            reply_markup=main_menu_markup(check_admin(message.chat.id)))


async def get_help(message: Message, bot: AsyncTeleBot, *args):
    print(datetime.datetime.now().__str__(), " : help ", message.from_user.id)
    await bot.send_message(message.chat.id, "Справка по командам пока в разработке",
                           reply_markup=None)


async def get_schedule(message: Message, bot: AsyncTeleBot, *args):
    print(datetime.datetime.now().__str__(), " : get_schedule ", message.from_user.id)
    user_info = get_users(message.chat.id)[0]
    if user_info[USERGROUP_IDX] is None:
        await bot.send_message(message.chat.id, "Пожалуйста, укажите свою группу в настройках", reply_markup=None)
    else:
        schedule = get_schedule_for_days(datetime.datetime.today().timetuple().tm_yday, user_info[USERGROUP_IDX])[0]
        reply=""
        for row in schedule:
            reply += row[SCHEDULE_TIME_IDX]+":\n"+row[SCHEDULE_EVENT_IDX]
        await bot.send_message(message.chat.id, "Ваше расписание:\n"+reply, reply_markup=None)


async def return_to_main_menu(message: Message, bot: AsyncTeleBot, *args):
    print(datetime.datetime.now().__str__(), " : return_to_main_menu ", message.from_user.id)
    await bot.send_message(message.chat.id, "Вы в главном меню", reply_markup=main_menu_markup(check_admin(message.chat.id)))


async def get_settings(message: Message, bot: AsyncTeleBot, *args):
    print(datetime.datetime.now().__str__(), " : get_settings ", message.from_user.id)
    await bot.send_message(message.chat.id, "Выберите необходимый пункт", reply_markup=settings_markup())


async def get_subs(message: Message, bot: AsyncTeleBot, *args):
    print(datetime.datetime.now().__str__(), " : get_subs ", message.from_user.id)
    await bot.send_message(message.chat.id, "Управление подписками пока в разработке",
                           reply_markup=None)


async def chose_group(message: Message, bot: AsyncTeleBot, *args):
    print(datetime.datetime.now().__str__(), " : chose_group ", message.from_user.id)
    if message.chat.type in ("group", "supergroup"):
        await bot.send_message(message.chat.id, "Поддержка груповых чатов на данный момент находится в разработке",
                               reply_markup=None)
    else:
        await bot.send_message(message.chat.id, "Выберите свою группу",
                           reply_markup=inline_group_markup())


async def set_group(call: CallbackQuery, bot: AsyncTeleBot, *args):
    print(datetime.datetime.now().__str__(), " : set_group ",call.data, call.from_user.id)
    g_idx = int(call.data.split("_")[1])
    if g_idx==-1:
        await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=None)
        await bot.edit_message_text("Группа не была изменена",call.from_user.id,call.message.message_id)
    else:
        await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=None)
        group = bot_init.groups[g_idx]
        upd_user(call.from_user.id, user_group=group)
        await bot.edit_message_text(group+" установлена Вашей группой", call.from_user.id, call.message.message_id)


async def send_request(message: Message, bot: AsyncTeleBot, *args):
    print(datetime.datetime.now().__str__(), " : send_request ", message.from_user.id)
    if message.text == "Предложить мероприятие":
        await bot.send_message(message.chat.id, "Функция \"Предложить мероприятие\" пока в разработке", reply_markup=None)
    elif message.text == "Сообщить об ошибке в расписании":
        await bot.send_message(message.chat.id, "Функция \"Сообщить об ошибке в расписании\" пока в разработке", reply_markup=None)