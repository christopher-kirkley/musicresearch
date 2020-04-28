from sqlalchemy import create_engine, desc, Column, String, Integer, Boolean, Date, func
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

from datetime import date

import os

from database import Base

# Models - declarative auto-load
class Contact(Base):
    __tablename__ = 'contact'
    contact_id = Column(Integer, primary_key=True)
    project_id = Column(Integer)
    name = Column(String(200))
    link = Column(String(300))
    checked = Column(Date, nullable=False, default=func.now())
    in_contact = Column(Boolean, nullable=False, default=False)
    notes = Column(String(500))
    active = Column(Boolean, nullable=False, default=True)

class Project(Base):
    __tablename__ = 'project'
    project_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    evernote = Column(String(150))
    description = Column(String(600))
    active = Column(Boolean, nullable=False, default=True)

class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True)


class ContactSchema(SQLAlchemySchema):
    class Meta:
        model = Contact
        load_instance = True

    contact_id = auto_field()
    project_id = auto_field()
    name = auto_field()
    link = auto_field()
    checked = auto_field()
    in_contact = auto_field()
    notes = auto_field()
    active = auto_field()

class ProjectSchema(SQLAlchemySchema):
    class Meta:
        model = Project
        load_instance = True

    project_id = auto_field()
    name = auto_field()
    evernote = auto_field()
    description = auto_field()
    active = auto_field()
    
contact_schema = ContactSchema()
contacts_schema = ContactSchema(many=True)

project_schema = ProjectSchema()
projects_schema = ProjectSchema(many=True)

