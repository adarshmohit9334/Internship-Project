from app import create_app

app = create_app()
client = app.test_client()
store = app.extensions['demo_store']

# Create test requester
requester = {
    'id': 'user-requester-1',
    'personnel_no': 'EMP1001',
    'name': 'Requester One',
    'email': 'requester@example.com',
    'department': 'Operations',
    'designation': 'Engineer',
    'mobile_no': '9999999999',
    'role': 'requester',
    'manager_id': None,
    'is_active': True,
    'password': 'password123'
}
store.add_profile(requester)

# Create test admin
admin = {
    'id': 'user-admin-1',
    'personnel_no': 'ADM1001',
    'name': 'Admin User',
    'email': 'admin@example.com',
    'department': 'Finance',
    'designation': 'Admin',
    'mobile_no': '8888888888',
    'role': 'admin',
    'manager_id': None,
    'is_active': True,
    'password': 'admin123'
}
store.add_profile(admin)

# Requester login
resp = client.post('/login', data={'personnel_no': 'EMP1001', 'password': 'password123'}, follow_redirects=True)
print('requester_login_status:', resp.status_code)
print('requester_login_path:', resp.request.path)

# Requester dashboard pages
for path in ['/dashboard', '/request/new', '/my-requests']:
    r = client.get(path)
    print(f'{path} => {r.status_code}')

# Save a draft request
resp = client.post('/request/save-draft', data={
    'department': 'Operations',
    'location': 'Delhi',
    'date_of_request': '2026-06-22',
    'work_order_no': 'WO-1001',
    'type_of_work': 'Civil Works',
    'job_value': '250000',
    'alternate_owner_id': '',
    'party_name': 'Acme Ltd',
    'nature_of_bg': 'Performance Bond',
    'bg_amount': '500000',
    'bg_expiry_date': '2027-06-22',
    'bg_claim_period': '90 days',
    'remarks': 'Draft verification'
}, follow_redirects=True)
print('save_draft_status:', resp.status_code)
print('save_draft_path:', resp.request.path)

# Admin login
client.get('/logout')
resp = client.post('/login', data={'personnel_no': 'ADM1001', 'password': 'admin123'}, follow_redirects=True)
print('admin_login_status:', resp.status_code)
print('admin_login_path:', resp.request.path)

# Admin pages
for path in ['/admin/dashboard', '/admin/requests', '/admin/pending', '/admin/reports', '/admin/settings']:
    r = client.get(path)
    print(f'{path} => {r.status_code}')

# Approve a request if exists
requests = store.list_requests()
req = next((r for r in requests if r.get('party_name') == 'Acme Ltd'), None)
if req:
    resp = client.post(f"/admin/request/{req['id']}/update-status", data={
        'new_status': 'Approved',
        'admin_remarks': 'Approved by test'
    }, follow_redirects=True)
    print('update_status_status:', resp.status_code)
    print('update_status_path:', resp.request.path)
    print('request_status_after_update:', store.get_request(req['id'])['status'])
else:
    print('No request found for approval test')
