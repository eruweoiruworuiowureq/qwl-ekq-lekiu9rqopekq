from array import array
from typing import Dict
import couchdb2

server = couchdb2.Server(username="admin", password="admin")

if not "pages" in server:
    server.create("pages")

if not "apps" in server:
    server.create("apps")

if not "bots" in server:
    server.create("bots")

bots = server.get("bots")
pages = server.get("pages")
apps = server.get("apps")

def get_app(app_id):
    app = apps.get(app_id)
    return app

def save_page(page, id, app_id):
    page["app_id"] = app_id
    p = pages.get(id or "")
    if id and p:
        page["_id"] = p["_id"]
        page["_rev"] = p["_rev"]
        pages.put(page)
        return id
    pages.put(page)
    return page["_id"]

def add_page_to_app(page_id, page_name, app_id):
    app = apps.get(app_id)
    if not app:
        return
    app["pages"][page_name] = page_id
    apps.put(app)

def get_pages(app_id):
    app = apps.get(app_id)
    return app and app["pages"] or None

def get_page(page_id = None, app_id = None, page_name = None):
    if page_id:
        return pages.get(page_id)
    app_pages = get_pages(app_id)
    return app_pages and app_pages[page_name] and get_page(app_pages[page_name]) or None

def get_apps(chat_id):
    return apps.find({"chat_id": str(chat_id)})

def create_app(chat_id, app_name):
    doc = {
        "title": app_name,
        "pages": {},
        "chat_id": str(chat_id)
    }
    apps.put(doc)
    return doc["_id"]

def get_bots(chat_id):
    return bots.find({"chat_id": str(chat_id)})

def get_all_bots():
    return bots.find({})["docs"]

def get_bot(bot_id):
    return bots.get(bot_id)

def add_bot(chat_id, bot_key, bot_name):
    if len(bots.find({"chat_id": str(chat_id), "bot_key": bot_key})["docs"]) != 0:
        return
    doc = {
        "chat_id": str(chat_id),
        "bot_key": bot_key,
        "bot_name": bot_name,
        "app_id": ""
    }
    bots.put(doc)

def set_app_to_bot(bot_id, app_id):
    bot = bots.get(bot_id)
    bot["app_id"] = app_id
    bots.put(bot)