import uuid
from flask import render_template, request, abort
from supabase_client import supabase, service_supabase

def home():
    # Check if the domain has 'admin' in it
    if 'admin-ltcato' in request.host:
        return render_template('views/admin_landing.html')
    
    # Otherwise, serve the normal user landing page
    return render_template('views/client/home.html')


def explore_map():
    return render_template('views/client/explore_map.html')

def destination_details(spot_id):
    """Route to view a dynamic destination detail page"""
    try:
        # Query supabase for the specific ID
        response = service_supabase.table('tourist_spots').select('*').eq('id', spot_id).single().execute()
        spot = response.data
        
        if not spot:
            # If ID doesn't exist, return a 404
            return abort(404, description="Tourist spot not found")
            
        # Pass the 'spot' dictionary to the Jinja2 template
        return render_template('views/client/destination_details.html', spot=spot)
        
    except Exception as e:
        print(f"Error fetching destination {spot_id}: {e}")
        return abort(500, description="Internal Server Error while fetching data")

def municipalities():
    try:
        # Fetch all municipalities
        municipalities_response = supabase.table('municipalities').select('*').order('name').execute()
        municipalities = municipalities_response.data
        
        # Fetch tourist spots to count them per municipality
        spots_response = supabase.table('tourist_spots').select('municipality_id', 'status').eq('status', 'approved').execute()
        spots = spots_response.data
        
        # Count spots per municipality
        spot_counts = {}
        for spot in spots:
            municipality_id = spot['municipality_id']
            if municipality_id:
                spot_counts[municipality_id] = spot_counts.get(municipality_id, 0) + 1
        
        # Attach spot counts to municipalities
        for municipality in municipalities:
            municipality['spot_count'] = spot_counts.get(municipality['id'], 0)
            
    except Exception as e:
        print(f"Error fetching municipalities: {e}")
        municipalities = []
        
    return render_template('views/client/municipalities.html', municipalities=municipalities)

def municipality_details(municipality_id):
    # In production, query your database for the specific municipality
    # and all tourist_spots where municipality_id matches
    return render_template('views/client/municipality_details.html')

def tourist_spots():
    try:
        # Query Supabase for all approved spots
        response = supabase.table('tourist_spots').select('*').eq('status', 'approved').order('created_at', desc=True).execute()
        spots = response.data
        
        # Pass the list of dictionaries to the Jinja2 template
        return render_template('views/client/tourist_spots.html', spots=spots)
        
    except Exception as e:
        print(f"Error fetching tourist spots list: {e}")
        return abort(500, description="Internal Server Error while fetching tourist spots.")

def lara_ai():
    return render_template('views/client/lara_ai.html')

def test_uploader():
    """Route to view and process the Mockup Uploader Tool"""
    if request.method == 'POST':
        try:
            # 1. Handle Main Image Upload
            main_image = request.files.get('main_image')
            main_image_url = ""
            
            if main_image and main_image.filename:
                # Create a unique filename to prevent overriding
                ext = main_image.filename.rsplit('.', 1)[1].lower() if '.' in main_image.filename else 'jpg'
                filename = f"destinations/{uuid.uuid4().hex}.{ext}"
                
                # Read file into bytes and upload via Python client
                file_bytes = main_image.read()
                service_supabase.storage.from_("images").upload(
                    path=filename,
                    file=file_bytes,
                    file_options={"content-type": main_image.content_type}
                )
                # Retrieve the public URL
                main_image_url = service_supabase.storage.from_("images").get_public_url(filename)

            # 2. Handle Gallery Images Upload
            gallery_images = request.files.getlist('gallery_images')
            gallery_urls = []
            
            for img in gallery_images:
                if img and img.filename:
                    ext = img.filename.rsplit('.', 1)[1].lower() if '.' in img.filename else 'jpg'
                    filename = f"destinations/{uuid.uuid4().hex}.{ext}"
                    
                    file_bytes = img.read()
                    service_supabase.storage.from_("images").upload(
                        path=filename,
                        file=file_bytes,
                        file_options={"content-type": img.content_type}
                    )
                    url = service_supabase.storage.from_("images").get_public_url(filename)
                    gallery_urls.append(url)

            # 3. Process the comma-separated lists
            highlights_str = request.form.get('highlights', '')
            highlights = [h.strip() for h in highlights_str.split(',') if h.strip()]

            audience_str = request.form.get('target_audience', '')
            target_audience = [t.strip() for t in audience_str.split(',') if t.strip()]

            # Get municipality ID from logged-in user session
            municipality_id = session.get('municipality_id')

            # 4. Construct payload for Supabase database
            payload = {
                "name": request.form.get('name'),
                "category": request.form.get('category'),
                "address": request.form.get('address'),
                "municipality_id": municipality_id,
                "hook_title": request.form.get('hook_title'),
                "hook_text": request.form.get('hook_text'),
                "description": request.form.get('description'),
                "opening_hours": request.form.get('opening_hours'),
                "entrance_fees": request.form.get('entrance_fees'),
                "what_to_bring": request.form.get('what_to_bring'),
                "parking_info": request.form.get('parking_info'),
                "highlights": highlights,
                "target_audience": target_audience,
                "main_image_url": main_image_url,
                "gallery_images": gallery_urls,
                "status": "approved"
            }

            # 5. Insert Record
            service_supabase.table('tourist_spots').insert(payload).execute()

            return render_template('views/admin/upload_mockup.html', success="Tourist spot uploaded successfully via Python!")

        except Exception as e:
            print(f"Error during upload: {e}")
            return render_template('views/admin/upload_mockup.html', error=str(e))

    # Render form on GET request
    return render_template('views/admin/upload_mockup.html')

