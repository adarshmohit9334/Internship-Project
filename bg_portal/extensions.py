import json
from pathlib import Path
from supabase import create_client
from flask import current_app

class DemoStore:
    def __init__(self, app):
        self.app = app
        self.base_dir = Path(app.root_path)
        self.data_file = self.base_dir / 'demo_store.json'
        self.data = self._load()

    def _load(self):
        if self.data_file.exists():
            try:
                return json.loads(self.data_file.read_text())
            except Exception:
                return self._default_data()
        return self._default_data()

    def _default_data(self):
        return {
            'profiles': {},
            'bg_requests': {},
            'attachments': {},
            'activity': [],
            'settings': {
                'md_threshold': 1500000,
                'notify_email': True,
                'notify_dashboard': True,
            }
        }

    def _save(self):
        self.data_file.write_text(json.dumps(self.data, indent=2, default=str))

    def add_profile(self, profile):
        self.data['profiles'][profile['id']] = profile
        self._save()
        return profile

    def get_profile(self, profile_id):
        return self.data['profiles'].get(profile_id)

    def list_profiles(self):
        return list(self.data['profiles'].values())

    def add_request(self, request):
        self.data['bg_requests'][request['id']] = request
        self._save()
        return request

    def get_request(self, request_id):
        return self.data['bg_requests'].get(request_id)

    def list_requests(self):
        return list(self.data['bg_requests'].values())

    def add_attachment(self, attachment):
        self.data['attachments'][attachment['id']] = attachment
        self._save()
        return attachment

    def add_activity(self, item):
        self.data['activity'].append(item)
        self._save()

    def get_activity(self, limit=10):
        return self.data['activity'][-limit:]

    def update_settings(self, settings):
        self.data['settings'].update(settings)
        self._save()

    def get_settings(self):
        return self.data['settings']

def init_extensions(app):
    app.extensions['demo_store'] = DemoStore(app)
    URL = app.config.get('SUPABASE_URL')
    KEY = app.config.get('SUPABASE_KEY')
    SERVICE_KEY = app.config.get('SUPABASE_SERVICE_KEY')

    if URL and URL != 'your_supabase_project_url':
        try:
            app.extensions['supabase'] = create_client(URL, KEY or SERVICE_KEY)
            app.extensions['supabase_enabled'] = bool(KEY or SERVICE_KEY)
        except Exception:
            app.extensions['supabase'] = None
            app.extensions['supabase_enabled'] = False
    else:
        app.extensions['supabase'] = None
        app.extensions['supabase_enabled'] = False

    if SERVICE_KEY:
        try:
            app.extensions['supabase_service'] = create_client(URL, SERVICE_KEY)
        except Exception:
            app.extensions['supabase_service'] = None
    else:
        app.extensions['supabase_service'] = None

def get_supabase_client():
    return current_app.extensions.get('supabase')

def get_supabase_service_client():
    return current_app.extensions.get('supabase_service')
