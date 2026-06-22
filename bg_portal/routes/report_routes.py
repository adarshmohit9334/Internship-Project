from flask import Blueprint, render_template, current_app
from utils.auth_decorators import login_required

report_bp = Blueprint('report', __name__)

@report_bp.route('/admin/reports')
@login_required
def reports():
    store = current_app.extensions['demo_store']
    requests = store.list_requests()
    total_bg_amount = sum(
        float(r.get('bg_amount', 0) or 0)
        for r in requests
    )
    return render_template(
        'admin/reports_analytics.html',
        requests=requests,
        total_bg_amount=total_bg_amount,
    )
