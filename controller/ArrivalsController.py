from utils import role_required, login_required
from flask import render_template, session, request, flash, redirect, url_for, send_file
from supabase_client import supabase, service_supabase
import io

# Try to import pandas, make it optional
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

class ArrivalsController:

    @staticmethod
    @login_required
    @role_required('super_admin')
    def arrivals():
        """Render arrivals management page"""
        active_menu = ['arrivals']
        try:
            # Fetch arrivals sorted by newest first
            # (Querying tourist_arrivals to not break any legacy dashboards, but can query spot_arrivals)
            response = supabase.table('tourist_arrivals').select('*').order('created_at', desc=True).execute()
            db_arrivals = response.data
            
            # We process the raw arrival data to match the expected Jinja logic if needed
            # Fallback fields are handled in Jinja2 template.
            arrivals = db_arrivals
            
        except Exception as e:
            print(f"Error fetching tourist arrivals list: {e}")
            arrivals = []

        return render_template('views/dashboard/arrivals.html', 
                            arrivals=arrivals,
                            menu=active_menu)


    def get_arrival(arrival_id):
        """Get specific arrival details from Supabase"""
        try:
            # Replaced mock data with live query from the new spot_arrivals table
            response = supabase.table('spot_arrivals').select('*').eq('id', arrival_id).execute()
            if response.data:
                return response.data[0]
            return {}
        except Exception as e:
            print(f"Error fetching arrival details: {e}")
            return {}


    def delete_arrival(arrival_id):
        """Delete an arrival submission"""
        try:
            supabase.table('spot_arrivals').delete().eq('id', arrival_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting arrival: {e}")
            return False


    def create_arrival(data=None):
        """Create a new arrival submission mapping to the new spot_arrivals schema"""
        try:
            # If no explicit data dict is passed by routes.py, construct it from the Flask request
            if data is None:
                # Helper to safely cast empty strings to 0
                def get_int(key):
                    val = request.form.get(key)
                    return int(val) if val and val.strip() else 0

                data = {
                    "tourist_spot_id": request.form.get('tourist_spot_id'),
                    "municipality_id": session.get('municipality_id'), # Pulled automatically from auth session
                    "submitted_by": session.get('user_id'),            # Pulled automatically from auth session
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

            # Insert into the new spot_arrivals table
            supabase.table('spot_arrivals').insert(data).execute()
            return True
            
        except Exception as e:
            print(f"Error saving arrival data to Supabase: {e}")
            return False


    def update_arrival(arrival_id, data):
        """Update an existing arrival submission"""
        try:
            supabase.table('spot_arrivals').update(data).eq('id', arrival_id).execute()
            return True
        except Exception as e:
            print(f"Error updating arrival record: {e}")
            return False
    
    @staticmethod
    def export_arrivals_to_excel():
        if not PANDAS_AVAILABLE:
            return "Pandas is not installed. Please install pandas to use export functionality.", 500
            
        try:
            # 1. Fetch data from your Supabase table
            # NOTE: Replace 'tourist_arrivals' with your actual table name in Supabase
            response = supabase.table('spot_arrivals').select('*').execute()
            data = response.data

            if not data:
                return "No data available to export", 404

            df = pd.DataFrame(data)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Tourist Arrivals')

            output.seek(0)

            return send_file(
                output,
                download_name='spot_arrivals.xlsx',
                as_attachment=True,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        except Exception as e:
            print(f"Error exporting arrivals to Excel: {e}")
            return f"An error occurred while generating the Excel file: {str(e)}", 500