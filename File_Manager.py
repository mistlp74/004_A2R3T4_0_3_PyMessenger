import os
import json
from config import CHATS_DIR, CONTACTS_FILE

def user_file_exists():
    if not os.path.isfile("User_Info.json"):
        return False
    try:
        with open("User_Info.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            name = data.get("name", "").strip()
            number = data.get("number", "").strip()
            if name and number:
                return True
    except Exception:
        pass
    return False

def save_user_info(name, number, USER_FILE):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump({"name": name, "number": number}, f, ensure_ascii=False, indent=4)

def load_user_info():
    with open("User_Info.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_contacts():
    if os.path.exists(CONTACTS_FILE):
        with open(CONTACTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_contacts(contacts):
    with open(CONTACTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(contacts, f, ensure_ascii=False, indent=2)