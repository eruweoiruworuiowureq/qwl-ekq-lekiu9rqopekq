from concurrent.futures import thread
import re
import threading
from time import sleep
import telebot

class Userstate:
    def __init__(self):
        self._userstates = {}
    def get(self, _chat_id, val):
        chat_id = str(_chat_id)
        return chat_id in self._userstates and val in self._userstates[chat_id] and self._userstates[chat_id][val] or "0"
    def set(self, _chat_id, val, value):
        chat_id = str(_chat_id) 
        if not chat_id in self._userstates:
            self._userstates[chat_id] = {}
        self._userstates[chat_id][val] = value

userstates = Userstate()

def on_inline_command(cmd, bot):
    regex = re.escape(cmd) + r"_(.*)"
    def decorator(handler):
        @bot.callback_query_handler(lambda call: re.match(regex, call.data) is not None)
        def command_handler(call: telebot.types.CallbackQuery):
            cmd_arg = re.match(regex, call.data).groups()[0]
            handler(cmd_arg, call)
    return decorator

def create_keyboard(page_id, chat_id):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("Редактировать текст", callback_data="edittext_" + page_id))
    keyboard.add(telebot.types.InlineKeyboardButton("Редактировать кнопки", callback_data="editbtns_" + page_id))
    keyboard.add(telebot.types.InlineKeyboardButton("Назад", callback_data="openapp_" + userstates.get(chat_id,"openned_app")))
    return keyboard

def parse_keyboard(kbrd):
    regex = r"\[(.*)\]\((.*)\)"
    matches = re.findall(regex, kbrd)
    d = {}
    for m in matches:
        d[m[0]] = m[1]
    return d

def isState(id, startswith):
    return userstates.get(id, "title") and userstates.get(id, "title").startswith(startswith)

def show_page(chat_id, page, bot):
    bot.send_message(chat_id=chat_id, text=page.get_info(), reply_markup=create_keyboard(page.id, chat_id), parse_mode="html")

def update_showed_page(chat_id, message_id, page, bot):
    try:
        bot.edit_message_text(text=page.get_info(), chat_id=chat_id, message_id=message_id, reply_markup=create_keyboard(page.id, chat_id), parse_mode='html')
    finally:
        return

def do_question(bot, chat_id, question, call = None):
    kbrd = telebot.types.InlineKeyboardMarkup()
    kbrd.add(telebot.types.InlineKeyboardButton("Отмена", callback_data="question_stop"))
    msg = bot.send_message(chat_id=chat_id, text=question, parse_mode="html", reply_markup=kbrd)

    @bot.message_handler(content_types=['text'], func=lambda msg: isState(msg.chat.id, "question") )
    def on_question_answer(msg: telebot.types.Message):
        id = msg.chat.id
        userstates.set(msg.chat.id,"title","sleep")
        bot.delete_message(id, userstates.get(msg.chat.id,"message").id)
        bot.delete_message(id, msg.message_id)
        userstates.get(msg.chat.id,"onAnswer")(msg)

    @on_inline_command("question", bot)
    def stop_question(msg, call):
        if msg == "stop":
            bot.delete_message(call.message.chat.id, call.message.message_id)

    if call:
        bot.answer_callback_query(call.id)
    def decorator(handler):
        userstates.set(chat_id,"title", "question")
        userstates.set(chat_id,"onAnswer", handler)
        userstates.set(chat_id,"message", msg)
    return decorator

def sleep_then_do(time):
    def sleep_func(func):
        sleep(time)
        func()
    def decorator(handle):
        t = threading.Thread(target=lambda: sleep_func(handle))
        t.start()
    return decorator
