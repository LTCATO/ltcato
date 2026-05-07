from flask import render_template, request, redirect, url_for, flash, session
from supabase_client import supabase, service_supabase

def login():
    # Check if this is admin portal or client portal
    is_admin_portal = 'admin-ltcato' in request.host
    
    if is_admin_portal:
        return admin_login()
    else:
        return client_login()

def admin_login():
    # If already logged in, redirect to dashboard
    if 'user' in session and session.get('role_name') == 'super_admin':
        return redirect(url_for("dashboard_page"))

    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        
        try:
            res = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if res.user:
                # Fetch user profile to get role and municipality
                profile_res = supabase.table('profiles').select('*, roles(role_name)').eq('id', res.user.id).execute()
                
                if profile_res.data:
                    profile = profile_res.data[0]
                    role_name = profile.get('roles', {}).get('role_name', 'guest') if profile.get('roles') else 'guest'
                    
                    # SECURITY CHECK: Only allow admins to login to this portal
                    if role_name not in ['super_admin', 'lgu_admin']:
                        # Sign them out of Supabase as well
                        supabase.auth.sign_out()
                        flash("Access denied. This portal is restricted to authorized administrators.", "error")
                        return redirect(url_for("login_page"))
                    
                    # Save base session variables for admins
                    session["user"] = res.user.id
                    session["email"] = res.user.email
                    session["role_name"] = role_name
                    session["municipality_id"] = profile.get('municipality_id')
                    session["first_name"] = profile.get('first_name')
                    session["last_name"] = profile.get('last_name')

                    flash(f"Welcome back, {session.get('first_name', 'Admin')}!", "success")
                    if role_name == 'super_admin':
                        return redirect(url_for("dashboard_page"))
                    elif role_name == 'lgu_admin':
                        return redirect(url_for("lgu_page"))    
                else:
                    # No profile associated with this account
                    supabase.auth.sign_out()
                    flash("Access denied. Admin profile not found.", "error")
                    return redirect(url_for("login_page"))
            else:
                flash("Invalid login credentials.", "error")
                return redirect(url_for("login_page"))

        except Exception as e:
            # Handle Supabase Auth errors gracefully (e.g., Invalid login credentials)
            error_msg = str(e)
            if "Invalid login credentials" in error_msg:
                flash("Invalid email or password.", "error")
            else:
                flash("An error occurred during login. Please try again.", "error")
            
            return redirect(url_for("login_page"))

    return render_template('views/login.html')

def client_login():
    # If already logged in, redirect to home
    if 'user' in session:
        return redirect(url_for("home_page"))

    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        
        try:
            res = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if res.user:
                # Fetch user profile to get role and municipality
                profile_res = supabase.table('profiles').select('*, roles(role_name), municipalities(name)').eq('id', res.user.id).execute()
                
                if profile_res.data:
                    profile = profile_res.data[0]
                    role_name = profile.get('roles', {}).get('role_name', 'guest') if profile.get('roles') else 'guest'
                    
                    # Only allow clients to login to this portal
                    if role_name not in ['tourist']:  # role_id 3 corresponds to 'tourist'
                        # Sign them out of Supabase as well
                        supabase.auth.sign_out()
                        flash("Access denied. Please use the admin portal for administrator accounts.", "error")
                        return redirect(url_for("login_signup_page"))
                    
                    # Save session variables for clients
                    session["user"] = res.user.id
                    session["email"] = res.user.email
                    session["role_name"] = role_name
                    session["municipality_id"] = profile.get('municipality_id')
                    session["municipality_name"] = profile.get('municipalities', {}).get('name') if profile.get('municipalities') else None
                    session["first_name"] = profile.get('first_name')
                    session["last_name"] = profile.get('last_name')

                    flash(f"Welcome back, {session.get('first_name', 'User')}!", "success")
                    return redirect(url_for("home_page"))
                else:
                    # No profile associated with this account
                    supabase.auth.sign_out()
                    flash("Account not found. Please complete your registration.", "error")
                    return redirect(url_for("login_signup_page"))
            else:
                flash("Invalid email or password.", "error")
                return redirect(url_for("login_signup_page"))

        except Exception as e:
            # Handle Supabase Auth errors gracefully
            error_msg = str(e)
            if "Invalid login credentials" in error_msg:
                flash("Invalid email or password.", "error")
            else:
                flash("An error occurred during login. Please try again.", "error")
            
            return redirect(url_for("login_signup_page"))

    return render_template('views/client/login_signup.html')

def register():
    """
    Handle client registration with role_id 3 (tourist/client role).
    """
    if request.method == 'GET':
        return render_template('views/client/login_signup.html')
    
    if request.method == 'POST':
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        municipality_id = request.form.get("municipality_id")
        
        # Validation
        if not all([first_name, last_name, email, password, confirm_password]):
            flash("All fields are required.", "error")
            return render_template('views/client/login_signup.html')
        
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template('views/client/login_signup.html')
        
        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template('views/client/login_signup.html')
        
        try:
            # Create user in Supabase Auth using service client (auto-confirmed)
            auth_response = service_supabase.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,  # Auto-confirm email
                "user_metadata": {
                    "first_name": first_name,
                    "last_name": last_name
                }
            })
            
            if auth_response.user:
                # Create profile record with role_id 3 (client/tourist)
                profile_data = {
                    "id": auth_response.user.id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "role_id": 3,  # Client/Tourist role
                    "municipality_id": None
                }
                
                profile_response = service_supabase.table('profiles').insert(profile_data).execute()
                
                if profile_response.data:
                    flash("Account created successfully! You can now login.", "success")
                    return redirect(url_for('login_signup_page'))
                else:
                    # If profile creation fails, try to clean up the auth user
                    try:
                        service_supabase.auth.admin.delete_user(auth_response.user.id)
                    except:
                        pass
                    flash("Error creating profile. Please try again.", "error")
            else:
                flash("Error creating account. Please try again.", "error")
                
        except Exception as e:
            error_msg = str(e)
            if "User already registered" in error_msg or "already been registered" in error_msg:
                flash("An account with this email already exists.", "error")
            else:
                flash(f"Registration error: {error_msg}", "error")
        
        return render_template('views/client/login_signup.html')

def logout():
    """Handles user logout"""
    session.clear()
    try:
        supabase.auth.sign_out()
    except:
        pass
    flash("You have been successfully logged out.", "success")
    return redirect(url_for('home_page'))