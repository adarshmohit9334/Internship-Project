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

    def is_supabase_active(self):
        return self.app.extensions.get('supabase_enabled') and self.app.extensions.get('supabase') is not None

    def add_profile(self, profile):
        self.data['profiles'][profile['id']] = profile
        self._save()
        if self.is_supabase_active():
            client = self.app.extensions.get('supabase_service') or self.app.extensions.get('supabase')
            try:
                db_profile = {k: v for k, v in profile.items() if k != 'password'}
                client.table('profiles').upsert(db_profile).execute()
            except Exception as e:
                print(f"Supabase upsert profile failed: {e}")
        return profile

    def get_profile(self, profile_id):
        profile = self.data['profiles'].get(profile_id)
        if self.is_supabase_active():
            client = self.app.extensions.get('supabase_service') or self.app.extensions.get('supabase')
            try:
                res = client.table('profiles').select('*').eq('id', profile_id).execute()
                if res.data:
                    db_profile = res.data[0]
                    # Retain local password if present
                    if profile and 'password' in profile:
                        db_profile['password'] = profile['password']
                    return db_profile
            except Exception as e:
                print(f"Supabase get profile failed: {e}")
        return profile

    def list_profiles(self):
        db_profiles = []
        if self.is_supabase_active():
            client = self.app.extensions.get('supabase_service') or self.app.extensions.get('supabase')
            try:
                res = client.table('profiles').select('*').execute()
                if res.data:
                    db_profiles = res.data
            except Exception as e:
                print(f"Supabase list profiles failed: {e}")
        
        # Merge local and remote
        profiles_dict = {p['id']: p for p in self.data['profiles'].values()}
        for p in db_profiles:
            profiles_dict[p['id']] = p
        return list(profiles_dict.values())

    def add_support_ticket(self, ticket):
        self.data.setdefault('support_tickets', []).append(ticket)
        self._save()
        return ticket

    def list_support_tickets(self):
        return self.data.setdefault('support_tickets', [])

    def add_request(self, request):
        self.data['bg_requests'][request['id']] = request
        self._save()
        if self.is_supabase_active():
            client = self.app.extensions.get('supabase_service') or self.app.extensions.get('supabase')
            try:
                client.table('bg_requests').upsert(request).execute()
            except Exception as e:
                print(f"Supabase upsert request failed: {e}")
        return request

    def get_request(self, request_id):
        req = self.data['bg_requests'].get(request_id)
        if self.is_supabase_active():
            client = self.app.extensions.get('supabase_service') or self.app.extensions.get('supabase')
            try:
                res = client.table('bg_requests').select('*').eq('id', request_id).execute()
                if res.data:
                    return res.data[0]
            except Exception as e:
                print(f"Supabase get request failed: {e}")
        return req

    def list_requests(self):
        db_requests = []
        if self.is_supabase_active():
            client = self.app.extensions.get('supabase_service') or self.app.extensions.get('supabase')
            try:
                res = client.table('bg_requests').select('*').execute()
                if res.data:
                    db_requests = res.data
            except Exception as e:
                print(f"Supabase list requests failed: {e}")
        
        # Merge local and remote
        requests_dict = {r['id']: r for r in self.data['bg_requests'].values()}
        for r in db_requests:
            requests_dict[r['id']] = r
        return list(requests_dict.values())

    def add_attachment(self, attachment):
        self.data['attachments'][attachment['id']] = attachment
        self._save()
        if self.is_supabase_active():
            client = self.app.extensions.get('supabase_service') or self.app.extensions.get('supabase')
            try:
                client.table('attachments').insert(attachment).execute()
            except Exception as e:
                print(f"Supabase insert attachment failed: {e}")
        return attachment

    def get_attachments(self, request_id):
        db_attachments = []
        if self.is_supabase_active():
            client = self.app.extensions.get('supabase_service') or self.app.extensions.get('supabase')
            try:
                res = client.table('attachments').select('*').eq('bg_request_id', request_id).execute()
                if res.data:
                    db_attachments = res.data
            except Exception as e:
                print(f"Supabase list attachments failed: {e}")
        
        # Merge local and remote
        attachments_dict = {a['id']: a for a in self.data['attachments'].values() if a.get('bg_request_id') == request_id}
        for a in db_attachments:
            attachments_dict[a['id']] = a
        return list(attachments_dict.values())

    def add_activity(self, item):
        self.data['activity'].append(item)
        self._save()
        if self.is_supabase_active():
            client = self.app.extensions.get('supabase_service') or self.app.extensions.get('supabase')
            try:
                db_log = {
                    'id': item.get('id'),
                    'bg_request_id': item.get('bg_request_id') or item.get('request_id'),
                    'action_by': item.get('action_by') or item.get('decided_by'),
                    'action': item.get('action'),
                    'old_status': item.get('old_status'),
                    'new_status': item.get('new_status'),
                    'note': item.get('note'),
                    'created_at': item.get('created_at'),
                }
                client.table('activity_log').insert(db_log).execute()
            except Exception as e:
                print(f"Supabase insert activity failed: {e}")

    def get_activity(self, limit=10):
        db_activity = []
        if self.is_supabase_active():
            client = self.app.extensions.get('supabase_service') or self.app.extensions.get('supabase')
            try:
                res = client.table('activity_log').select('*').order('created_at', desc=True).limit(limit).execute()
                if res.data:
                    db_activity = res.data
            except Exception as e:
                print(f"Supabase get activity failed: {e}")
        
        # Merge local and remote activity
        all_activity = list(self.data['activity'])
        for act in db_activity:
            # normalize keys from DB to match local structure
            act_normalized = {
                'id': act.get('id'),
                'bg_request_id': act.get('bg_request_id'),
                'action_by': act.get('action_by'),
                'action': act.get('action'),
                'old_status': act.get('old_status'),
                'new_status': act.get('new_status'),
                'note': act.get('note'),
                'created_at': act.get('created_at'),
            }
            if act_normalized not in all_activity:
                all_activity.append(act_normalized)
        return all_activity[-limit:]

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
