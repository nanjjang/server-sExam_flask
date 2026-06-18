import os
from dotenv import load_dotenv
load_dotenv()

secret_key = os.getenv("SECRET_KEY")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(BASE_DIR, 'database/images')
USERS_PATH = os.path.join(BASE_DIR, 'database/users')

os.makedirs(USERS_PATH, exist_ok=True)
os.makedirs(IMAGE_PATH, exist_ok=True)
