from controller.HomeController import home
from controller.LoginController import login, register
from controller.DashboardController import dashboardIndex

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
    
    @app.route('/dashboard')
    def dashboard_page():
        return dashboardIndex()

