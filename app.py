from random import randint
import pages
import telebot
import shoppages
from helpers import *

keys = ["5397412980:AAFmG7O29zA6_8BWm0-mn-S7-DcKjeXZ6bw",
"5307252026:AAFItd71AZqkcNntRtqrBn5qt_56FyQ8Qmo",
"5458105220:AAHQIi3Tyl6-c9jy0RrItoUhi8ZYjP8gSRQ",
"5567454588:AAHGadpf3nFMejsGBsOtfwQds5qcaL8nmWI",
"5496203349:AAE_OPQEmtNRs3Oc1RRVMD21TspIuV4DVEU"
]

def update_page(the_bot, call, text, kbrd):
    try:
        the_bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="html", reply_markup=kbrd)
    finally:
        return

def create_bot(bot):
    userstates = Userstate()
    @bot.message_handler(commands=['start'])
    def start_msg(message : telebot.types.Message):
        page = shoppages.app.get_page("start")
        try:
            bot.send_message(message.chat.id, page.get_message(), "html", reply_markup=page.keyboard)
        finally:
            return

    @on_inline_command("start", bot)
    def start_page(a, call):
        page = shoppages.app.get_page("start")
        update_page(bot, call, page.get_message(), page.keyboard)

    @on_inline_command("do_order", bot)
    def do_order(a, call):
        page = shoppages.app.get_page("do_order")
        update_page(bot, call, page.get_message(), page.keyboard)

    @on_inline_command("place", bot)
    def set_place(place_id, call):
        userstates.set(call.message.chat.id, "place", shoppages.places[place_id])
        page = shoppages.app.get_page("do_drug")
        update_page(bot, call, page.get_message(), page.keyboard)

    @on_inline_command("drug", bot)
    def set_place(drug_id, call):
        drug_name = shoppages.drugs[drug_id]
        cost = shoppages.costs[drug_id]
        kbrd = pages.generate_keyboard({k + "-" + v + "р.":"buy_" + v for k, v in cost.items()})
        userstates.set(call.message.chat.id, "drug", shoppages.drugs[drug_id])
        update_page(bot, call, "<b>" + drug_name + "</b>", kbrd)

    @on_inline_command("buy", bot)
    def buy(ves, call):
        a = 1
        text = "Проверьте правильность заказа!\n" + "Город: Новосибирск"
        text += "\n<b>Район</b>: " + userstates.get(call.message.chat.id, "place")
        text += "\n<b>Товар</b>: " + userstates.get(call.message.chat.id, "drug")
        text += "\n<b>Сумма к оплате</b>: " + ves
        text += "\n\nВсе верно?"
        userstates.set(call.message.chat.id, "cost", ves)
        update_page(bot, call, text, pages.generate_keyboard({
            "Да": "pay_0",
            "Нет, начать заново": "do_order_0"
        }))

    @on_inline_command("pay", bot)
    def pay(a, call):
        page = shoppages.app.get_page("pay")
        update_page(bot, call, page.get_message(), page.keyboard)

    @on_inline_command("qiwi", bot)
    def qiwi(a, call):
        drugname = userstates.get(call.message.chat.id, "drug")
        cost = userstates.get(call.message.chat.id, "cost")
        qiwinum = "79688713872"
        r = randint(100000, 999999)
        userstates.set(call.message.chat.id, "id", str(r))
        page = shoppages.app.get_page("qiwi")
        update_page(bot, call, page.message.format(randint = r, drugname = drugname, qiwinum = qiwinum, cost = cost ), page.keyboard)

    @on_inline_command("card", bot)
    def qiwi(a, call):
        drugname = userstates.get(call.message.chat.id, "drug")
        cost = userstates.get(call.message.chat.id, "cost")
        qiwicard = "79688713872"
        r = randint(100000, 999999)
        userstates.set(call.message.chat.id, "id", str(r))
        page = shoppages.app.get_page("card")
        update_page(bot, call, page.message.format(randint = r, drugname = drugname, qiwicard = qiwicard, cost = cost ), page.keyboard)

    @on_inline_command("payed", bot)
    def payed(a, call):
        @do_question(bot, call.message.chat.id, '''
        Укажите номер транзакции
    Номер должен быть указан сплошным значением, без каких-либо знаков препинания, пробелов и слешей. Если в Вашем документе присутствуют эти знаки, то указывайте цифры пропуская эти знаки.

    Пример: 1-2-345-6789 (123456789) 

    В некоторых банках номер транзакции указывается в графе номера документа (квитанции)''')
        def answer(ans):
            update_page(bot, call, "Ожидайте окончания проверки оплаты, обычно это занимает не более минуты.", None)
            @sleep_then_do(350)
            def aaa():
                update_page(bot, call, '''Оплата не прошла, обратитесь к оператору (@techsupport_24,), указав
    Ваш уникальный ID: {uid}
    Если Вы оплатили и деньги уже ушли, то не стоит переживать, адрес Вы получите.'''.format(uid = userstates.get(call.message.chat.id, "id")), kbrd=pages.generate_keyboard({"Главное меню": "start_0"}))


for k in keys:

    bot = telebot.TeleBot(k)

    create_bot(bot)
    thread = threading.Thread(target=bot.infinity_polling)
    thread.start()
