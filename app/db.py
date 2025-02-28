import sqlite3
from datetime import datetime
from flask import current_app, g
from app import get_db

def init_db():
    """Initialize the database with tables"""
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
    db.commit()

def query_db(query, args=(), one=False):
    """Query the database and return results"""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def insert_db(table, fields=None):
    """Insert into the database and return the last row id"""
    if fields is None:
        return None
    
    placeholders = ', '.join(['?'] * len(fields))
    columns = ', '.join(fields.keys())
    values = tuple(fields.values())
    
    sql = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
    
    db = get_db()
    cur = db.execute(sql, values)
    db.commit()
    return cur.lastrowid

def update_db(table, fields, condition):
    """Update the database"""
    if fields is None:
        return False
    
    set_clause = ', '.join([f'{key} = ?' for key in fields.keys()])
    values = tuple(fields.values())
    
    sql = f'UPDATE {table} SET {set_clause} WHERE {condition[0]}'
    
    db = get_db()
    db.execute(sql, values + condition[1])
    db.commit()
    return True

def delete_db(table, condition):
    """Delete from the database"""
    sql = f'DELETE FROM {table} WHERE {condition[0]}'
    
    db = get_db()
    db.execute(sql, condition[1])
    db.commit()
    return True

# Helper functions for specific tables

# ChecklistTemplate functions
def get_templates():
    """Get all checklist templates"""
    return query_db('SELECT * FROM checklist_template ORDER BY name')

def get_template(template_id):
    """Get a checklist template by ID"""
    return query_db('SELECT * FROM checklist_template WHERE id = ?', (template_id,), one=True)

def add_template(name):
    """Create a new checklist template"""
    return insert_db('checklist_template', {
        'name': name,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

def update_template(template_id, name):
    """Update a checklist template"""
    return update_db('checklist_template', {'name': name}, ('id = ?', (template_id,)))

def delete_template(template_id):
    """Delete a checklist template"""
    return delete_db('checklist_template', ('id = ?', (template_id,)))

# TemplateItem functions
def get_template_items(template_id):
    """Get all items for a template"""
    return query_db('SELECT * FROM template_item WHERE template_id = ? ORDER BY position', (template_id,))

def create_template_item(template_id, group, item, position):
    """Create a new template item"""
    return insert_db('template_item', {
        'template_id': template_id,
        'group_name': group,
        'item': item,
        'position': position
    })

def delete_template_item(item_id):
    """Delete a template item"""
    return delete_db('template_item', ('id = ?', (item_id,)))

def get_max_position(template_id):
    """Get the maximum position for a template"""
    result = query_db('SELECT MAX(position) as max_pos FROM template_item WHERE template_id = ?', 
                     (template_id,), one=True)
    return result['max_pos'] if result and result['max_pos'] is not None else 0

# DailyChecklist functions
def get_checklists():
    """Get all daily checklists"""
    return query_db('''
        SELECT c.*, t.name as template_name 
        FROM daily_checklist c
        JOIN checklist_template t ON c.template_id = t.id
        ORDER BY c.date DESC
    ''')

def get_checklist(checklist_id):
    """Get a daily checklist by ID"""
    return query_db('''
        SELECT c.*, t.name as template_name 
        FROM daily_checklist c
        JOIN checklist_template t ON c.template_id = t.id
        WHERE c.id = ?
    ''', (checklist_id,), one=True)

def create_checklist(template_id, date):
    """Create a new daily checklist"""
    return insert_db('daily_checklist', {
        'template_id': template_id,
        'date': date,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'completed': 0,
        'sent': 0
    })

def update_checklist(checklist_id, completed=None, sent=None):
    """Update a daily checklist"""
    fields = {}
    if completed is not None:
        fields['completed'] = 1 if completed else 0
    if sent is not None:
        fields['sent'] = 1 if sent else 0
    
    if fields:
        return update_db('daily_checklist', fields, ('id = ?', (checklist_id,)))
    return False

def delete_checklist(checklist_id):
    """Delete a daily checklist"""
    return delete_db('daily_checklist', ('id = ?', (checklist_id,)))

def get_checklist_by_template_date(template_id, date):
    """Get a checklist by template ID and date"""
    return query_db('''
        SELECT * FROM daily_checklist 
        WHERE template_id = ? AND date = ?
    ''', (template_id, date), one=True)

def get_recent_checklists(limit=5):
    """Get recent checklists"""
    return query_db('''
        SELECT c.*, t.name as template_name 
        FROM daily_checklist c
        JOIN checklist_template t ON c.template_id = t.id
        ORDER BY c.created_at DESC
        LIMIT ?
    ''', (limit,))

def get_today_checklists_count():
    """Get count of today's checklists"""
    result = query_db('''
        SELECT COUNT(*) as count FROM daily_checklist 
        WHERE date = ?
    ''', (datetime.now().strftime('%Y-%m-%d'),), one=True)
    return result['count'] if result else 0

# ChecklistItem functions
def get_checklist_items(checklist_id):
    """Get all items for a checklist"""
    return query_db('SELECT * FROM checklist_item WHERE checklist_id = ? ORDER BY position', (checklist_id,))

def create_checklist_item(checklist_id, group, item, position):
    """Create a new checklist item"""
    return insert_db('checklist_item', {
        'checklist_id': checklist_id,
        'group_name': group,
        'item': item,
        'position': position,
        'time': None,
        'status': None
    })

def update_checklist_item(item_id, time, status):
    """Update a checklist item"""
    return update_db('checklist_item', {
        'time': time,
        'status': status
    }, ('id = ?', (item_id,)))

def get_checklist_item(item_id):
    """Get a checklist item by ID"""
    return query_db('SELECT * FROM checklist_item WHERE id = ?', (item_id,), one=True)

# EmailRecipient functions
def get_recipients():
    """Get all email recipients"""
    return query_db('SELECT * FROM email_recipient ORDER BY email')

def get_active_recipients():
    """Get all active email recipients"""
    return query_db('SELECT * FROM email_recipient WHERE active = 1 ORDER BY email')

def get_recipient(recipient_id):
    """Get an email recipient by ID"""
    return query_db('SELECT * FROM email_recipient WHERE id = ?', (recipient_id,), one=True)

def add_recipient(email, name, active):
    """Create a new email recipient"""
    return insert_db('email_recipient', {
        'email': email,
        'name': name,
        'active': 1 if active else 0
    })

def update_recipient(recipient_id, email, name, active):
    """Update an email recipient"""
    return update_db('email_recipient', {
        'email': email,
        'name': name,
        'active': 1 if active else 0
    }, ('id = ?', (recipient_id,)))

def delete_recipient(recipient_id):
    """Delete an email recipient"""
    return delete_db('email_recipient', ('id = ?', (recipient_id,)))

def get_recipient_by_email(email):
    """Get a recipient by email"""
    return query_db('SELECT * FROM email_recipient WHERE email = ?', (email,), one=True)

# Count functions for dashboard
def get_templates_count():
    """Get count of templates"""
    result = query_db('SELECT COUNT(*) as count FROM checklist_template', one=True)
    return result['count'] if result else 0

def get_checklists_count():
    """Get count of checklists"""
    result = query_db('SELECT COUNT(*) as count FROM daily_checklist', one=True)
    return result['count'] if result else 0

def get_recipients_count():
    """Get count of active recipients"""
    result = query_db('SELECT COUNT(*) as count FROM email_recipient WHERE active = 1', one=True)
    return result['count'] if result else 0
