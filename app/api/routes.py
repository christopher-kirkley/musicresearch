from flask import Blueprint, jsonify

from database import db_session
from app.models import Contact, Project, projects_schema

api = Blueprint('api', __name__)

@api.route('/api/v1.0/project', methods=['GET'])
def get_all_projects():
    projects = db_session.query(Project).order_by(Project.name).all()
    db_session.close()
    result = projects_schema.dump(projects)
    return jsonify(result)

@api.route('/api/v1.0/project', methods=['POST'])
def create_project():
    data = request.get_json(force=True)
    new_project = Project(
                        name=data['name'],
                        evernote=data['evernote'],
                        description=data['description'],
                        )
    db_session.add(new_project)
    db_session.commit()
    return jsonify({'success': 'true'})

@api.route('/api/v1.0/project/<project_id>', methods=['GET'])
def get_project(project_id):
    project = db_session.query(Project).filter(Project.project_id==project_id).first()
    result = project_schema.dump(project)
    return jsonify(result)

@api.route('/api/v1.0/project/<project_id>', methods=['PUT'])
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

@api.route('/api/v1.0/project/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    db_session.query(Project).filter(Project.project_id==project_id).delete()
    db_session.commit()
    return jsonify({'success': 'true'})

@api.route('/api/v1.0/project/<project_id>/contact', methods=['GET'])
def get_project_contacts(project_id):
    contacts = db_session.query(Contact).filter(Contact.project_id == project_id).all()
    result = contacts_schema.dump(contacts)
    return jsonify(result)
    
@api.route('/api/v1.0/contact', methods=['POST'])
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

@api.route('/api/v1.0/contact/<contact_id>', methods=['GET'])
def get_contact(contact_id):
    contact = db_session.query(Contact).filter(Contact.contact_id==contact_id).first()
    result = contact_schema.dump(contact)
    return jsonify(result)

@api.route('/api/v1.0/contact/<contact_id>', methods=['PUT'])
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

@api.route('/api/v1.0/contact/<contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    db_session.query(Contact).filter(Contact.contact_id==contact_id).delete()
    db_session.commit()
    return jsonify({'success': 'contact delete'})


