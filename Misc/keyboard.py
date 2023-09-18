from telebot.types import ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import bot_init

def main_menu_markup(admin:bool = False):
    buttons = [
        ["Узнать расписание"],
        ["Управление подписками"],
        ["Настройки","Помощь"]
    ]
    if admin:
        buttons.append(["Админка"])
    menu_markup = ReplyKeyboardMarkup(is_persistent=True, row_width=2, resize_keyboard=True)
    for b in buttons:
        menu_markup.row(*b)
    return menu_markup


def settings_markup():
    buttons = [
        ["Главное меню"],
        ["Выбрать группу"],
        ["Предложить мероприятие"],
        ["Сообщить об ошибке в расписании"]
    ]
    markup = ReplyKeyboardMarkup(is_persistent=True, row_width=1, resize_keyboard=True)
    for b in buttons:
        markup.row(*b)
    return markup


def inline_group_markup():
    keyboard = []
    groups = bot_init.groups
    for i in range(len(groups)):
        keyboard.append([InlineKeyboardButton(groups[i], callback_data="group_"+str(i))])
    keyboard.append([InlineKeyboardButton("Назад", callback_data="group_-1")])
    markup = InlineKeyboardMarkup(keyboard, 5)
    return markup