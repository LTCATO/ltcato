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

            flash("login credentials", "success")
            print("tama")

            return redirect(url_for("dashboard_page"))
        else:
            print("mali")
            flash("Invalid login credentials", "danger")

    except Exception as e:
        flash(f"Error: {str(e)}", "danger")

    return render_template('views/login.html')

def register():
    return render_template('views/register.html')