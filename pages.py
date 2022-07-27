from struct import unpack
from telebot import types

class Page():
    def __init__(self, message = None, keyboard = {}, id = None):
        self.message = message
        self._keyboard = keyboard
        self.keyboard = generate_keyboard(keyboard)
        self.id = id
        if id is None:
            self.save()
    def get_message(self, **kwargs):
            return self.message
    
    def set_keyboard(self, kbrd):
        self._keyboard = kbrd
        self.keyboard = generate_keyboard(kbrd)
    def save(self):
        d = self.toDict()
        # self.id = server.save_page(d, self.id, "test")
    def toDict(self):
        return {
            "message" : self.message,
            "keyboard" : self._keyboard
        }
    def get_keyboard(self):
        out = ''
        for k, v in self._keyboard.items():
            out += '[<b>' + k + "</b>] (" + v + ')\n'
        return out 
    def get_info(self):
        return self.get_message() + '\n\n' + self.get_keyboard()
    def fromDict(dict):
        return Page(dict["message"], dict["keyboard"], dict["_id"])

class PageApp():
    def __init__(self):
        self.pages = {}
    def set_page(self, name, p):
        self.pages[name] = p
    def get_page(self, name) -> Page:
        return self.pages[name]
    def toDict(self):
        dict = {}
        for k, v in self.pages.items():
            dict[k] = v.toDict()
        return dict

def get_page(name, pages, message : types.Message):
    p : Page = pages.get_page(name)
    return {"chat_id" : message.chat.id, "text" : p.get_message(), "reply_markup" : p.keyboard}

def generate_keyboard(dict):
    keyboard = types.InlineKeyboardMarkup()
    for k, v in dict.items():
        keyboard.add(types.InlineKeyboardButton(text=k, callback_data=v), row_width=2)
    return keyboard