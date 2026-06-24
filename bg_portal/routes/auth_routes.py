from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from utils.auth_decorators import login_required
import uuid

auth_bp = Blueprint('auth', __name__)


def _build_session_user(profile):
    return {
        'id': profile.get('id') or profile.get('user_id'),
        'role': profile.get('role', 'requester'),
        'name': profile.get('name') or profile.get('full_name'),
        'personnel_no': profile.get('personnel_no')
    }


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    store = current_app.extensions['demo_store']
    profile_id = session['user']['id']
    profile_data = store.get_profile(profile_id)
    if not profile_data:
        profile_data = {
            'id': profile_id,
            'name': session['user'].get('name', ''),
            'role': session['user'].get('role', 'requester'),
            'personnel_no': session['user'].get('personnel_no', ''),
            'email': '',
            'mobile_no': '',
            'department': '',
            'designation': ''
        }
    
    if request.method == 'POST':
        profile_data['name'] = request.form.get('name', '').strip()
        profile_data['email'] = request.form.get('email', '').strip()
        profile_data['mobile_no'] = request.form.get('mobile_no', '').strip()
        profile_data['department'] = request.form.get('department', '').strip()
        profile_data['designation'] = request.form.get('designation', '').strip()
        
        # Save profile
        store.add_profile(profile_data)
        
        # Update session
        session['user']['name'] = profile_data['name']
        session['user']['personnel_no'] = profile_data.get('personnel_no')
        session.modified = True
        
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('auth.profile'))
        
    return render_template('auth/profile.html', profile=profile_data)


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    store = current_app.extensions['demo_store']
    profile_id = session['user']['id']
    profile_data = store.get_profile(profile_id)
    
    if request.method == 'POST':
        old_password = request.form.get('old_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if not profile_data:
            flash('Profile data not found.', 'error')
            return redirect(url_for('auth.change_password'))
            
        if profile_data.get('password') and profile_data.get('password') != old_password:
            flash('Current password does not match.', 'error')
            return redirect(url_for('auth.change_password'))
            
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return redirect(url_for('auth.change_password'))
            
        if not new_password:
            flash('New password cannot be empty.', 'error')
            return redirect(url_for('auth.change_password'))
            
        # Update the password
        profile_data['password'] = new_password
        store.add_profile(profile_data)
        
        # If Supabase is active, update the user password there
        client = current_app.extensions.get('supabase')
        if client:
            try:
                client.auth.update_user({'password': new_password})
            except Exception as e:
                print(f"Supabase password update failed: {e}")
                
        flash('Password updated successfully.', 'success')
        return redirect(url_for('auth.profile'))
        
    return render_template('auth/change_password.html')



@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        personnel_no = request.form.get('personnel_no', '').strip()
        password = request.form.get('password', '').strip()
        store = current_app.extensions['demo_store']
        profile = None

        # Try real Supabase auth first when the form value looks like an email.
        client = current_app.extensions.get('supabase')
        if client and '@' in personnel_no:
            try:
                auth_response = client.auth.sign_in_with_password({
                    'email': personnel_no,
                    'password': password,
                })
                user = getattr(auth_response, 'user', None)
                if user:
                    profile = {
                        'id': user.id,
                        'role': 'requester',
                        'name': user.user_metadata.get('name') if getattr(user, 'user_metadata', None) else None,
                        'personnel_no': user.user_metadata.get('personnel_no') if getattr(user, 'user_metadata', None) else None,
                    }
            except Exception as exc:
                flash(f'Login failed: {exc}', 'error')
                return redirect(url_for('auth.login'))

        if profile is None:
            for p in store.list_profiles():
                if p.get('personnel_no') == personnel_no or p.get('email') == personnel_no:
                    profile = p
                    break

        if not profile:
            flash('Personnel number or email not found', 'error')
            return redirect(url_for('auth.login'))

        if profile.get('password') and profile.get('password') != password:
            flash('Invalid password', 'error')
            return redirect(url_for('auth.login'))

        session['user'] = _build_session_user(profile)
        return redirect(url_for('dashboard.homepage'))
    return render_template('auth/login.html')

@auth_bp.route('/signup/step1', methods=['GET', 'POST'])
def signup_step1():
    if request.method == 'POST':
        data = {
            'department': request.form.get('department', '').strip(),
            'location': request.form.get('location', '').strip(),
            'name': request.form.get('name', '').strip(),
            'personnel_no': request.form.get('personnel_no', '').strip(),
            'designation': request.form.get('designation', '').strip(),
            'mobile_no': request.form.get('mobile_no', '').strip(),
        }
        if not all(data.values()):
            flash('All fields are required.', 'error')
            return redirect(url_for('auth.signup_step1'))
        session['signup_step1'] = data
        return redirect(url_for('auth.signup_step2'))
    return render_template('auth/signup_step1.html')

@auth_bp.route('/signup/step2', methods=['GET', 'POST'])
def signup_step2():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm = request.form.get('confirm_password', '').strip()
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('auth.signup_step2'))
        step1 = session.get('signup_step1')
        if not step1:
            flash('Please complete step 1 first.', 'error')
            return redirect(url_for('auth.signup_step1'))

        client = current_app.extensions.get('supabase')
        user_id = None
        if client:
            try:
                auth_response = client.auth.sign_up({
                    'email': email,
                    'password': password,
                    'options': {
                        'data': {
                            'name': step1['name'],
                            'personnel_no': step1['personnel_no'],
                            'department': step1['department'],
                            'designation': step1['designation'],
                            'mobile_no': step1['mobile_no'],
                        }
                    }
                })
                user = getattr(auth_response, 'user', None)
                if user:
                    user_id = user.id
            except Exception as exc:
                flash(f'Sign-up failed: {exc}', 'error')
                return redirect(url_for('auth.signup_step2'))

        if user_id is None:
            user_id = str(uuid.uuid4())

        profile = {
            'id': user_id,
            'personnel_no': step1['personnel_no'],
            'name': step1['name'],
            'email': email,
            'department': step1['department'],
            'designation': step1['designation'],
            'mobile_no': step1['mobile_no'],
            'role': 'requester',
            'manager_id': None,
            'is_active': True,
            'password': password,
        }
        current_app.extensions['demo_store'].add_profile(profile)
        session.pop('signup_step1', None)
        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/signup_step2.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
