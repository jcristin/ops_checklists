from datetime import datetime
from app import db

class ChecklistTemplate(db.Model):
    """Model for checklist templates"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('TemplateItem', backref='template', lazy='dynamic', cascade='all, delete-orphan')
    checklists = db.relationship('DailyChecklist', backref='template', lazy='dynamic')
    
    def __repr__(self):
        return f'<ChecklistTemplate {self.name}>'

class TemplateItem(db.Model):
    """Model for items within a checklist template"""
    id = db.Column(db.Integer, primary_key=True)
    group = db.Column(db.String(100), nullable=False)
    item = db.Column(db.String(200), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('checklist_template.id'), nullable=False)
    position = db.Column(db.Integer, default=0)  # For ordering items
    
    def __repr__(self):
        return f'<TemplateItem {self.group}: {self.item}>'

class DailyChecklist(db.Model):
    """Model for daily checklists"""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    template_id = db.Column(db.Integer, db.ForeignKey('checklist_template.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    sent = db.Column(db.Boolean, default=False)
    items = db.relationship('ChecklistItem', backref='checklist', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<DailyChecklist {self.date} - {self.template.name if self.template else "Unknown"}>'

class ChecklistItem(db.Model):
    """Model for items within a daily checklist"""
    id = db.Column(db.Integer, primary_key=True)
    group = db.Column(db.String(100), nullable=False)
    item = db.Column(db.String(200), nullable=False)
    time = db.Column(db.String(10))  # Time when the check was performed
    status = db.Column(db.String(10))  # OK or Fail
    checklist_id = db.Column(db.Integer, db.ForeignKey('daily_checklist.id'), nullable=False)
    position = db.Column(db.Integer, default=0)  # For ordering items
    
    def __repr__(self):
        return f'<ChecklistItem {self.group}: {self.item} - {self.status}>'

class EmailRecipient(db.Model):
    """Model for email recipients"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100))
    active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<EmailRecipient {self.email}>'
