from flask import render_template, session
from utils import municipality_admin_required, superadmin_required, login_required

@superadmin_required
def dashboardIndex():
    active_menu = ['dashboard', 'analytics']
    return render_template('views/dashboard/index.html', menu = active_menu)