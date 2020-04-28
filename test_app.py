import os
import tempfile
import pytest

from flask import Flask
from flask_cors import CORS

os.environ['DB_URI'] = 'sqlite://'

from app import app, get_all_project
from app import metadata, Project, engine
from config import Config

import json

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

db_session = scoped_session(sessionmaker(bind=engine))


@pytest.fixture
def client():
    app.config['TESTING'] = True
    
    """Create db"""
    metadata.create_all(engine)

    """create testing client"""
    client = app.test_client()

    """establish app context"""
    ctx = app.app_context()
    ctx.push()

    yield client

    ctx.pop()


def test_one(client):
    q = db_session.query(Project).all()
    assert len(q) == 0

    project = Project(
            name='hey',
            evernote='google',
            description='potato')

    db_session.add(project)
    db_session.commit()

    q = db_session.query(Project).all()
    assert len(q) == 1

def test_two(client):
    q = db_session.query(Project).all()
    assert len(q) == 1
    assert 'hey' == q[0].name

def test_can_get_all_projects(client):
    resp = client.get('/api/v1.0/project')
    assert resp.status_code == 200
    json_resp = json.loads(resp.data)
    assert len(json_resp) == 1

def test_can_add_new_project(client):    
    data = {
        'name': 'jojo',
        'evernote': 'taco',
        'description': 'free for all'
            }
    json_data = json.dumps(data)
    resp = client.post('/api/v1.0/project', data=json_data)
    assert resp.status_code == 200
    json_resp = json.loads(resp.data)
    assert json_resp == {'success': 'true'}
    q = db_session.query(Project).filter(Project.name == 'jojo').one()
    assert q.name == 'jojo'
    assert q.evernote == 'taco'
    assert q.description == 'free for all'

def test_now_has_multiple_projects(client):
    q = db_session.query(Project).all()
    assert len(q) == 2

def test_can_delete_project(client):
    q = db_session.query(Project).first()
    id_to_delete = q.project_id
    resp = client.delete(f'/api/v1.0/project/{id_to_delete}')
    assert resp.status_code == 200
    json_resp = json.loads(resp.data)
    assert json_resp == {'success': 'true'}
    q = db_session.query(Project).filter(Project.project_id == id_to_delete).all()
    assert len(q) == 0

def test_try_function_name(client):
    resp = get_all_projects() 
    assert resp.status_code == 200
    json_resp = json.loads(resp.data)
    assert len(json_resp) == 1
    
