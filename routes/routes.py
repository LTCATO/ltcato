from controller.HomeController import home
from controller.LoginController import login, register
from controller.DashboardController import dashboardIndex
from utils import admin_required, superadmin_required, login_required

def register_routes(app):
    @app.route("/")
    def home_page():
        return home()

    @app.route("/login", methods=["GET", "POST"])
    def login_page():
        return login()

    @app.route("/register")
    def register_page():
        return register()
    
    @admin_required
    @app.route('/dashboard')
    def dashboard_page():
        return dashboardIndex()