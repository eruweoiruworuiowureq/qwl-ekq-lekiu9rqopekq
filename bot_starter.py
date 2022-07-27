import threading
import telebot
import pages

bot_threads = {}

standart_app = pages.PageApp()
standart_app.set_page("hello", pages.Page("Бот работает.", {}, "1") )

def start_msg_fab(bot, v):
    def start_msg(message):
        bot.send_message(**pages.get_page("hello", v, message))
    return start_msg

def callback_inline_fab(bot, v):
    def callback_inline(call):
        if call.message:
            try:
                bot.edit_message_text(**pages.get_page(call.data, v, call.message), message_id = call.message.message_id)
            finally:
                return
    return callback_inline

def start(bots):
    for k, v in bots.items():
        bot = telebot.TeleBot(k)

        bot.message_handler(commands=['start'])(start_msg_fab(bot, v))
        bot.callback_query_handler(func=lambda call: True)(callback_inline_fab(bot, v))

        thread = threading.Thread(target=bot.infinity_polling)
        thread.start()

        bot_threads[k] = {"thread": thread, "stop_bot" : bot.stop_polling()}

def add_bot(k, app = None):
    if k in bot_threads:
        bot_threads[k]["stop_bot"]()
    try:
        bot = telebot.TeleBot(k)
        bot.message_handler(commands=['start'])(start_msg_fab(bot, app or standart_app))
        bot.callback_query_handler(func=lambda call: True)(callback_inline_fab(bot, app or standart_app))
        thread = threading.Thread(target=bot.infinity_polling)
        thread.start()
        bot_threads[k] = {"thread": thread, "stop_bot" : bot.stop_polling}
    finally:
        return