from flask import render_template, request, redirect, url_for, flash, session
from supabase_client import supabase

def login():
    if 'admin-ltcato' not in request.host:
        flash("Please log in with your administrator account to access the admin portal.", "info")
        return redirect(url_for("home_page"))  # Redirect to the public landing page instead of showing the login form
    
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
                    if role_name not in ['super_admin', 'municipality_admin']:
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
                    elif role_name == 'municipality_admin':
                        return redirect(url_for("login_page"))    
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

def register():
    """
    Public registration is completely disabled for this SaaS platform.
    New Municipality Admins can ONLY be created by the Super Admin 
    from the internal dashboard.
    """
    flash("Public registration is disabled. If you are an admin, please contact the Super Admin for your credentials.", "error")
    return redirect(url_for('login_page'))

def logout():
    """Handles user logout"""
    session.clear()
    try:
        supabase.auth.sign_out()
    except:
        pass
    flash("You have been successfully logged out.", "success")
    return redirect(url_for('login_page'))