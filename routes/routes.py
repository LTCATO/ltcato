from controller.HomeController import home, explore_map, destination_details, municipalities, municipality_details, tourist_spots, lara_ai
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

    @app.route('/explore-map')
    def explore_map_page():
        return explore_map()
    
    @app.route('/destination/<spot_id>')
    def destination_details_page(spot_id):
        return destination_details(spot_id)

    @app.route('/municipalities')
    def municipalities_page():
        return municipalities()

    @app.route('/municipalities/<municipality_id>')
    def municipality_details_page(municipality_id):
        return municipality_details(municipality_id)
    
    @app.route('/tourist-spots')
    def tourist_spots_page():
        return tourist_spots()

    @app.route('/lara-ai')
    def lara_ai_page():
        return lara_ai()