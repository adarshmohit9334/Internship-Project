import uuid
from datetime import datetime

# In-memory storage to bypass Supabase for now
# Users structure:
# {
#   user_id (str): {
#       "id": str,
#       "personnel_no": str,
#       "email": str,
#       "password": str,
#       "name": str,
#       "department": str,
#       "designation": str,
#       "mobile_no": str,
#       "role": str ('requester' | 'admin')
#   }
# }
users = {
    "admin-uuid-1234": {
        "id": "admin-uuid-1234",
        "personnel_no": "A001",
        "email": "admin@example.com",
        "password": "password",
        "name": "Admin User",
        "department": "Finance",
        "designation": "Manager",
        "mobile_no": "1234567890",
        "role": "admin"
    }
}

# Requests structure:
# {
#   request_id (str): {
#       ...bg_request fields...
#   }
# }
requests = {}

def get_user_by_personnel_no(personnel_no):
    for u in users.values():
        if u['personnel_no'] == personnel_no:
            return u
    return None

def get_user_by_id(user_id):
    return users.get(user_id)

def create_user(data):
    user_id = str(uuid.uuid4())
    data['id'] = user_id
    data['role'] = 'requester'  # default
    users[user_id] = data
    return data

def get_requests_for_user(user_id):
    return [req for req in requests.values() if req['requester_id'] == user_id]

def get_all_requests():
    return list(requests.values())

def get_pending_requests():
    return [req for req in requests.values() if req['status'] == 'Pending']

def create_request(data):
    req_id = str(uuid.uuid4())
    data['id'] = req_id
    data['created_at'] = datetime.now().isoformat()
    requests[req_id] = data
    return data

def get_request(req_id):
    return requests.get(req_id)

def update_request(req_id, data):
    if req_id in requests:
        requests[req_id].update(data)
        return requests[req_id]
    return None
