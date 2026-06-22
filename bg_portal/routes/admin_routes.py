from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from utils.auth_decorators import login_required, admin_required
from datetime import datetime
import uuid

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
@admin_required
def dashboard():
    store = current_app.extensions['demo_store']
    reqs = store.list_requests()
    pending = [r for r in reqs if r.get('status') == 'Pending']
    approved = [r for r in reqs if r.get('status') == 'Approved']
    rejected = [r for r in reqs if r.get('status') == 'Rejected']
    return render_template(
        'dashboard/admin_home.html',
        requests=reqs,
        pending=pending,
        approved=approved,
        rejected=rejected,
        activity=store.get_activity(10),
    )

@admin_bp.route('/admin/requests')
@admin_required
def all_requests():
    store = current_app.extensions['demo_store']
    return render_template('admin/all_requests.html', requests=store.list_requests())

@admin_bp.route('/admin/approved')
@admin_required
def approved():
    store = current_app.extensions['demo_store']
    return render_template('admin/approved_requests.html', requests=[r for r in store.list_requests() if r.get('status') == 'Approved'])

@admin_bp.route('/admin/rejected')
@admin_required
def rejected():
    store = current_app.extensions['demo_store']
    return render_template('admin/rejected_requests.html', requests=[r for r in store.list_requests() if r.get('status') == 'Rejected'])

@admin_bp.route('/admin/users')
@admin_required
def users():
    store = current_app.extensions['demo_store']
    return render_template('admin/user_management.html', profiles=store.list_profiles())

@admin_bp.route('/admin/request/<request_id>/update-status', methods=['POST'])
@admin_required
def update_status(request_id):
    store = current_app.extensions['demo_store']
    req = store.get_request(request_id)
    if not req:
        flash('Request not found.', 'error')
        return redirect(url_for('approval.pending'))
    new_status = request.form.get('new_status')
    req['status'] = new_status
    req['admin_remarks'] = request.form.get('admin_remarks', '')
    req['decided_by'] = session['user']['id']
    req['decision_at'] = datetime.utcnow().isoformat()
    store.add_request(req)
    store.add_activity({
        'id': str(uuid.uuid4()),
        'bg_request_id': request_id,
        'action_by': session['user']['id'],
        'action': 'Updated status',
        'old_status': req.get('status'),
        'new_status': new_status,
        'note': req['admin_remarks'],
        'created_at': datetime.utcnow().isoformat(),
    })
    flash('Status updated.', 'success')
    return redirect(url_for('approval.pending'))

@admin_bp.route('/admin/user/<user_id>/update-role', methods=['POST'])
@admin_required
def update_role(user_id):
    store = current_app.extensions['demo_store']
    profile = store.get_profile(user_id)
    if profile:
        profile['role'] = request.form.get('role', profile['role'])
        store.add_profile(profile)
        flash('Role updated.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/admin/user/<user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_status(user_id):
    store = current_app.extensions['demo_store']
    profile = store.get_profile(user_id)
    if profile:
        profile['is_active'] = not profile.get('is_active', True)
        store.add_profile(profile)
        flash('User status updated.', 'success')
    return redirect(url_for('admin.users'))
