from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from utils.auth_decorators import login_required

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/admin/settings')
@login_required
def settings():
    store = current_app.extensions['demo_store']
    return render_template('admin/settings.html', settings=store.get_settings())

@settings_bp.route('/admin/settings/save', methods=['POST'])
@login_required
def save_settings():
    store = current_app.extensions['demo_store']
    store.update_settings({
        'md_threshold': int(request.form.get('md_threshold', store.get_settings().get('md_threshold', 1500000))),
        'notify_email': request.form.get('notify_email') == 'on',
        'notify_dashboard': request.form.get('notify_dashboard') == 'on'
    })
    flash('Settings saved.', 'success')
    return redirect(url_for('settings.settings'))
