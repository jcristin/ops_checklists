from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_mail import Message
from app import mail
from app.db import (
    get_templates, get_template, add_template, update_template, delete_template,
    get_template_items, create_template_item, delete_template_item, get_max_position,
    get_checklists, get_checklist, create_checklist, update_checklist, delete_checklist,
    get_checklist_by_template_date, get_recent_checklists, get_today_checklists_count,
    get_checklist_items, create_checklist_item, update_checklist_item, get_checklist_item,
    get_recipients, get_active_recipients, get_recipient, add_recipient, update_recipient, delete_recipient,
    get_templates_count, get_checklists_count, get_recipients_count
)
from app.forms import (
    TemplateForm, TemplateItemForm, DailyChecklistForm, 
    CompleteChecklistForm, ChecklistItemForm, EmailRecipientForm
)
from datetime import datetime

# Create blueprints
main_bp = Blueprint('main', __name__)
templates_bp = Blueprint('templates', __name__)
checklists_bp = Blueprint('checklists', __name__)
admin_bp = Blueprint('admin', __name__)

# Helper functions
def send_checklist_email(checklist):
    """Send email with checklist details to all active recipients"""
    recipients = get_active_recipients()
    if not recipients:
        flash('No active email recipients found. Email not sent.', 'warning')
        return False
    
    recipient_emails = [r['email'] for r in recipients]
    template_name = checklist['template_name']
    date_str = checklist['date']
    
    # Create email subject and body
    subject = f'Operations Checklist: {template_name} - {date_str}'
    
    # Get checklist items
    items = get_checklist_items(checklist['id'])
    
    # Create HTML table for checklist items
    items_html = '<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">'
    items_html += '<tr><th>Group</th><th>Item</th><th>Time</th><th>Status</th></tr>'
    
    # Add items to the table
    for item in sorted(items, key=lambda x: x['position']):
        status_color = 'green' if item['status'] == 'OK' else 'red'
        items_html += f'<tr>'
        items_html += f'<td>{item["group_name"]}</td>'
        items_html += f'<td>{item["item"]}</td>'
        items_html += f'<td>{item["time"]}</td>'
        items_html += f'<td style="color: {status_color}; font-weight: bold;">{item["status"]}</td>'
        items_html += f'</tr>'
    
    items_html += '</table>'
    
    # Complete email body
    body_html = f'''
    <html>
    <body>
        <h2>Operations Checklist: {template_name}</h2>
        <p>Date: {date_str}</p>
        <p>Please find below the completed checklist:</p>
        {items_html}
        <p>This is an automated message from the Operations Checklists application.</p>
    </body>
    </html>
    '''
    
    # Create and send the message
    msg = Message(
        subject=subject,
        recipients=recipient_emails,
        html=body_html,
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    
    try:
        mail.send(msg)
        update_checklist(checklist['id'], sent=True)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        flash(f'Failed to send email: {str(e)}', 'danger')
        return False

# Main routes
@main_bp.route('/')
def index():
    """Home page"""
    # Get counts for dashboard
    templates_count = get_templates_count()
    checklists_count = get_checklists_count()
    today_checklists = get_today_checklists_count()
    recipients_count = get_recipients_count()
    
    # Get recent checklists
    recent_checklists = get_recent_checklists(5)
    
    return render_template(
        'index.html', 
        templates_count=templates_count,
        checklists_count=checklists_count,
        today_checklists=today_checklists,
        recipients_count=recipients_count,
        recent_checklists=recent_checklists
    )

# Template routes
@templates_bp.route('/')
def list_templates():
    """List all checklist templates"""
    templates = get_templates()
    return render_template('templates/list.html', templates=templates)

@templates_bp.route('/create', methods=['GET', 'POST'])
def create_template():
    """Create a new checklist template"""
    form = TemplateForm()
    if form.validate_on_submit():
        template_id = add_template(form.name.data)
        flash(f'Template "{form.name.data}" created successfully!', 'success')
        return redirect(url_for('templates.edit_template', template_id=template_id))
    return render_template('templates/create.html', form=form)

@templates_bp.route('/<int:template_id>/edit', methods=['GET', 'POST'])
def edit_template(template_id):
    """Edit a checklist template and its items"""
    template = get_template(template_id)
    if not template:
        abort(404)
        
    template_form = TemplateForm(obj=template)
    item_form = TemplateItemForm()
    
    if template_form.validate_on_submit():
        update_template(template_id, template_form.name.data)
        flash('Template updated successfully!', 'success')
        return redirect(url_for('templates.edit_template', template_id=template_id))
    
    items = get_template_items(template_id)
    return render_template(
        'templates/edit.html', 
        template=template, 
        template_form=template_form,
        item_form=item_form,
        items=items
    )

@templates_bp.route('/<int:template_id>/items/add', methods=['POST'])
def add_template_item(template_id):
    """Add an item to a template"""
    template = get_template(template_id)
    if not template:
        abort(404)
        
    form = TemplateItemForm()
    
    if form.validate_on_submit():
        # Get the highest position value and add 1
        max_position = get_max_position(template_id)
        
        create_template_item(
            template_id=template_id,
            group=form.group.data,
            item=form.item.data,
            position=max_position + 1
        )
        flash('Item added to template!', 'success')
    
    return redirect(url_for('templates.edit_template', template_id=template_id))

@templates_bp.route('/<int:template_id>/items/<int:item_id>/delete')
def delete_template_item(template_id, item_id):
    """Delete an item from a template"""
    # No need to verify the item belongs to the template since we're using direct SQL
    delete_template_item(item_id)
    flash('Item deleted from template!', 'success')
    
    return redirect(url_for('templates.edit_template', template_id=template_id))

@templates_bp.route('/<int:template_id>/delete', methods=['POST'])
def delete_template(template_id):
    """Delete a checklist template"""
    template = get_template(template_id)
    if not template:
        abort(404)
        
    name = template['name']
    delete_template(template_id)
    flash(f'Template "{name}" deleted successfully!', 'success')
    
    return redirect(url_for('templates.list_templates'))

# Checklist routes
@checklists_bp.route('/')
def list_checklists():
    """List all daily checklists"""
    checklists = get_checklists()
    return render_template('checklists/list.html', checklists=checklists)

@checklists_bp.route('/create', methods=['GET', 'POST'])
def create_checklist():
    """Create a new daily checklist"""
    form = DailyChecklistForm()
    
    # Set default date to today
    if request.method == 'GET':
        form.date.data = datetime.now().date()
    
    if form.validate_on_submit():
        template = get_template(form.template_id.data)
        if not template:
            abort(404)
            
        # Format date as string
        date_str = form.date.data.strftime('%Y-%m-%d')
        
        # Check if a checklist already exists for this template and date
        existing = get_checklist_by_template_date(template['id'], date_str)
        
        if existing:
            flash(f'A checklist for "{template["name"]}" on {date_str} already exists!', 'warning')
            return redirect(url_for('checklists.edit_checklist', checklist_id=existing['id']))
        
        # Create new checklist
        checklist_id = create_checklist(template['id'], date_str)
                
        # Create checklist items based on template items
        template_items = get_template_items(template['id'])
        for item in template_items:
            create_checklist_item(
                checklist_id=checklist_id,
                group=item['group_name'],
                item=item['item'],
                position=item['position']
            )
        
        flash('Checklist created successfully!', 'success')
        return redirect(url_for('checklists.edit_checklist', checklist_id=checklist_id))
    
    return render_template('checklists/create.html', form=form)

@checklists_bp.route('/<int:checklist_id>/edit', methods=['GET', 'POST'])
def edit_checklist(checklist_id):
    """Edit a daily checklist"""
    checklist = get_checklist(checklist_id)
    if not checklist:
        abort(404)
        
    # Create a form with a field for each checklist item
    form = CompleteChecklistForm()
    
    if request.method == 'GET':
        # Populate form with existing items
        form.items.entries = []
        items = get_checklist_items(checklist_id)
        for item in sorted(items, key=lambda x: x['position']):
            item_form = ChecklistItemForm()
            item_form.id.data = item['id']
            item_form.group.data = item['group_name']
            item_form.item.data = item['item']
            item_form.time.data = item['time']
            item_form.status.data = item['status']
            form.items.append_entry(item_form.data)
    
    if form.validate_on_submit():
        for i, item_data in enumerate(form.items.data):
            update_checklist_item(
                item_id=item_data['id'],
                time=item_data['time'],
                status=item_data['status']
            )
        
        update_checklist(checklist_id, completed=True)
        flash('Checklist saved successfully!', 'success')
        
        # Redirect to view page
        return redirect(url_for('checklists.view_checklist', checklist_id=checklist_id))
    
    return render_template('checklists/edit.html', form=form, checklist=checklist)

@checklists_bp.route('/<int:checklist_id>/view')
def view_checklist(checklist_id):
    """View a completed checklist"""
    checklist = get_checklist(checklist_id)
    if not checklist:
        abort(404)
        
    items = get_checklist_items(checklist_id)
    items = sorted(items, key=lambda x: x['position'])
    
    return render_template('checklists/view.html', checklist=checklist, items=items)

@checklists_bp.route('/<int:checklist_id>/send', methods=['POST'])
def send_checklist(checklist_id):
    """Send a checklist by email"""
    checklist = get_checklist(checklist_id)
    if not checklist:
        abort(404)
        
    if not checklist['completed']:
        flash('Cannot send an incomplete checklist!', 'danger')
        return redirect(url_for('checklists.view_checklist', checklist_id=checklist_id))
    
    if send_checklist_email(checklist):
        flash('Checklist sent by email successfully!', 'success')
    else:
        flash('Failed to send checklist by email.', 'danger')
    
    return redirect(url_for('checklists.view_checklist', checklist_id=checklist_id))

@checklists_bp.route('/<int:checklist_id>/delete', methods=['POST'])
def delete_checklist(checklist_id):
    """Delete a daily checklist"""
    checklist = get_checklist(checklist_id)
    if not checklist:
        abort(404)
        
    date_str = checklist['date']
    template_name = checklist['template_name']
    
    delete_checklist(checklist_id)
    flash(f'Checklist for "{template_name}" on {date_str} deleted successfully!', 'success')
    
    return redirect(url_for('checklists.list_checklists'))

# Admin routes
@admin_bp.route('/recipients')
def list_recipients():
    """List all email recipients"""
    recipients = get_recipients()
    return render_template('admin/recipients.html', recipients=recipients)

@admin_bp.route('/recipients/create', methods=['GET', 'POST'])
def create_recipient():
    """Create a new email recipient"""
    form = EmailRecipientForm()
    
    if form.validate_on_submit():
        add_recipient(
            email=form.email.data,
            name=form.name.data,
            active=form.active.data
        )
        flash(f'Recipient {form.email.data} added successfully!', 'success')
        return redirect(url_for('admin.list_recipients'))
    
    return render_template('admin/create_recipient.html', form=form)

@admin_bp.route('/recipients/<int:recipient_id>/edit', methods=['GET', 'POST'])
def edit_recipient(recipient_id):
    """Edit an email recipient"""
    recipient = get_recipient(recipient_id)
    if not recipient:
        abort(404)
        
    form = EmailRecipientForm(obj=recipient)
    
    if form.validate_on_submit():
        update_recipient(
            recipient_id=recipient_id,
            email=form.email.data,
            name=form.name.data,
            active=form.active.data
        )
        flash(f'Recipient {form.email.data} updated successfully!', 'success')
        return redirect(url_for('admin.list_recipients'))
    
    return render_template('admin/edit_recipient.html', form=form, recipient=recipient)

@admin_bp.route('/recipients/<int:recipient_id>/delete', methods=['POST'])
def delete_recipient(recipient_id):
    """Delete an email recipient"""
    recipient = get_recipient(recipient_id)
    if not recipient:
        abort(404)
        
    email = recipient['email']
    delete_recipient(recipient_id)
    flash(f'Recipient {email} deleted successfully!', 'success')
    
    return redirect(url_for('admin.list_recipients'))
