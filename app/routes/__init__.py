from flask import Flask
from .auth import auth_bp
from .upload import upload_bp
from .root import root_bp

def register_routes(app: Flask):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(upload_bp, url_prefix='/upload')
    app.register_blueprint(root_bp, url_prefix='/')