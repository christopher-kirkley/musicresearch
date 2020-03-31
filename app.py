from flask import Flask, render_template, jsonify, request, redirect, url_for
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config import Config
from forms import ContactForm

app = Flask(__name__)

config = Config()

SQLALCHEMY_DATABASE_URI = f"postgresql://{config.USERNAME}:{config.PASSWORD}@localhost:5432/{config.DATABASE}"

engine = create_engine(SQLALCHEMY_DATABASE_URI)
db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
metadata = Base.metadata
metadata.bind=engine

# Models - declarative auto-load
class Contact(Base):
    __tablename__ = 'contact'
    __table_args__ = {'autoload':True}

class Project(Base):
    __tablename__ = 'project'
    __table_args__ = {'autoload':True}

@app.route('/', methods=['GET'])
def index():
    # x = db_session.execute("SELECT * FROM contact;").fetchall()
    projects = db_session.query(Project).all()
    return render_template('index.html', projects=projects)

@app.route('/add_project', methods=['GET', 'POST'])
def add_project():

    if request.method == 'POST':
        name = request.form.get('name')
        link = request.form.get('link')
        description = request.form.get('description')

        new_project = Project(
                            name=name,
                            evernote=link,
                            description=description,
                            active=bool(0)
                            )
        db_session.add(new_project)
        db_session.commit()

    return render_template('add_project.html')

@app.route('/<int:id>', methods=['GET', 'POST'])
def project(id):

    if request.method == 'POST':
        if request.form.get('submit'):
            name = request.form.get('name')
            link = request.form.get('link')
            notes = request.form.get('notes')
            in_contact = request.form.get('in-contact')
            new_contact = Contact(
                                project_id=id,
                                name=name,
                                link=link,
                                notes=notes,
                                in_contact=bool(int(in_contact)),
                                active=bool(0))
            db_session.add(new_contact)
            db_session.commit()
        if request.form.get('update'):
            return 'x'
        if request.form.get('delete'):
            id_to_delete = request.form.get('id')
            db_session.query(Contact).filter(Contact.contact_id==id_to_delete).delete()
            db_session.commit()
            return redirect(url_for('project', id=id))

    queued_contacts = (db_session
            .query(Contact)
            .filter(Contact.project_id == id)
            .filter(Contact.in_contact == 'false')
            .all()
            )
    current_contacts = (db_session
            .query(Contact)
            .filter(Contact.project_id == id)
            .filter(Contact.in_contact == 'true')
            .all()
            )
    project = (db_session
            .query(Project)
            .filter(Project.project_id == id)
            .first()
            )
    return render_template('project.html', queued_contacts=queued_contacts,
            current_contacts=current_contacts, project=project) 

@app.route('/get_projects', methods=['GET'])
def get_projects():
    # x = db_session.execute("SELECT * FROM contact;").fetchall()
    projects = db_session.query(Project.project_id, Project.name).order_by(Project.name).all()
    return jsonify(projects)

if __name__ == '__main__':
    app.run(debug=True)
