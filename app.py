from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_cors import CORS
from sqlalchemy import create_engine, desc, Column, String, Integer, Boolean, Date, func
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

from datetime import date

import os

from config import Config
from forms import ContactForm, ProjectForm

def create_app(config_class=Config):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

app.config['SECRET_KEY'] = config.SECRET_KEY

DATABASE = os.environ.get("DB_URI", f"postgresql://{config.USERNAME}:{config.PASSWORD}@localhost:5432/{config.DATABASE}")

SQLALCHEMY_DATABASE_URI = DATABASE 

engine = create_engine(SQLALCHEMY_DATABASE_URI)
db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
metadata = Base.metadata
metadata.bind=engine





if __name__ == '__main__':
    app.run(debug=True)
