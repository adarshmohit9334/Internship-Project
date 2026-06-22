from functools import wraps
from flask import redirect, url_for, session, abort

def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get('user'):
            return redirect(url_for('auth.login'))
        return view_func(*args, **kwargs)
    return wrapped

def admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        user = session.get('user')
        if not user or user.get('role') != 'admin':
            return abort(403)
        return view_func(*args, **kwargs)
    return wrapped
