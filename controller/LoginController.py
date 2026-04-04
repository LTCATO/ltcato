from flask import render_template, request, redirect, url_for, flash, session
from supabase_client import supabase


def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            res = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if res.user:
                # Save session
                session["user"] = res.user.id
                session["email"] = res.user.email

                flash("Login successful!", "success")

                return redirect(url_for("dashboard_page"))
            else:
                flash("Invalid login credentials", "error")

        except Exception as e:
            flash(f"Error: {str(e)}", "error")

    return render_template('views/login.html')

def register():
    return render_template('views/register.html')