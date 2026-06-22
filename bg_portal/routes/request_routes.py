from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from utils.auth_decorators import login_required
from utils.approval_logic import get_approval_level, validate_attachments
from utils.file_helpers import upload_attachment, get_signed_url
import uuid
from datetime import datetime, date

request_bp = Blueprint('request', __name__)

def get_profile_for_session():
    user = session.get('user')
    if not user:
        return None
    return current_app.extensions['demo_store'].get_profile(user['id'])

@request_bp.route('/request/new')
@login_required
def new_request():
    profile = get_profile_for_session()
    store = current_app.extensions['demo_store']
    alternatives = [p for p in store.list_profiles() if p['id'] != profile['id']]
    return render_template(
        'requests/new_request.html',
        profile=profile,
        alternatives=alternatives,
        today=date.today().isoformat(),
    )

@request_bp.route('/request/save-draft', methods=['POST'])
@login_required
def save_draft():
    profile = get_profile_for_session()
    request_id = str(uuid.uuid4())
    data = {
        'id': request_id,
        'requester_id': profile['id'],
        'department': request.form.get('department', profile.get('department', '')),
        'location': request.form.get('location', ''),
        'date_of_request': request.form.get('date_of_request', date.today().isoformat()),
        'work_order_no': request.form.get('work_order_no', ''),
        'type_of_work': request.form.get('type_of_work', ''),
        'job_value': request.form.get('job_value', 0),
        'alternate_owner_id': request.form.get('alternate_owner_id', ''),
        'party_name': request.form.get('party_name', ''),
        'nature_of_bg': request.form.get('nature_of_bg', ''),
        'bg_amount': request.form.get('bg_amount', 0),
        'bg_expiry_date': request.form.get('bg_expiry_date', ''),
        'bg_claim_period': request.form.get('bg_claim_period', ''),
        'remarks': request.form.get('remarks', ''),
        'approval_level': get_approval_level(request.form.get('bg_amount', 0)),
        'status': 'Draft',
        'admin_remarks': '',
        'decided_by': None,
        'decision_at': None,
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat(),
    }
    current_app.extensions['demo_store'].add_request(data)
    flash('Saved as draft.', 'success')
    return redirect(url_for('request.my_requests'))

@request_bp.route('/request/submit', methods=['POST'])
@login_required
def submit_request():
    profile = get_profile_for_session()
    bg_amount = float(request.form.get('bg_amount', 0) or 0)
    approval_level = get_approval_level(bg_amount)
    errors = validate_attachments(request.files, approval_level)
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('request.new_request'))
    request_id = str(uuid.uuid4())
    data = {
        'id': request_id,
        'requester_id': profile['id'],
        'department': request.form.get('department', profile.get('department', '')),
        'location': request.form.get('location', ''),
        'date_of_request': request.form.get('date_of_request', date.today().isoformat()),
        'work_order_no': request.form.get('work_order_no', ''),
        'type_of_work': request.form.get('type_of_work', ''),
        'job_value': request.form.get('job_value', 0),
        'alternate_owner_id': request.form.get('alternate_owner_id', ''),
        'party_name': request.form.get('party_name', ''),
        'nature_of_bg': request.form.get('nature_of_bg', ''),
        'bg_amount': bg_amount,
        'bg_expiry_date': request.form.get('bg_expiry_date', ''),
        'bg_claim_period': request.form.get('bg_claim_period', ''),
        'remarks': request.form.get('remarks', ''),
        'approval_level': approval_level,
        'status': 'Pending',
        'admin_remarks': '',
        'decided_by': None,
        'decision_at': None,
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat(),
    }
    store = current_app.extensions['demo_store']
    store.add_request(data)
    for field in ['bg_vetted_draft', 'md_approval', 'board_approval', 'beneficiary_clause', 'bank_account_details']:
        if field in request.files and request.files[field].filename:
            upload_path = upload_attachment(request.files[field], request_id, field)
            store.add_attachment({
                'id': str(uuid.uuid4()),
                'bg_request_id': request_id,
                'attachment_type': field,
                'file_name': request.files[field].filename,
                'file_path': upload_path,
                'uploaded_at': datetime.utcnow().isoformat(),
            })
    store.add_activity({
        'id': str(uuid.uuid4()),
        'bg_request_id': request_id,
        'action_by': profile['id'],
        'action': 'Submitted request',
        'old_status': 'Draft',
        'new_status': 'Pending',
        'note': 'Request submitted for approval',
        'created_at': datetime.utcnow().isoformat(),
    })
    flash('Request submitted successfully.', 'success')
    return redirect(url_for('request.my_requests'))

@request_bp.route('/my-requests')
@login_required
def my_requests():
    user = session['user']
    store = current_app.extensions['demo_store']
    requests = [r for r in store.list_requests() if r.get('requester_id') == user['id']]
    return render_template('requests/my_requests.html', requests=requests)

@request_bp.route('/request/<request_id>')
@login_required
def view_request(request_id):
    store = current_app.extensions['demo_store']
    request_data = store.get_request(request_id)
    attachments = [a for a in store.data['attachments'].values() if a.get('bg_request_id') == request_id]
    if request_data is None:
        return render_template('404.html'), 404
    for att in attachments:
        att['signed_url'] = get_signed_url(att['file_path'])
    return render_template('requests/view_request.html', request_data=request_data, attachments=attachments)
