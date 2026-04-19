from controller.HomeController import home, explore_map, destination_details, municipalities, municipality_details, tourist_spots, lara_ai, test_uploader
from controller.LoginController import login, register, logout
from controller.DashboardController import dashboardIndex, accounts, create_account, update_account, delete_account, lgu_dashboard, tourist_spots as lgu_tourist_spots
from controller.ArrivalsController import arrivals
from controller.DecisionController import decision

def register_routes(app):
# CLIENT-FACING ROUTES
    @app.route("/")
    def home_page():
        return home()

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

    @app.route('/test-uploader', methods=["GET", "POST"])
    def test_uploader_page():
        return test_uploader()

# SUPERADMIN DASHBOARD ROUTES
    
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
    
    @app.route('/dashboard/lgu')
    def lgu_page():
        return lgu_dashboard()
    
    @app.route('/dashboard/lgu/spots')
    def lgu_spots_page():
        return lgu_tourist_spots()
    
    @app.route('/dashboard/lgu/arrivals-data')
    def lgu_arrivals_data_page():
        from flask import render_template
        return render_template('views/dashboard/lgu/arrivals_data.html')
    
    @app.route('/dashboard/lgu/feedbacks')
    def lgu_feedbacks_page():
        from flask import render_template
        return render_template('views/dashboard/lgu/feedbacks.html')

# AUTH ROUTES
    @app.route("/login", methods=["GET", "POST"])
    def login_page():
        return login()

    @app.route("/register")
    def register_page():
        return register()
    
    @app.route('/accounts/create', methods=['POST'])
    def create_account_page():
        return create_account()

    @app.route('/accounts/update/<string:user_id>', methods=['PUT'])
    def update_account_page(user_id):
        return update_account(user_id)

    @app.route('/accounts/delete/<string:user_id>', methods=['DELETE'])
    def delete_account_page(user_id):
        return delete_account(user_id)

    @app.route('/logout')
    def logout_page():
        return logout()
