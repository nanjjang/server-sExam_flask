import os

secret_key = "sunrin-secret-key-2026"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(BASE_DIR, 'database/images')
THUMB_PATH = os.path.join(BASE_DIR, 'database/thumbs')
USERS_PATH = os.path.join(BASE_DIR, 'database/users')
IMAGE_META_PATH = os.path.join(BASE_DIR, 'database/image_meta.json')

os.makedirs(USERS_PATH, exist_ok=True)
os.makedirs(IMAGE_PATH, exist_ok=True)
os.makedirs(THUMB_PATH, exist_ok=True)
