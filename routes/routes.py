from controller.HomeController import home
from controller.LoginController import login, register, logout
from controller.DashboardController import dashboardIndex, accounts
from controller.ArrivalsController import arrivals
from controller.DecisionController import decision

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
    
    @app.route('/dashboard/accounts')
    def accounts_page():
        return accounts()
    
    @app.route('/dashboard/arrivals')
    def arrivals_page():
        return arrivals()
    
    @app.route('/dashboard/decision')
    def decision_page():
        return decision()

    @app.route('/logout')
    def logout_page():
        return logout()