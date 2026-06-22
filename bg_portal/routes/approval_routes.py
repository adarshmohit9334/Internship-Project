from flask import Blueprint, render_template, current_app
from utils.auth_decorators import login_required

approval_bp = Blueprint('approval', __name__)

@approval_bp.route('/admin/pending')
@login_required
def pending():
    store = current_app.extensions['demo_store']
    requests = [r for r in store.list_requests() if r.get('status') in ('Pending', 'Under Review')]
    requests.sort(key=lambda r: r.get('created_at', ''))
    return render_template('admin/pending_approvals.html', requests=requests)
