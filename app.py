from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config import Config

app = Flask(__name__)

config = Config()

SQLALCHEMY_DATABASE_URI = f"postgresql://{config.USERNAME}:{config.PASSWORD}@localhost:5432/{config.DATABASE}"

engine = create_engine(SQLALCHEMY_DATABASE_URI)
db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()

@app.route('/')
def index():
    x = db_session.execute("SELECT * FROM contact;").fetchall()
    return str(x) 

if __name__ == '__main__':
    app.run(debug=True)
