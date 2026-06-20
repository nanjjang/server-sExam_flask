import os
from dotenv import load_dotenv
load_dotenv()

secret_key = os.getenv("SECRET_KEY")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(BASE_DIR, 'database/images')
THUMB_PATH = os.path.join(BASE_DIR, 'database/thumbs')
USERS_PATH = os.path.join(BASE_DIR, 'database/users')
IMAGE_META_PATH = os.path.join(BASE_DIR, 'database/image_meta.json')

os.makedirs(USERS_PATH, exist_ok=True)
os.makedirs(IMAGE_PATH, exist_ok=True)
os.makedirs(THUMB_PATH, exist_ok=True)
