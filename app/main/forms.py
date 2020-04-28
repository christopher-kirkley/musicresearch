from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, validators, RadioField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()]) 
    link = StringField('Link', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[DataRequired()])
    in_contact = RadioField(choices=[(0, 'In-Progress'),(1, 'In-Contact')], coerce=int)

    submit = SubmitField('Submit')

class ProjectForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    evernote = StringField('Link', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit')

