from controller.HomeController import home, explore_map, login_signup, destination_details, municipalities, municipality_details, tourist_spots, lara_ai, test_uploader, platform_features, security, lgu_support
from controller.LoginController import admin_login,client_login, register, logout, client_create_account
from controller.DashboardController import dashboardIndex, accounts, create_account, update_account, delete_account, lgu_dashboard, tourist_spots as lgu_tourist_spots, lgu_add_spot, lgu_get_spot_data, lgu_edit_spot, lgu_delete_spot
from controller.ArrivalsController import ArrivalsController
from controller.DecisionController import decision
from controller.ItineraryController import itinerary_page, optimize_itinerary, get_spots_map_data
from utils import login_required

def register_routes(app):
# CLIENT-FACING ROUTES
    @app.route("/")
    def home_page():
        return home()

    @app.route('/explore-map')
    def explore_map_page():
        return explore_map()

    @app.route('/login-signup', methods=['GET', 'POST'])
    def login_signup_page():
        return client_login()
    
    @app.route('/destination/<spot_id>')
    def destination_details_page(spot_id):
        return destination_details(spot_id)

    @app.route('/lgu')
    def lgu_listing_page():
        return municipalities()

    @app.route('/lgu/<municipality_id>')
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

    @app.route('/platform-features')
    def platform_features_page():
        return platform_features()

    @app.route('/security')
    def security_page():
        return security()

    @app.route('/lgu-support')
    def lgu_support_page():
        return lgu_support()

    @app.route('/itinerary')
    def itinerary_page_route():
        return itinerary_page()

    @app.route('/api/itinerary/optimize', methods=['POST'])
    def itinerary_optimize_api():
        return optimize_itinerary()

    @app.route('/api/spots/map-data')
    def spots_map_data_api():
        return get_spots_map_data()

    @app.route('/api/explore-map/data')
    def explore_map_data_api():
        """API endpoint to fetch tourist spots and municipalities for the explore map"""
        from flask import jsonify
        from supabase_client import supabase
        
        try:
            # Fetch all municipalities
            municipalities_response = supabase.table('municipalities').select('*').execute()
            municipalities = municipalities_response.data
            
            # Fetch all approved tourist spots with municipality data
            spots_response = supabase.table('tourist_spots').select('*, municipalities(name)').eq('status', 'approved').execute()
            spots = spots_response.data
            
            # Helper function to safely convert to float with fallback
            def safe_float(value, default):
                try:
                    if value is None:
                        return default
                    return float(value)
                except (ValueError, TypeError):
                    return default
            
            # Group spots by municipality
            municipalities_with_spots = []
            for municipality in municipalities:
                municipality_spots = [spot for spot in spots if spot.get('municipality_id') == municipality.get('id')]
                
                # Get municipality coordinates with fallback
                mun_lat = safe_float(municipality.get('latitude'), 14.2)
                mun_lng = safe_float(municipality.get('longitude'), 121.3)
                
                municipalities_with_spots.append({
                    'id': f"m{municipality['id']}",
                    'name': municipality['name'],
                    'type': 'municipality',
                    'lat': mun_lat,
                    'lng': mun_lng,
                    'spots': [
                        {
                            'id': f"s{spot['id']}",
                            'name': spot['name'],
                            'type': (spot.get('category') or 'nature').lower(),
                            'lat': safe_float(spot.get('latitude'), mun_lat),
                            'lng': safe_float(spot.get('longitude'), mun_lng),
                            'description': spot.get('description', ''),
                            'image': spot.get('main_image_url', 'https://images.unsplash.com/photo-1540541338287-41700207dee6?auto=format&fit=crop&w=400&q=80'),
                            'category': spot.get('category', 'Nature'),
                            'address': spot.get('address', ''),
                            'rating': safe_float(spot.get('rating'), 0.0),
                            'reviews_count': int(spot.get('reviews_count', 0))
                        } for spot in municipality_spots
                    ]
                })
            
            return jsonify({
                'success': True,
                'data': municipalities_with_spots
            })
            
        except Exception as e:
            print(f"Error fetching explore map data: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

# SUPERADMIN DASHBOARD ROUTES
    
    @app.route('/dashboard')
    def dashboard_page():
        return dashboardIndex()
    
    @app.route('/dashboard/accounts')
    def accounts_page():
        return accounts()
    
    @app.route('/dashboard/arrivals')
    def arrivals_page():
        return ArrivalsController.arrivals()
    
    @app.route('/dashboard/decision')
    def decision_page():
        return decision()
    
    @app.route('/dashboard/promoton')
    def promoton_page():
        from flask import render_template
        return render_template('views/dashboard/promoton.html')
    
    @app.route('/dashboard/chatbot-config')
    def chatbot_config_page():
        from flask import render_template
        return render_template('views/dashboard/chatbot-config.html')
    
    @app.route('/dashboard/lgu')
    def lgu_page():
        return lgu_dashboard()
        
    @app.route('/dashboard/lgu-management')
    def lgu_management_page():
        from controller.LguManagementController import lgu_management_index
        return lgu_management_index()

    @app.route('/dashboard/lgu-management/<municipality_id>')
    def lgu_management_details_page(municipality_id):
        from controller.LguManagementController import lgu_management_details
        return lgu_management_details(municipality_id)

    @app.route('/api/spots/<spot_id>/status', methods=['POST'])
    def api_spot_status(spot_id):
        from controller.LguManagementController import update_spot_status
        return update_spot_status(spot_id)
    
    @app.route('/dashboard/lgu/spots')
    def lgu_spots_page():
        return lgu_tourist_spots()

    @app.route('/dashboard/lgu/spots/add', methods=['POST'])
    def lgu_add_spot_page():
        return lgu_add_spot()

    @app.route('/dashboard/lgu/spots/<spot_id>/data', methods=['GET'])
    def lgu_get_spot_data_page(spot_id):
        return lgu_get_spot_data(spot_id)

    @app.route('/dashboard/lgu/spots/<spot_id>/edit', methods=['POST'])
    def lgu_edit_spot_page(spot_id):
        return lgu_edit_spot(spot_id)

    @app.route('/dashboard/lgu/spots/<spot_id>/delete', methods=['POST'])
    def lgu_delete_spot_page(spot_id):
        return lgu_delete_spot(spot_id)

    @app.route('/dashboard/lgu/arrivals-data')
    @login_required
    def lgu_arrivals_data_page():
        from flask import render_template, session
        from supabase_client import supabase
        
        try:
            # Fetch arrivals data from spot_arrivals table (filtered by user's municipality)
            municipality_id = session.get('municipality_id')
            query = supabase.table('spot_arrivals').select(
                '''
                id,
                report_month,
                this_city_male,
                this_city_female,
                other_city_male,
                other_city_female,
                other_prov_male,
                other_prov_female,
                foreign_male,
                foreign_female,
                tourist_spots!inner(name, municipality_id),
                municipalities!inner(name)
                '''
            ).order('report_month', desc=True)
            
            if municipality_id:
                query = query.eq('municipality_id', municipality_id)
                
            arrivals_response = query.execute()
            
            arrivals_data = arrivals_response.data
            
            # Process arrivals data to match template expectations
            arrivals = []
            for arrival in arrivals_data:
                domestic_total = (arrival['this_city_male'] + arrival['this_city_female'] + 
                                arrival['other_city_male'] + arrival['other_city_female'] +
                                arrival['other_prov_male'] + arrival['other_prov_female'])
                foreign_total = arrival['foreign_male'] + arrival['foreign_female']
                
                arrivals.append({
                    'id': arrival['id'],
                    'date': arrival['report_month'],
                    'spot_name': arrival['tourist_spots']['name'],
                    'domestic_total': domestic_total,
                    'foreign_total': foreign_total,
                    'municipality': arrival['municipalities']['name']
                })
            
            # Fetch tourist spots for dropdown (filtered by user's municipality)
            municipality_id = session.get('municipality_id')
            if municipality_id:
                spots_response = supabase.table('tourist_spots').select('id, name').eq('status', 'approved').eq('municipality_id', municipality_id).execute()
            else:
                spots_response = supabase.table('tourist_spots').select('id, name').eq('status', 'approved').execute()
            spots = spots_response.data
            
        except Exception as e:
            print(f"Error fetching arrivals data: {e}")
            arrivals = []
            spots = []
        
        return render_template('views/dashboard/lgu/arrivals_data.html', 
                            arrivals=arrivals, 
                            spots=spots)
    
    @app.route('/lgu/arrivals-data/add', methods=['POST'])
    @login_required
    def lgu_add_arrival_data():
        from flask import session, request, redirect, url_for, flash
        from supabase_client import supabase
        
        try:
            # Verify user has role_id 2 (LGU role)
            user_id = session.get('user')
            if not user_id:
                flash('User not authenticated', 'error')
                return redirect(url_for('lgu_arrivals_data_page'))
            
            # Check user's role from profiles table
            profile_response = supabase.table('profiles').select('role_id, municipality_id').eq('id', user_id).execute()
            if not profile_response.data or profile_response.data[0]['role_id'] != 2:
                flash('Unauthorized: Only LGU users can submit arrival data', 'error')
                return redirect(url_for('lgu_arrivals_data_page'))
            
            user_profile = profile_response.data[0]
            
            # Helper to safely cast empty strings to 0
            def get_int(key):
                val = request.form.get(key)
                return int(val) if val and val.strip() else 0

            # Prepare data for insertion
            data = {
                "tourist_spot_id": int(request.form.get('tourist_spot_id')),
                "municipality_id": user_profile['municipality_id'],  # From user's profile
                "submitted_by": user_id,                            # Verified logged-in user
                "report_month": request.form.get('submission_date'),
                
                # Granular demographics mapping directly from modal inputs
                "this_city_male": get_int('this_city_male'),
                "this_city_female": get_int('this_city_female'),
                "other_city_male": get_int('other_city_male'),
                "other_city_female": get_int('other_city_female'),
                "other_prov_male": get_int('other_prov_male'),
                "other_prov_female": get_int('other_prov_female'),
                "foreign_male": get_int('foreign_male'),
                "foreign_female": get_int('foreign_female')
            }

            # Insert into spot_arrivals table
            supabase.table('spot_arrivals').insert(data).execute()
            
            flash('Arrivals data successfully submitted!', 'success')
            
        except Exception as e:
            print(f"Error saving arrival data to Supabase: {e}")
            flash('Error submitting arrivals data. Please try again.', 'error')
        
        return redirect(url_for('lgu_arrivals_data_page'))
    
    @app.route('/dashboard/lgu/feedbacks')
    def lgu_feedbacks_page():
        from flask import render_template
        return render_template('views/dashboard/lgu/feedbacks.html')

# API ROUTES
    @app.route('/api/municipalities', methods=['GET'])
    def municipalities_api():
        from flask import jsonify
        from supabase_client import supabase
        try:
            response = supabase.table('municipalities').select('id, name').execute()
            return jsonify(response.data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/lara-chat', methods=['POST'])
    def lara_chat_api():
        from controller.HomeController import lara_chat
        return lara_chat()

    @app.route('/dashboard/arrivals/export', methods=['GET'])
    @login_required
    def export_arrivals():
        # This calls the controller method we just created
        return ArrivalsController.export_arrivals_to_excel()


# AUTH ROUTES
    @app.route("/login", methods=["GET", "POST"])
    def login_page():
        return admin_login()

    @app.route("/register", methods=["GET", "POST"])
    def register_page():
        return register()
    
    @app.route('/client-create-account', methods=["GET", "POST"])
    def client_create_account_page():
        return client_create_account()
    
    @app.route('/accounts/create', methods=['POST'])
    def dashboard_create_account_page():
        from controller.DashboardController import create_account as dashboard_create_account
        return dashboard_create_account()

    @app.route('/accounts/update/<string:user_id>', methods=['PUT'])
    def update_account_page(user_id):
        return update_account(user_id)

    @app.route('/accounts/delete/<string:user_id>', methods=['DELETE'])
    def delete_account_page(user_id):
        return delete_account(user_id)

    @app.route('/logout')
    def logout_page():
        return logout()
