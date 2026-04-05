from flask import render_template, session
from utils import role_required, login_required


@login_required
@role_required('super_admin', 'municipality_admin')
def dashboardIndex():
    active_menu = ['dashboard', 'analytics']
    return render_template('views/dashboard/index.html', menu=active_menu)


@login_required
@role_required('super_admin')
def accounts():
    active_menu = ['accounts']
    return render_template('views/dashboard/accounts.html', menu=active_menu)