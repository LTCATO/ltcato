import uuid
from flask import render_template, session, request, jsonify
from utils import role_required, login_required
from supabase_client import supabase, service_supabase

@login_required
@role_required('super_admin')
def dashboardIndex():
    active_menu = ['dashboard', 'analytics']
    return render_template('views/dashboard/index.html', menu=active_menu)

@login_required
@role_required('super_admin')
def accounts():
    active_menu = ['accounts']

    try:
        # 1. Fetch profiles and automatically join roles and municipalities
        # Supabase allows fetching related tables using the foreign key relationships
        profiles_response = supabase.table('profiles').select(
            'id, first_name, last_name, created_at, '
            'roles(role_name), municipalities(name)'
        ).execute()
        
        profiles = profiles_response.data

        # 2. Fetch emails using service_supabase (requires SERVICE_ROLE_KEY)
        auth_users = service_supabase.auth.admin.list_users()
        email_map = {user.id: user.email for user in auth_users}
        for p in profiles:
            p['email'] = email_map.get(p['id'], 'No Email Found')

        # 3. Fetch data for the "Add Account" modal dropdowns
        mun_response = supabase.table('municipalities').select('id, name').execute()
        municipalities = mun_response.data

        roles_response = supabase.table('roles').select('id, role_name').execute()
        roles = roles_response.data
        print(f"Fetched {len(profiles)} profiles, {len(municipalities)} municipalities, and {len(roles)} roles from Supabase.")

        # 3. Calculate statistics dynamically
        stats = {
            'total': len(profiles),
            'active': len(profiles), # Adjust if you add a 'status' column later
            'pending': 0,            # Adjust based on your workflow logic
            'municipalities': len(municipalities)
        }

    except Exception as e:
        print(f"Error fetching data from Supabase: {e}")
        profiles = []
        municipalities = []
        roles = []
        stats = {'total': 0, 'active': 0, 'pending': 0, 'municipalities': 0}

    return render_template(
        'views/dashboard/accounts.html', 
        menu=active_menu,
        profiles=profiles,
        municipalities=municipalities,
        roles=roles,
        stats=stats
    )

@login_required
@role_required('super_admin')
def create_account():
    data = request.get_json()
    
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')
    role_id = data.get('role_id')
    municipality_id = data.get('municipality_id')

    try:
        auth_response = service_supabase.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True 
        })
        
        new_user_id = auth_response.user.id

        profile_data = {
            "id": new_user_id,
            "first_name": first_name,
            "last_name": last_name,
            "role_id": int(role_id),
            "municipality_id": int(municipality_id) if municipality_id else None
        }
        
        service_supabase.table('profiles').insert(profile_data).execute()

        return jsonify({
            "success": True, 
            "message": "Account created successfully!"
        }), 201

    except Exception as e:
        print(f"Error creating account: {e}")
        # Return the error message to the frontend for debugging
        return jsonify({
            "success": False, 
            "message": str(e)
        }), 400

