from flask import Flask
from config import secret_key
from routes import register_routes

app = Flask(__name__)
app.secret_key = secret_key

register_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