def platform_features():
    """Route to display the platform features page"""
    return render_template('views/platform-features.html')

def security():
    """Route to display the security page"""
    return render_template('views/security.html')

def lgu_support():
    """Route to display the LGU support citizen charter page"""
    return render_template('views/lgu-support.html')

def lara_chat():
    """API endpoint for LARA AI chatbot with Supabase integration"""
    import os
    import json
    import google.generativeai as genai
    
    try:
        # Get API key from environment variable
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            return {
                'success': False,
                'error': 'API key not configured. Please contact administrator.'
            }, 500
        
        # Configure Gemini API
        genai.configure(api_key=api_key)
        
        # Get request data
        data = request.get_json()
        user_message = data.get('message', '').strip()
        chat_history = data.get('history', [])
        
        if not user_message:
            return {
                'success': False,
                'error': 'Message cannot be empty'
            }, 400
        
        # Fetch all approved tourist spots and municipalities from Supabase
        try:
            # Fetch tourist spots
            spots_response = supabase.table('tourist_spots').select('id, name, category, municipality_id, hook_title').eq('status', 'approved').order('created_at', desc=True).execute()
            spots_data = spots_response.data if spots_response.data else []
            
            # Fetch municipalities to map municipality_id to municipality names
            municipalities_response = supabase.table('municipalities').select('id, name').execute()
            municipalities_data = municipalities_response.data if municipalities_response.data else []
            
            # Create a dictionary mapping municipality_id to municipality name
            municipality_map = {m.get('id'): m.get('name', 'Unknown Municipality') for m in municipalities_data}
            
            # Format spots data grouped by municipality
            spots_info = ""
            if spots_data:
                # Group spots by municipality
                spots_by_municipality = {}
                for spot in spots_data:
                    municipality_id = spot.get('municipality_id')
                    municipality_name = municipality_map.get(municipality_id, 'Unknown Municipality')
                    
                    if municipality_name not in spots_by_municipality:
                        spots_by_municipality[municipality_name] = []
                    
                    spots_by_municipality[municipality_name].append(spot)
                
                # Build the info string organized by municipality
                spots_info = "\n\nAvailable Tourist Spots by Municipality:\n"
                for municipality_name in sorted(spots_by_municipality.keys()):
                    spots_info += f"\n{municipality_name}:\n"
                    for spot in spots_by_municipality[municipality_name]:
                        spots_info += f"  - {spot.get('name', 'Unknown')} ({spot.get('category', 'N/A')})\n"
            else:
                spots_info = "\n\nNo tourist spots currently in the database."
        except Exception as db_error:
            print(f"Error fetching spots from Supabase: {db_error}")
            spots_info = "\n\nUnable to fetch spots from database at the moment."
        
        # System prompt for LARA with database context
        system_prompt = f"""You are LARA (Laguna Artificial Resident Assistant), the official AI tourist guide for the Laguna Tourism website. 
Your personality is extremely welcoming, polite, enthusiastic, and knowledgeable about Laguna's culture, municipalities, and tourist spots. 

IMPORTANT RULES:
1. You were created and programmed by the 'LTCATO Development Team' (Laguna Tourism Culture Arts and Trade Office) Special Mention Lawrence Celis. If asked who made you, proudly state this.
2. ONLY provide information about tourist spots that are listed in the database below.
3. The MUNICIPALITY is the primary location identifier - not the address. A spot belongs to the municipality shown in the database, regardless of its stated address.
4. If someone asks about a spot NOT in the database, respond: "I can't find it in my database."
5. Keep all responses SHORT and CONCISE (2-3 sentences maximum).
6. Be friendly and helpful about Laguna's culture and tourism.
7. Answer in the language the user uses (English or Filipino or Taglish).
8. If the user asks for directions, provide a general description of how to get there from the city center of the municipality, but do NOT provide turn-by-turn directions.
9. If the user asks for directions, ask where they are from and where they want to go, then provide a estimated time and distance based on typical routes, but do NOT provide specific routes or turn-by-turn directions.
{spots_info}"""
        
        # Prepare conversation history for Gemini API
        messages = []
        for item in chat_history:
            role = "user" if item.get('role') == 'user' else 'model'
            messages.append({
                'role': role,
                'parts': [item.get('content', '')]
            })
        
        # Add current user message
        messages.append({
            'role': 'user',
            'parts': [user_message]
        })
        
        # Call Gemini API
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=system_prompt
        )
        
        response = model.generate_content(messages)
        
        if response and response.text:
            return {
                'success': True,
                'reply': response.text
            }, 200
        else:
            return {
                'success': False,
                'error': 'No response from AI model'
            }, 500
            
    except Exception as e:
        print(f"Error in LARA chat: {str(e)}")
        return {
            'success': False,
            'error': f'Error processing request: {str(e)}'
        }, 500