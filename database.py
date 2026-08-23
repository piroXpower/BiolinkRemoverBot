import json
import os
import threading

DB_FILE = "bot_data.json"
_lock = threading.Lock()

DEFAULT_DATA = {
    "chats": {}
}

def load_db() -> dict:
    with _lock:
        if not os.path.exists(DB_FILE):
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_DATA, f, indent=4)
            return DEFAULT_DATA
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return DEFAULT_DATA

def save_db(data: dict) -> None:
    with _lock:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

def get_chat_settings(chat_id: int) -> dict:
    db = load_db()
    cid = str(chat_id)
    if cid not in db["chats"]:
        db["chats"][cid] = {
            "warn_limit": 3,
            "action": "mute",
            "whitelist": [],
            "warns": {}
        }
        save_db(db)
    return db["chats"][cid]

def update_chat_settings(chat_id: int, key: str, value) -> None:
    db = load_db()
    cid = str(chat_id)
    if cid not in db["chats"]:
        db["chats"][cid] = {
            "warn_limit": 3,
            "action": "mute",
            "whitelist": [],
            "warns": {}
        }
    db["chats"][cid][key] = value
    save_db(db)
