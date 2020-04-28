from flask import Blueprint, render_template, request

from datetime import date
from database import db_session

from app.models import Contact, Project

from app.main.forms import ContactForm, ProjectForm

main = Blueprint(
        'main', __name__,
        template_folder='templates',
                )

@main.route('/', methods=['GET'])
def index():

    today = date.today()
    
    pending_contacts = (db_session.query(Contact.contact_id,
                                        Contact.name.label('contact_name'),
                                        Contact.link,
                                        Contact.checked,
                                        Project.project_id,
                                        Project.name.label('project_name'),
                                        Project.evernote)
                                        .join(Project, Project.project_id == Contact.project_id)
                                        .order_by(Contact.checked)
                                        .filter(today - Contact.checked > 7)
                                        .all()
                                        )

    return render_template('dashboard.html', pending_contacts=pending_contacts)

@main.route('/add_project', methods=['GET', 'POST'])
def add_project():

    title = 'Add Project'
    
    return render_template('add_project.html', title=title)

@main.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
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
        return redirect(url_for('main.index'))
        
    return render_template('add_project.html', title=title, form=form)

@main.route('/<int:project_id>', methods=['GET', 'POST'])
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
        return redirect(url_for('main.project', project_id=project_id))

    contact_id = request.form.get('id')

    if request.form.get('update'):
        contact = db_session.query(Contact).get(contact_id)
        today = date.today()
        contact.checked = today
        db_session.commit()
    if request.form.get('edit'):
        return redirect(url_for('main.edit_contact', contact_id=contact_id, project_id=project_id))

    queued_contacts = (db_session
            .query(Contact)
            .filter(Contact.project_id == project_id)
            .filter(Contact.in_contact == 'false')
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

@main.route('/<int:project_id>/edit_contact/<int:contact_id>', methods=['GET', 'POST'])
def edit_contact(project_id, contact_id):

    contact_obj = db_session.query(Contact).get(contact_id)

    form = ContactForm(obj=contact_obj)

    if form.validate_on_submit():
        form.populate_obj(contact_obj)
        contact_obj.name=form.name.data
        contact_obj.link=form.link.data
        contact_obj.notes=form.notes.data
        db_session.commit()
        return redirect(url_for('main.project', project_id=project_id, contact_id=contact_id))
    if request.form.get('delete'):
        db_session.query(Contact).filter(Contact.contact_id==contact_id).delete()
        db_session.commit()
        return redirect(url_for('main.project', project_id=project_id))

    return render_template('edit_contact.html', form=form)

