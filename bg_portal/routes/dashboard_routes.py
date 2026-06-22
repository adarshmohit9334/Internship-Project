from flask import Blueprint, render_template, session, current_app
from utils.auth_decorators import login_required

dashboard_bp = Blueprint('dashboard', __name__)

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
