from functools import wraps
from flask import session, redirect, url_for, flash, current_app

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                flash("Please log in to access this page.", "error")
                return redirect(url_for('login_page'))
            
            user_role = session.get('role_name')
            
            if not user_role or user_role not in allowed_roles:
                flash("You do not have permission to access this page.", "error")
                return redirect(url_for('dashboard_page'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def mask_name(name):
    """Masks a name for anonymous feedback (e.g. Dennrick -> De****k)"""
    if not name or name.strip() == "":
        return "Anonymous"
        
    words = name.split()
    masked_words = []
    
    for word in words:
        if len(word) <= 2:
            masked_words.append(word)
        else:
            start = word[:2]
            end = word[-1]
            asterisks = '*' * (len(word) - 3)
            masked_words.append(f"{start}{asterisks}{end}")
            
    return " ".join(masked_words)