from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_cors import CORS
from sqlalchemy import create_engine, desc, Column, String, Integer, Boolean, Date, func
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

from datetime import date

from config import Config
from forms import ContactForm, ProjectForm


app = Flask(__name__)
CORS(app)

config = Config()

app.config['SECRET_KEY'] = config.SECRET_KEY

SQLALCHEMY_DATABASE_URI = f"postgresql://{config.USERNAME}:{config.PASSWORD}@localhost:5432/{config.DATABASE}"

engine = create_engine(SQLALCHEMY_DATABASE_URI)
db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
metadata = Base.metadata
metadata.bind=engine

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
    __table_args__ = {'autoload':True}

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

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html') 

@app.route('/add_project', methods=['GET', 'POST'])
def add_project():

    title = 'Add Project'
    
    form = ProjectForm()

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

    return render_template('add_project.html', title=title, form=form)

@app.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):

    title = 'Edit Project'

    project_obj = db_session.query(Project).get(project_id)

    form = ProjectForm(obj=project_obj)

    if form.validate_on_submit():
        form.populate_obj(project_obj)
        project_obj.name=form.name.data
        project_obj.evernote=form.evernote.data
        project_obj.description=form.description.data
        db_session.commit()
    if request.form.get('delete'):
        db_session.query(Project).filter(Project.project_id==project_id).delete()
        db_session.commit()
        return redirect(url_for('index'))
        
    return render_template('add_project.html', title=title, form=form)

@app.route('/<int:project_id>', methods=['GET', 'POST'])
def project(project_id):

    form = ContactForm()

    if form.validate_on_submit():
        new_contact = Contact(
                            project_id=project_id,
                            name=form.name.data,
                            link=form.link.data,
                            notes=form.notes.data,
                            in_contact=bool(form.in_contact.data),
                            active=bool(0))
        db_session.add(new_contact)
        db_session.commit()
        return redirect(url_for('project', project_id=project_id))

    contact_id = request.form.get('id')

    if request.form.get('update'):
        contact = db_session.query(Contact).get(contact_id)
        today = date.today()
        contact.checked = today
        db_session.commit()
    if request.form.get('edit'):
        return redirect(url_for('edit_contact', contact_id=contact_id, project_id=project_id))
    if request.form.get('delete'):
        id_to_delete = request.form.get('id')
        db_session.query(Contact).filter(Contact.contact_id==id_to_delete).delete()
        db_session.commit()
        return redirect(url_for('project', project_id=project_id))

    queued_contacts = (db_session
            .query(Contact)
            .filter(Contact.project_id == project_id)
            # .filter(Contact.in_contact == 'false')
            .all()
            )
    current_contacts = (db_session
            .query(Contact)
            .filter(Contact.project_id == project_id)
            .filter(Contact.in_contact == 'true')
            .all()
            )
    project = (db_session
            .query(Project)
            .filter(Project.project_id == project_id)
            .first()
            )
    return render_template('project.html', queued_contacts=queued_contacts,
            current_contacts=current_contacts, project=project, form=form)

@app.route('/<int:project_id>/edit_contact/<int:contact_id>', methods=['GET', 'POST'])
def edit_contact(project_id, contact_id):

    contact_obj = db_session.query(Contact).get(contact_id)

    form = ContactForm(obj=contact_obj)

    if form.validate_on_submit():
        form.populate_obj(contact_obj)
        contact_obj.name=form.name.data
        contact_obj.link=form.link.data
        contact_obj.notes=form.notes.data
        db_session.commit()
        return redirect(url_for('project', project_id=project_id, contact_id=contact_id))

    return render_template('edit_contact.html', form=form)

@app.route('/api/v1.0/project', methods=['GET'])
def get_all_projects():
    projects = db_session.query(Project).order_by(Project.name).all()
    result = projects_schema.dump(projects)
    return jsonify(result)

@app.route('/api/v1.0/project', methods=['POST'])
def create_project():
    data = request.get_json()
    new_project = Project(
                        name=data['name'],
                        evernote=data['evernote'],
                        description=data['description'],
                        )
    db_session.add(new_project)
    db_session.commit()
    return jsonify({'success': 'true'})

@app.route('/api/v1.0/project/<project_id>', methods=['GET'])
def get_project(project_id):
    project = db_session.query(Project).filter(Project.project_id==project_id).first()
    result = project_schema.dump(project)
    return jsonify(result)

@app.route('/api/v1.0/project/<project_id>', methods=['PUT'])
def update_project(project_id):
    data = request.get_json()
    project = db_session.query(Project).get(project_id)

    if 'name' in data:
        project.name=data['name']
    if 'evernote' in data:
        project.evernote=data['evernote']
    if 'description' in data:
        project.description = data['description']
    db_session.commit()
    return jsonify({'success': 'project updated'})

@app.route('/api/v1.0/project/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    db_session.query(Project).filter(Project.project_id==project_id).delete()
    db_session.commit()
    return jsonify({'success': 'project delete'})

@app.route('/api/v1.0/project/<project_id>/contact', methods=['GET'])
def get_project_contacts(project_id):
    contacts = db_session.query(Contact).filter(Contact.project_id == project_id).all()
    result = contacts_schema.dump(contacts)
    return jsonify(result)
    
@app.route('/api/v1.0/contact', methods=['POST'])
def create_contact():
    data = request.get_json()
    new_contact = Contact(
                        project_id=data['project_id'],
                        name=data['name'],
                        link=data['link'],
                        in_contact=data['in_contact'],
                        notes=data['notes'],
                        )
    db_session.add(new_contact)
    db_session.commit()
    return jsonify({'success': 'true'})

@app.route('/api/v1.0/contact/<contact_id>', methods=['GET'])
def get_contact(contact_id):
    contact = db_session.query(Contact).filter(Contact.contact_id==contact_id).first()
    result = contact_schema.dump(contact)
    return jsonify(result)

@app.route('/api/v1.0/contact/<contact_id>', methods=['PUT'])
def update_contact(contact_id):
    data = request.get_json()
    contact = db_session.query(Contact).get(contact_id)

    if 'name' in data:
        contact.name=data['name']
    if 'link' in data:
        contact.link=data['link']
    if 'in_contact' in data:
        contact.in_contact=data['in_contact']
    if 'notes' in data:
        contact.notes=data['notes']
    db_session.commit()
    return jsonify({'success': 'contact updated'})

@app.route('/api/v1.0/contact/<contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    db_session.query(Contact).filter(Contact.contact_id==contact_id).delete()
    db_session.commit()
    return jsonify({'success': 'contact delete'})


if __name__ == '__main__':
    app.run(debug=True)
