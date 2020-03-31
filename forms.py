from wtforms import Form, BooleanField, StringField, validators, RadioField

class ContactForm(Form):
    name = StringField('Name', [validators.Length(min=4, max=25)])
    link = StringField('Link', [validators.Length(min=4, max=200)])
    notes = StringField('Name', [validators.Length(min=4, max=200)])
    in_contact = RadioField(choices=[(1, 'In-Progress'),(2, 'In-Contact')])

