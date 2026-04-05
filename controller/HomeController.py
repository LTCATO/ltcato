from flask import render_template

def home():
    return render_template('views/client/home.html')

def explore_map():
    return render_template('views/client/explore_map.html')

def destination_details(spot_id):
    # Here you would query Supabase:
    # spot = supabase.table('tourist_spots').select('*').eq('id', spot_id).single().execute().data
    # feedbacks = supabase.table('spot_feedbacks').select('*').eq('tourist_spot_id', spot_id).execute().data
    
    # Pass the data to the template
    # return render_template('views/destination_details.html', spot=spot, feedbacks=feedbacks)
    
    # For now, just render the static template
    return render_template('views/client/destination_details.html')

def municipalities():
    # In production, query your database for all municipalities
    return render_template('views/client/municipalities.html')

def municipality_details(municipality_id):
    # In production, query your database for the specific municipality
    # and all tourist_spots where municipality_id matches
    return render_template('views/client/municipality_details.html')

def tourist_spots():
    # In production, query your database for all approved tourist_spots
    return render_template('views/client/tourist_spots.html')

def lara_ai():
    return render_template('views/client/lara_ai.html')