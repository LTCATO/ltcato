from utils import role_required, login_required
from flask import render_template, request, jsonify
from supabase_client import supabase, service_supabase

@login_required
@role_required('super_admin')
def lgu_management_index():
    """Render LGU overview page (selecting municipality)."""
    active_menu = ['lgu_management']
    try:
        # Fetch all municipalities
        municipalities_response = supabase.table('municipalities').select('*').order('name').execute()
        municipalities = municipalities_response.data
        
        # Fetch all pending spots to count them per municipality
        pending_spots_response = supabase.table('tourist_spots').select('municipality_id').eq('status', 'pending').execute()
        pending_counts = {}
        for spot in pending_spots_response.data:
            m_id = spot.get('municipality_id')
            if m_id:
                pending_counts[m_id] = pending_counts.get(m_id, 0) + 1
        
        # Attach the counts to our municipalities list
        for m in municipalities:
            m['pending_count'] = pending_counts.get(m['id'], 0)
            
    except Exception as e:
        print(f"Error fetching LGU Management overview: {e}")
        municipalities = []
        
    return render_template('views/dashboard/lgu_management/index.html', 
                            municipalities=municipalities, 
                            menu=active_menu)

@login_required
@role_required('super_admin')
def lgu_management_details(municipality_id):
    """Render details page for a specific LGU to view/approve its spots."""
    active_menu = ['lgu_management']
    try:
        # Fetch municipality details
        municipality_response = supabase.table('municipalities').select('*').eq('id', municipality_id).single().execute()
        municipality = municipality_response.data
        
        # Fetch tourist spots for this municipality
        spots_response = supabase.table('tourist_spots').select('*').eq('municipality_id', municipality_id).order('created_at', desc=True).execute()
        spots = spots_response.data
        
    except Exception as e:
        print(f"Error fetching LGU details: {e}")
        municipality = None
        spots = []

    return render_template('views/dashboard/lgu_management/details.html', 
                           municipality=municipality,
                           spots=spots,
                           menu=active_menu)

@login_required
@role_required('super_admin')
def update_spot_status(spot_id):
    """API endpoint to update a tourist spot's status."""
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status not in ['approved', 'rejected', 'pending']:
        return jsonify({"success": False, "message": "Invalid status."}), 400
        
    try:
        # Update the status using service_supabase (admin privileges)
        service_supabase.table('tourist_spots').update({"status": new_status}).eq('id', spot_id).execute()
        return jsonify({"success": True, "message": f"Spot status updated to {new_status}."})
    except Exception as e:
        print(f"Error updating spot status: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