@login_required
@role_required('super_admin')
def update_account(user_id):
    data = request.get_json()
    try:
        # 1. Update Auth data if provided (email/password)
        auth_update_data = {}
        if data.get('email'):
            auth_update_data['email'] = data.get('email')
            auth_update_data['email_confirm'] = True # Auto-confirm new email
        if data.get('password'):  # Only update password if they typed a new one
            auth_update_data['password'] = data.get('password')

        if auth_update_data:
            service_supabase.auth.admin.update_user_by_id(user_id, auth_update_data)

        # 2. Update Public Profiles table
        role_id = data.get('role_id')
        municipality_id = data.get('municipality_id')
        
        profile_update_data = {
            "first_name": data.get('first_name'),
            "last_name": data.get('last_name'),
            "role_id": int(role_id) if role_id else None,
            "municipality_id": int(municipality_id) if municipality_id else None
        }
        
        service_supabase.table('profiles').update(profile_update_data).eq('id', user_id).execute()

        return jsonify({"success": True, "message": "Account updated successfully!"})
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@login_required
@role_required('super_admin')
def delete_account(user_id):
    try:
        # 1. Delete from profiles (Requires executing before auth deletion due to foreign key constraints, unless CASCADE is ON)
        service_supabase.table('profiles').delete().eq('id', user_id).execute()
        
        # 2. Delete Auth User entirely (Requires SERVICE_ROLE_KEY)
        service_supabase.auth.admin.delete_user(user_id)

        return jsonify({"success": True, "message": "Account permanently deleted."})
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@login_required
@role_required('lgu_admin')
def lgu_dashboard():
    active_menu = ['lgu']
    municipality_id = session.get('municipality_id')
    
    try:
        # Fetch municipality details
        municipality_response = supabase.table('municipalities').select('*').eq('id', municipality_id).execute()
        municipality = municipality_response.data[0] if municipality_response.data else None
        
        # Fetch tourist spots for this municipality
        spots_response = supabase.table('tourist_spots').select('*').eq('municipality_id', municipality_id).execute()
        tourist_spots = spots_response.data
        
        # Calculate tourist spots statistics
        total_spots = len(tourist_spots)
        active_spots = len([spot for spot in tourist_spots if spot.get('status') == 'approved'])
        pending_spots = len([spot for spot in tourist_spots if spot.get('status') == 'pending'])
        
        # Fetch recent arrivals for this municipality
        arrivals_response = supabase.table('tourist_arrivals').select('*').eq('municipality_id', municipality_id).order('created_at', desc=True).limit(12).execute()
        recent_arrivals = arrivals_response.data
        
        # Calculate total arrivals
        total_arrivals = sum([
            arrival.get('local_count', 0) + arrival.get('foreigner_count', 0) + arrival.get('outsider_count', 0)
            for arrival in recent_arrivals
        ])
        
        # Fetch recent feedback for tourist spots in this municipality
        if tourist_spots:
            spot_ids = [spot['id'] for spot in tourist_spots]
            feedback_response = supabase.table('spot_feedbacks').select('*').in_('tourist_spot_id', spot_ids).order('created_at', desc=True).limit(10).execute()
            recent_feedback = feedback_response.data
            
            # Calculate average rating
            if recent_feedback:
                avg_rating = sum(feedback.get('rating', 0) for feedback in recent_feedback) / len(recent_feedback)
            else:
                avg_rating = 0
        else:
            recent_feedback = []
            avg_rating = 0
        
        # Prepare statistics
        stats = {
            'total_arrivals': total_arrivals,
            'total_spots': total_spots,
            'active_spots': active_spots,
            'pending_spots': pending_spots,
            'avg_rating': round(avg_rating, 1) if avg_rating else 0,
            'recent_feedback_count': len(recent_feedback)
        }
        
    except Exception as e:
        print(f"Error fetching LGU dashboard data: {e}")
        municipality = None
        tourist_spots = []
        recent_arrivals = []
        recent_feedback = []
        stats = {
            'total_arrivals': 0,
            'total_spots': 0,
            'active_spots': 0,
            'pending_spots': 0,
            'avg_rating': 0,
            'recent_feedback_count': 0
        }
    
    return render_template(
        'views/dashboard/lgu/index.html', 
        menu=active_menu,
        municipality=municipality,
        tourist_spots=tourist_spots,
        recent_arrivals=recent_arrivals,
        recent_feedback=recent_feedback,
        stats=stats
    )

