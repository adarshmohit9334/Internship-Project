from app import create_app

app = create_app()
client = app.test_client()

client.post(
    '/new-application',
    data={
        'applicant_name': 'Demo User',
        'customer_id': 'CUST-999',
        'product_category': 'Performance Bond',
        'requested_amount': '5555',
        'description': 'For approval test'
    },
    follow_redirects=True
)

store = app.extensions['store']
request = next(
    (item for item in store.list_requests() if item.get('customer_id') == 'CUST-999'),
    None
)

if request is None:
    raise RuntimeError('No request was created')

resp = client.post(f"/request/{request['id']}/approve", follow_redirects=True)
updated = client.get('/pending-approvals')

print('request_id:', request['id'])
print('approve_status:', resp.status_code)
print('pending_page_has_approved:', 'Approved' in updated.text)
print('request_status_after_approval:', store.get_request(request['id'])['status'])
