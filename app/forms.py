from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, SubmitField, BooleanField, HiddenField, FieldList, FormField
from wtforms.validators import DataRequired, Email, ValidationError, Optional
from app.db import get_templates, get_recipient_by_email
from datetime import datetime

class TemplateForm(FlaskForm):
    """Form for creating/editing checklist templates"""
    name = StringField('Template Name', validators=[DataRequired()])
    submit = SubmitField('Save Template')

class TemplateItemForm(FlaskForm):
    """Form for adding items to templates"""
    group = StringField('Group', validators=[DataRequired()])
    item = StringField('Item Description', validators=[DataRequired()])
    submit = SubmitField('Add Item')

class EmailRecipientForm(FlaskForm):
    """Form for managing email recipients"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Name', validators=[Optional()])
    active = BooleanField('Active', default=True)
    submit = SubmitField('Save Recipient')
    
    def __init__(self, *args, **kwargs):
        super(EmailRecipientForm, self).__init__(*args, **kwargs)
        self.original_email = kwargs.get('obj', {}).get('email', None)
    
    def validate_email(self, email):
        if email.data != self.original_email:
            recipient = get_recipient_by_email(email.data)
            if recipient:
                raise ValidationError('Email already registered.')

class DailyChecklistForm(FlaskForm):
    """Form for creating daily checklists"""
    template_id = SelectField('Template', coerce=int, validators=[DataRequired()])
    date = DateField('Date', default=datetime.now, validators=[DataRequired()])
    submit = SubmitField('Create Checklist')
    
    def __init__(self, *args, **kwargs):
        super(DailyChecklistForm, self).__init__(*args, **kwargs)
        templates = get_templates()
        self.template_id.choices = [(t['id'], t['name']) for t in templates]

class ChecklistItemForm(FlaskForm):
    """Form for a single checklist item in a daily checklist"""
    id = HiddenField()
    group = HiddenField()
    item = HiddenField()
    time = StringField('Time', validators=[DataRequired()])
    status = SelectField('Status', choices=[('OK', 'OK'), ('Fail', 'Fail')], validators=[DataRequired()])

class CompleteChecklistForm(FlaskForm):
    """Form for completing a daily checklist with multiple items"""
    items = FieldList(FormField(ChecklistItemForm))
    submit = SubmitField('Save Checklist')
