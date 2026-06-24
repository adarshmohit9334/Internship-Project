from flask import Blueprint, render_template, session, current_app, request, redirect, url_for, flash
from utils.auth_decorators import login_required
from datetime import datetime
import uuid

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/homepage')
@login_required
def homepage():
    return render_template('dashboard/homepage.html')


@dashboard_bp.route('/dashboard')
@login_required
def home():
    user = session['user']
    store = current_app.extensions['demo_store']
    requests = [r for r in store.list_requests() if r.get('requester_id') == user['id']]
    total = len(requests)
    pending = sum(1 for r in requests if r.get('status') == 'Pending')
    approved = sum(1 for r in requests if r.get('status') == 'Approved')
    rejected = sum(1 for r in requests if r.get('status') == 'Rejected')
    recent = sorted(requests, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
    return render_template(
        'dashboard/home.html',
        total=total,
        pending=pending,
        approved=approved,
        rejected=rejected,
        recent=recent,
    )


@dashboard_bp.route('/support', methods=['GET', 'POST'])
@login_required
def support():
    store = current_app.extensions['demo_store']
    user = session['user']
    if request.method == 'POST':
        ticket = {
            'id': str(uuid.uuid4()),
            'user_id': user['id'],
            'user_name': user['name'],
            'subject': request.form.get('subject', '').strip(),
            'category': request.form.get('category', '').strip(),
            'message': request.form.get('message', '').strip(),
            'created_at': datetime.utcnow().isoformat(),
            'status': 'Open'
        }
        store.add_support_ticket(ticket)
        flash('Support ticket submitted successfully. Our team will contact you shortly.', 'success')
        return redirect(url_for('dashboard.support'))
        
    tickets = [t for t in store.list_support_tickets() if t.get('user_id') == user['id']]
    return render_template('dashboard/support.html', tickets=tickets)