@login_required
@role_required('lgu_admin')
def tourist_spots():
    active_menu = ['spots']
    municipality_id = session.get('municipality_id')
    
    try:
        # Fetch municipality details
        municipality_response = supabase.table('municipalities').select('*').eq('id', municipality_id).execute()
        municipality = municipality_response.data[0] if municipality_response.data else None
        
        # Fetch tourist spots for this municipality
        spots_response = supabase.table('tourist_spots').select('*').eq('municipality_id', municipality_id).execute()
        tourist_spots = spots_response.data
        
        # Fetch user profiles for created_by and approved_by fields
        user_ids = set()
        for spot in tourist_spots:
            if spot.get('created_by'):
                user_ids.add(spot['created_by'])
            if spot.get('approved_by'):
                user_ids.add(spot['approved_by'])
        
        user_profiles = {}
        if user_ids:
            profiles_response = supabase.table('profiles').select('id, first_name, last_name').in_('id', list(user_ids)).execute()
            for profile in profiles_response.data:
                user_profiles[profile['id']] = profile
        
        # Attach user profiles to spots
        for spot in tourist_spots:
            if spot.get('created_by') and spot['created_by'] in user_profiles:
                spot['created_by_profile'] = user_profiles[spot['created_by']]
            if spot.get('approved_by') and spot['approved_by'] in user_profiles:
                spot['approved_by_profile'] = user_profiles[spot['approved_by']]
        
        # Calculate tourist spots statistics
        total_spots = len(tourist_spots)
        active_spots = len([spot for spot in tourist_spots if spot.get('status') == 'approved'])
        pending_spots = len([spot for spot in tourist_spots if spot.get('status') == 'pending'])
        
        # Fetch recent feedback for tourist spots in this municipality
        if tourist_spots:
            spot_ids = [spot['id'] for spot in tourist_spots]
            feedback_response = supabase.table('spot_feedbacks').select('*').in_('tourist_spot_id', spot_ids).order('created_at', desc=True).limit(10).execute()
            recent_feedback = feedback_response.data
            
            # Calculate average rating
            if recent_feedback:
                avg_rating = sum(feedback.get('rating', 0) for feedback in recent_feedback) / len(recent_feedback)
            else:
                avg_rating = 0
        else:
            recent_feedback = []
            avg_rating = 0
        
        # Prepare statistics
        stats = {
            'total_spots': total_spots,
            'active_spots': active_spots,
            'pending_spots': pending_spots,
            'avg_rating': round(avg_rating, 1) if avg_rating else 0,
            'recent_feedback_count': len(recent_feedback)
        }
        
        # Prepare category data for chart
        categories = {}
        for spot in tourist_spots:
            cat = spot.get('category') or 'other'
            categories[cat] = categories.get(cat, 0) + 1
        
        category_labels = list(categories.keys())
        category_data = list(categories.values())
        
    except Exception as e:
        print(f"Error fetching tourist spots data: {e}")
        municipality = None
        tourist_spots = []
        recent_feedback = []
        stats = {
            'total_spots': 0,
            'active_spots': 0,
            'pending_spots': 0,
            'avg_rating': 0,
            'recent_feedback_count': 0
        }
        category_labels = []
        category_data = []
    
    return render_template(
        'views/dashboard/lgu/spots.html', 
        menu=active_menu,
        municipality=municipality,
        tourist_spots=tourist_spots,
        recent_feedback=recent_feedback,
        stats=stats,
        category_labels=category_labels,
        category_data=category_data
    )   

