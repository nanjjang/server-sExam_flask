import os
import json
from datetime import datetime
from config import USERS_PATH


def get_user(username):
    filepath = os.path.join(USERS_PATH, f"{username}.json")
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_user(username, password_hash):
    filepath = os.path.join(USERS_PATH, f"{username}.json")
    data = {
        'username': username,
        'password': password_hash,
        'created_at': datetime.now().isoformat()
    }
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
