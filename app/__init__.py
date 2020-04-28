from flask import Flask 
from flask_cors import CORS
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

from config import Config

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object('config.Config')


    with app.app_context():
        from app.main.routes import main
        from app.api.routes import api
        app.register_blueprint(main)
        app.register_blueprint(api)
    
    return app