@login_required
@role_required('lgu_admin')
def lgu_add_spot():
    """Handle tourist spot creation from the LGU dashboard."""
    if request.method != 'POST':
        return jsonify({"success": False, "message": "Method not allowed"}), 405

    try:
        # 1. Handle Main Image Upload
        main_image = request.files.get('main_image')
        main_image_url = ""

        if main_image and main_image.filename:
            ext = main_image.filename.rsplit('.', 1)[1].lower() if '.' in main_image.filename else 'jpg'
            filename = f"destinations/{uuid.uuid4().hex}.{ext}"

            file_bytes = main_image.read()
            service_supabase.storage.from_("images").upload(
                path=filename,
                file=file_bytes,
                file_options={"content-type": main_image.content_type}
            )
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

        # 3. Process comma-separated lists
        highlights_str = request.form.get('highlights', '')
        highlights = [h.strip() for h in highlights_str.split(',') if h.strip()]

        audience_str = request.form.get('target_audience', '')
        target_audience = [t.strip() for t in audience_str.split(',') if t.strip()]

        # 4. Get municipality ID and user ID from logged-in LGU session
        municipality_id = session.get('municipality_id')
        user_id = session.get('user')

        # 5. Construct payload
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
            "latitude": float(request.form.get('latitude')) if request.form.get('latitude') else None,
            "longitude": float(request.form.get('longitude')) if request.form.get('longitude') else None,
            "created_by": user_id,
            "status": "pending"
        }

        # 6. Insert record
        service_supabase.table('tourist_spots').insert(payload).execute()

        return jsonify({"success": True, "message": "Tourist spot submitted successfully!"}), 200

    except Exception as e:
        print(f"Error adding LGU tourist spot: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@login_required
@role_required('lgu_admin')
def lgu_get_spot_data(spot_id):
    """Return a single tourist spot's data as JSON (used by the Edit modal)."""
    try:
        municipality_id = session.get('municipality_id')
        response = service_supabase.table('tourist_spots') \
            .select('*') \
            .eq('id', spot_id) \
            .eq('municipality_id', municipality_id) \
            .single() \
            .execute()

        spot = response.data
        if not spot:
            return jsonify({"success": False, "message": "Spot not found or access denied."}), 404

        return jsonify({"success": True, "spot": spot}), 200

    except Exception as e:
        print(f"Error fetching spot data: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@login_required
@role_required('lgu_admin')
def lgu_edit_spot(spot_id):
    """Update an existing tourist spot. Optionally replaces images if new files are supplied."""
    try:
        municipality_id = session.get('municipality_id')

        # Build the text-field payload (same structure as insert)
        highlights_str = request.form.get('highlights', '')
        highlights = [h.strip() for h in highlights_str.split(',') if h.strip()]

        audience_str = request.form.get('target_audience', '')
        target_audience = [t.strip() for t in audience_str.split(',') if t.strip()]

        payload = {
            "name": request.form.get('name'),
            "category": request.form.get('category'),
            "address": request.form.get('address'),
            "hook_title": request.form.get('hook_title'),
            "hook_text": request.form.get('hook_text'),
            "description": request.form.get('description'),
            "opening_hours": request.form.get('opening_hours'),
            "entrance_fees": request.form.get('entrance_fees'),
            "what_to_bring": request.form.get('what_to_bring'),
            "parking_info": request.form.get('parking_info'),
            "highlights": highlights,
            "target_audience": target_audience,
            "latitude": float(request.form.get('latitude')) if request.form.get('latitude') else None,
            "longitude": float(request.form.get('longitude')) if request.form.get('longitude') else None,
        }

        # Optional: replace main image if a new file was uploaded
        main_image = request.files.get('main_image')
        if main_image and main_image.filename:
            ext = main_image.filename.rsplit('.', 1)[1].lower() if '.' in main_image.filename else 'jpg'
            filename = f"destinations/{uuid.uuid4().hex}.{ext}"
            file_bytes = main_image.read()
            service_supabase.storage.from_("images").upload(
                path=filename,
                file=file_bytes,
                file_options={"content-type": main_image.content_type}
            )
            payload["main_image_url"] = service_supabase.storage.from_("images").get_public_url(filename)

        # Optional: append new gallery images
        gallery_images = request.files.getlist('gallery_images')
        new_gallery_urls = []
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
                new_gallery_urls.append(url)

        if new_gallery_urls:
            # Fetch existing gallery and append new ones
            existing = service_supabase.table('tourist_spots').select('gallery_images') \
                .eq('id', spot_id).single().execute()
            existing_gallery = existing.data.get('gallery_images') or []
            payload["gallery_images"] = existing_gallery + new_gallery_urls

        # Update only the record that belongs to this municipality (security check)
        service_supabase.table('tourist_spots') \
            .update(payload) \
            .eq('id', spot_id) \
            .eq('municipality_id', municipality_id) \
            .execute()

        return jsonify({"success": True, "message": "Tourist spot updated successfully!"}), 200

    except Exception as e:
        print(f"Error editing tourist spot: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@login_required
@role_required('lgu_admin')
def lgu_delete_spot(spot_id):
    """Delete a tourist spot record. Only deletes from DB; storage files are left intact."""
    try:
        municipality_id = session.get('municipality_id')

        # Verify ownership before deleting
        service_supabase.table('tourist_spots') \
            .delete() \
            .eq('id', spot_id) \
            .eq('municipality_id', municipality_id) \
            .execute()

        return jsonify({"success": True, "message": "Tourist spot deleted."}), 200

    except Exception as e:
        print(f"Error deleting tourist spot: {e}")
        return jsonify({"success": False, "message": str(e)}), 500