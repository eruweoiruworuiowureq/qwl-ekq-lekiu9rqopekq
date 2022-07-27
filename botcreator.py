import server
import pages
import bot_starter
import telebot
from helpers import *

bots = server.get_all_bots()
for b in bots:
    try:
        a = server.get_app(b["app_id"])
        app = pages.PageAppOf(a)
        bot_starter.add_bot(b["bot_key"], app)
    finally:
        continue

@bot.message_handler(commands=['start'])
def start_msg(message : telebot.types.Message):
    start_page(message.chat.id)

def start_page(chat_id, call = None):
    kbrd = {"Приложения": "openapps_" + str(chat_id), "Боты" : "openbots_" + str(chat_id)}
    if call:
        bot.edit_message_text("Главное меню.", chat_id, call.message.message_id, reply_markup=pages.generate_keyboard(kbrd))
    else:
        bot.send_message(chat_id, "Главное меню.", reply_markup=pages.generate_keyboard(kbrd))
on_inline_command("startpage")(lambda chat_id, call: start_page(chat_id, call))

def open_bots(chat_id, message_id = None):
    bots = server.get_bots(chat_id)
    kbrd = {}
    for b in bots["docs"]:
        kbrd[b["bot_name"]] = "openbot_" + b["_id"]
    send_kbrd = pages.generate_keyboard(kbrd)
    send_kbrd.add(telebot.types.InlineKeyboardButton("Добавить бота", callback_data="createbot_" + str(chat_id)))
    send_kbrd.add(telebot.types.InlineKeyboardButton("Назад", callback_data="startpage_" + str(chat_id)))
    try:
        if message_id:
            bot.edit_message_text("Ваши боты:", chat_id, message_id, reply_markup=send_kbrd)
        else:
            bot.send_message(chat_id, "Ваши боты:", reply_markup=send_kbrd)
    finally:
        return

def open_app(app_id, chat_id):
    app = server.get_app(app_id)
    msg = "Вы открыли приложение " + app["title"] + "\n\n Страницы: "
    pages = app["pages"]
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    for k, v in pages.items():
        keyboard.add(telebot.types.InlineKeyboardButton(k, callback_data="openpage_"+v))
    keyboard.add(telebot.types.InlineKeyboardButton("Создать страницу", callback_data="createpage_"+app_id))
    keyboard.add(telebot.types.InlineKeyboardButton("Назад", callback_data="openapps_"+str(chat_id)))
    bot.send_message(chat_id, msg, reply_markup=keyboard)
    userstates.set(chat_id,"openned_app", app_id)

def open_apps(chat_id, message_id = None):
    user_apps = server.get_apps(chat_id)["docs"]
    apps = {}
    for app in user_apps:
        apps[app["title"]] = "openapp_" + app["_id"]
    kbrd = pages.generate_keyboard(apps)
    kbrd.add(telebot.types.InlineKeyboardButton(text="Создать новое приложение", callback_data="createapp_" + str(chat_id)))
    kbrd.add(telebot.types.InlineKeyboardButton("Назад", callback_data="startpage_" + str(chat_id)))
    if message_id:
        bot.edit_message_reply_markup(chat_id, message_id, reply_markup=kbrd)
    else:
        bot.send_message(chat_id, "Ваши приложения: ", reply_markup = kbrd)

@on_inline_command("openpage")
def open_page(page_id, call):
    page = pages.Page.fromDict(server.get_page(page_id))
    show_page(call.message.chat.id, page)
    bot.delete_message(call.message.chat.id, call.message.message_id)

@on_inline_command("edittext")
def edit_msg(page_id, call):
    page = pages.Page.fromDict(server.get_page(page_id))
    @do_question(call.message.chat.id, "Введите новый текст страницы", call)
    def on_edit_question(msg: telebot.types.Message):
        page.message = msg.html_text
        page.save()
        update_showed_page(msg.chat.id, call.message.id, page)

@on_inline_command("openapp")
def open_app_msg(app_id, call):
    open_app(app_id, call.message.chat.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)

