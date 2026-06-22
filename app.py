<<<<<<< HEAD
import json
import os
import uuid
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for
from supabase import create_client

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / 'portal_data.json'


class DemoStore:
    def __init__(self):
        self.data = self._load()

    def _load(self):
        if DATA_FILE.exists():
            try:
                return json.loads(DATA_FILE.read_text())
            except Exception:
                return self._default()
        return self._default()

    def _default(self):
        return {
            'profiles': {},
            'requests': {},
            'activity': [],
        }

    def _save(self):
        DATA_FILE.write_text(json.dumps(self.data, indent=2, default=str))

    def add_profile(self, profile):
        self.data['profiles'][profile['id']] = profile
        self._save()
        return profile

    def get_profile(self, profile_id):
        return self.data['profiles'].get(profile_id)

    def list_profiles(self):
        return list(self.data['profiles'].values())

    def add_request(self, request):
        self.data['requests'][request['id']] = request
        self._save()
        return request

    def get_request(self, request_id):
        return self.data['requests'].get(request_id)

    def list_requests(self):
        return list(self.data['requests'].values())

    def add_activity(self, item):
        self.data['activity'].append(item)
        self._save()

    def get_activity(self, limit=10):
        return self.data['activity'][-limit:]


def create_app():
    app = Flask(__name__)

    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY', 'super-secret-key-123'),
        SUPABASE_URL=os.getenv('SUPABASE_URL', ''),
        SUPABASE_KEY=os.getenv('SUPABASE_KEY', ''),
        SUPABASE_SERVICE_ROLE_KEY=os.getenv('SUPABASE_SERVICE_ROLE_KEY', os.getenv('SUPABASE_SERVICE_KEY', '')),
        SUPABASE_STORAGE_BUCKET=os.getenv('SUPABASE_STORAGE_BUCKET', 'bg-attachments'),
    )

    app.extensions['store'] = DemoStore()

    url = app.config.get('SUPABASE_URL')
    key = app.config.get('SUPABASE_KEY')
    if url and key:
        try:
            app.extensions['supabase'] = create_client(url, key)
            app.extensions['supabase_enabled'] = True
        except Exception:
            app.extensions['supabase'] = None
            app.extensions['supabase_enabled'] = False
    else:
        app.extensions['supabase'] = None
        app.extensions['supabase_enabled'] = False

    # Design tokens extracted from Stitch project 9630793419576038833
    app.config['DESIGN_TOKENS'] = {
        'primary': '#001256',
        'on_primary': '#ffffff',
        'primary_container': '#1b2a6b',
        'on_primary_container': '#8694db',
        'secondary': '#3a54c4',
        'surface': '#f8f9fb',
        'surface_container': '#eceef0',
        'surface_container_high': '#e6e8ea',
        'on_surface': '#191c1e',
        'on_surface_variant': '#454650',
        'outline': '#767681',
        'background': '#f8f9fb',
        'font_family': 'Arimo, sans-serif'
    }

    @app.route('/')
    def index():
        return redirect(url_for('pending_approvals'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            store = app.extensions['store']
            profile = None
            for p in store.list_profiles():
                if p.get('email') == email:
                    profile = p
                    break
            if not profile or profile.get('password') != password:
                flash('Invalid email or password.', 'error')
                return redirect(url_for('login'))
            session['user'] = {
                'id': profile['id'],
                'name': profile.get('name'),
                'email': profile.get('email'),
                'role': profile.get('role', 'requester')
            }
            return redirect(url_for('pending_approvals'))
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))

    @app.route('/new-application', methods=['GET', 'POST'])
    def new_application():
        if request.method == 'POST':
            data = {
                'id': str(uuid.uuid4()),
                'applicant_name': request.form.get('applicant_name', '').strip(),
                'customer_id': request.form.get('customer_id', '').strip(),
                'product_category': request.form.get('product_category', 'Performance Bond'),
                'requested_amount': request.form.get('requested_amount', '0'),
                'description': request.form.get('description', '').strip(),
                'status': 'Draft',
                'created_at': datetime.utcnow().isoformat(),
            }
            app.extensions['store'].add_request(data)
            flash('Application saved successfully.', 'success')
            return redirect(url_for('new_application'))
        return render_template('new_application.html')

    @app.route('/pending-approvals')
    def pending_approvals():
        requests = app.extensions['store'].list_requests()
        return render_template('pending_approvals.html', requests=requests)

    @app.route('/new-bg-request', methods=['GET', 'POST'])
    def new_bg_request():
        if request.method == 'POST':
            data = {
                'id': str(uuid.uuid4()),
                'guarantee_type': request.form.get('guarantee_type', 'Bid Bond'),
                'beneficiary': request.form.get('beneficiary', '').strip(),
                'amount': request.form.get('amount', '0'),
                'validity_date': request.form.get('validity_date', ''),
                'terms': request.form.get('terms', '').strip(),
                'status': 'Pending',
                'created_at': datetime.utcnow().isoformat(),
            }
            app.extensions['store'].add_request(data)
            flash('BG request submitted successfully.', 'success')
            return redirect(url_for('pending_approvals'))
        return render_template('new_bg_request.html')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            confirm = request.form.get('confirm_password', '').strip()
            if password != confirm:
                flash('Passwords do not match.', 'error')
                return redirect(url_for('signup'))
            profile = {
                'id': str(uuid.uuid4()),
                'name': request.form.get('full_name', '').strip(),
                'email': email,
                'employee_id': request.form.get('employee_id', '').strip(),
                'role': request.form.get('role', 'Approver'),
                'password': password,
            }
            app.extensions['store'].add_profile(profile)
            flash('Account created successfully.', 'success')
            return redirect(url_for('login'))
        return render_template('signup.html')

    @app.route('/request/<request_id>/approve', methods=['POST'])
    def approve_request(request_id):
        req = app.extensions['store'].get_request(request_id)
        if req:
            req['status'] = 'Approved'
            app.extensions['store'].add_request(req)
            app.extensions['store'].add_activity({
                'id': str(uuid.uuid4()),
                'request_id': request_id,
                'action': 'Approved',
                'created_at': datetime.utcnow().isoformat(),
            })
            flash('Request approved.', 'success')
        return redirect(url_for('pending_approvals'))

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
=======
from flask import Flask, redirect, url_for

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    from extensions import init_supabase
    init_supabase(app)

    # Register Blueprints
    from routes.auth_routes import bp as auth_bp
    from routes.dashboard_routes import bp as dashboard_bp
    from routes.request_routes import bp as request_bp
    from routes.report_routes import bp as report_bp
    from routes.approval_routes import bp as approval_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(request_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(approval_bp)

    @app.route('/')
    def index():
        return redirect(url_for('dashboard.home'))

    @app.before_request
    def mock_login():
        from flask import session
        session['user_id'] = '00000000-0000-0000-0000-000000000000'
        session['user_name'] = 'Test Admin'
        session['role'] = 'admin'

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
>>>>>>> 91082328bb3fa4e447dced4b9fa38b017ad0faef
