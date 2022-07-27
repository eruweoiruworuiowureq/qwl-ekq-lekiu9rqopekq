from pages import *

places = {
    "8":"Центральный",
    "7":"Калининский",
    "6":"Дзержинский",
    "5":"Октябрьский",
    "4":"Ленинский",
    "3":"Кировский",
    "2":"Первомайский",
    "1":"Советский"}

drugs = {
    "12":"🌟НЕОМЕФ🌟",
    "14":"🌟DMT🌟",
    "1":"Скорость A-PVP (синие крисы)",
    "2":"Мефедрон Кристаллы VHQ",
    "3":"Амфетамин HQ",
    "4":"Гаш Евро",
    "5":"Гаш Ice-O-Lator",
    "6": "Бошки АК-47",
    "7": "Бошки Amnezia Haze",
    "8": "Гера HQ белый",
    "9": "Метадон",
    "10": "Экстази RED-BULL",
    "11": "ЛСД-25"
}

costs = {
    "1":{"0,5г":"1600", "1г" : "2900", "2г":"5000"},
    "2":{"0,5г":"1300", "1г" : "2300", "2г":"4000"},
    "3":{"0,5г":"1200", "1г" : "2000", "2г":"3500"},
    "4":{"0,5г":"1200", "1г" : "2000", "2г":"3500"},
    "5":{"0,5г":"1400", "1г" : "2200", "3г":"4000"},
    "6":{"0,5г":"1400", "1г" : "2200", "3г":"4000"},
    "7":{"1г" : "2200", "2г":"3800"},
    "8":{"0,5г":"3300", "1г" : "5800", "2г":"9900"},
    "9":{"0,5г":"3400", "1г" : "5600"},
    "10":{"2шт":"2900", "5шт" : "6000"},
    "11":{"2шт":"2900"},
    "12":{"0,5г":"2000", "1г" : "3800", "2г":"7000"},
    "14":{"1г":"7000"},
}

app = PageApp()

app.set_page("start", Page('''Приветствуем✌️
Наш магазин работает только в <b>Новосибирске</b>
Вы попали на окно навигации нашего магазина.

<b>В нашем магазине все клады</b>🎁
-Магнит🧲
    или
-Тайник🙈

Никаких шныряний и копаний по лесу. Все клады производятся по особой схеме, из-за чего легко поднимаемы, но крайне надежны 

В нашем боте возможен заказ не всего перечня товаров нашего магазина, если интересующего Вас товара, или развесовки не оказалось в нашем боте, просьба обратиться к оператору (@techsupport_24,) для оформления ручного заказа.

Наш магазин в TOR:
neomefsiq65f3cjyzaogds2w4xknsjyubneleh23qtxa34xmell2sjqd.onion/''',
{"Оформить заказ" : "do_order_0"}))

p = {
    v: "place_" + k for k, v in places.items()
}
p["🔙Назад"] = "start_0"
app.set_page("do_order", Page("🌆<b>Выберите район</b>🌆", p))

p = {
    v: "drug_" + k for k, v in drugs.items()
}
p["🔙Назад"] = "do_order_0"
app.set_page("do_drug", Page("🌐<b>Выберите товар</b>🌐", p))

app.set_page("pay", Page('''💳<b>Выберите способ оплаты</b>💵

         <b>❗️ВАЖНО❗️ </b>

 СОВЕТУЕМ ВЫБИРАТЬ СПОСОБ ОПЛАТЫ QIWI
 Qiwi можно пополнить любым способом:
 - С карты любого банка,
 - Через терминал,
 - Со своего личного Qiwi кошелька''', {"Карта": "card_0", "QIWI" : "qiwi_0", "Отмена" : "start_0"}))

app.set_page("card", Page('''На данный момент оплата через Карту невозможна.''',
{ "Отмена" : "pay_0"}))

app.set_page("qiwi", Page('''Отлично.
Ваш уникальный ID: {randint}
Ваш город: Новосибирск
Товар: {drugname}
Сумма к оплате: {cost}

------------------------------------------
Перевод на QIWI по номеру телефона:

{qiwinum}

После оплаты, подтвердите нажатием на кнопку "Подтверждаю"
Укажите номер транзакции из чека или электронной квитанции, после чего бот проверит транзакцию и автоматически выдаст фото + координаты.''',
{"Подтверждаю": "payed_0", "Отмена" : "start_0"}))