@on_inline_command("editbtns")
def edit_btns_cmd(page_id, call):
    page = pages.Page.fromDict(server.get_page(page_id))
    q_msg = "Введите новые кнопки в виде:\n[Название кнопки](Название страницы)\n\nСуществующие страницы:\n" + "\n".join("<b>" + page + "</b>" for page in server.get_pages(userstates.get(call.message.chat.id, "openned_app")).keys())
    @do_question(call.message.chat.id, q_msg, call)
    def on_edit_question(msg: telebot.types.Message):
        kbrd = parse_keyboard(msg.text)
        page.set_keyboard(kbrd)
        page.save()
        update_showed_page(msg.chat.id, call.message.id, page)

@on_inline_command("createpage")
def edit_btns(app_id, call):
    q_msg = "Введите название страницы"
    @do_question(call.message.chat.id, q_msg, call)
    def on_edit_question(msg: telebot.types.Message):
        title = msg.text
        new_page = pages.Page("Пусто.")
        new_page.save()
        server.add_page_to_app(new_page.id, title, app_id)
        open_app(app_id, call.message.chat.id)
        bot.delete_message(call.message.chat.id, call.message.message_id)

@on_inline_command("createapp")
def create_app(chat_id, call):
    @do_question(chat_id, "Введите название приложения", call)
    def create_app_answer_handler(msg: telebot.types.Message):
        title = msg.text
        app_id = server.create_app(chat_id, title)
        start_page = pages.Page("Это стартовая страница")
        server.add_page_to_app(start_page.id, "hello", app_id)
        open_apps(chat_id, call.message.message_id)

@on_inline_command("openapps")
def openapps_handler(chat_id, call):
    open_apps(chat_id)
    bot.delete_message(call.message.chat.id, call.message.message_id)

on_inline_command("openbots")(lambda msg, call: open_bots(call.message.chat.id, call.message.message_id))

@on_inline_command("createbot")
def add_bot(chat_id, call):
    @do_question(chat_id, "Введите название бота", call)
    def bot_name_handler(bot_name_msg):
        @do_question(chat_id, "Введите апи-кей бота")
        def bot_key_handler(bot_key_msg):
            name = bot_name_msg.text
            key = bot_key_msg.text
            info_msg = bot.send_message(chat_id, "Идет проверка ключа...")
            good = True
            test_bot = None
            try:
                test_bot = telebot.TeleBot(key)
            except Exception as e:
                good = False
                print(e)
            res_msg = bot.send_message(chat_id, "Бот добавлен" if good else "Ключ неверный")
            sleep_then_do(2)(lambda: bot.delete_message(chat_id, res_msg.message_id))
            bot.delete_message(chat_id, info_msg.message_id)
            if not good:
                return
            test_bot.stop_polling()
            server.add_bot(chat_id, key, name)
            bot_starter.add_bot(key)
            open_bots(chat_id, call.message.message_id)

def open_bot(bot_id, call):
    chat_id = call.message.chat.id
    openned_bot = server.get_bot(bot_id)
    userstates.set(chat_id, "openned_bot", bot_id)
    user_apps = server.get_apps(chat_id)["docs"]
    apps = {}
    for app in user_apps:
        apps[app["title"] + (" (Выбрано)" if app["_id"] == openned_bot["app_id"] else "")] = "setapp_" + app["_id"]
    kbrd = pages.generate_keyboard(apps)
    kbrd.add(telebot.types.InlineKeyboardButton("Назад", callback_data="openbots_" + str(chat_id)))
    bot.edit_message_text("Бот <b>" + openned_bot["bot_name"] + "</b>\n\nКакое приложение установить?", chat_id, call.message.message_id, parse_mode="html", reply_markup=kbrd)

on_inline_command("openbot")(open_bot)

@on_inline_command("setapp")
def set_app(app_id, call):
    bot_id = userstates.get(call.message.chat.id, "openned_bot")
    server.set_app_to_bot(bot_id, app_id)
    open_bot(bot_id, call)
    bot_starter.add_bot(server.get_bot(bot_id)["bot_key"], pages.PageAppOf(server.get_app(app_id)))

bot.polling()