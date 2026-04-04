from flask import render_template, session
from utils import admin_required, superadmin_required, login_required

@admin_required
def dashboardIndex():
    active_menu = ['dashboard', 'analytics']
    return render_template('views/dashboard/index.html', menu = active_menu)