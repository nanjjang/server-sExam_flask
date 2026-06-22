from flask import Flask
from config import secret_key
from routes import register_routes

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = secret_key

register_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
