from flask import Flask, render_template, jsonify, request, redirect, url_for
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import date

from config import Config
from forms import ContactForm, ProjectForm

app = Flask(__name__)

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

@app.route('/_del_contact', methods=['GET'])
def _del_contact():
    return 'success'
    
@app.route('/get_projects', methods=['GET'])
def get_projects():
    # x = db_session.execute("SELECT * FROM contact;").fetchall()
    projects = db_session.query(Project.project_id, Project.name).order_by(Project.name).all()
    return jsonify(projects)

if __name__ == '__main__':
    app.run(debug=True)
