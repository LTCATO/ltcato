import math
from datetime import datetime, timedelta
from flask import render_template, request, jsonify, session, redirect, url_for, flash
from supabase_client import supabase, service_supabase

# ---------------------------------------------------------------------------
# Visit duration per category (in minutes) – used for ETA calculation
# ---------------------------------------------------------------------------
CATEGORY_DURATION = {
    "nature":       120,   # 2 hours
    "resort":       180,   # 3 hours
    "pilgrimage":    30,   # 30 minutes
    "historical":    60,   # 1 hour
    "cultural":      60,
    "adventure":    120,
    "beach":        150,
    "waterfall":    120,
    "park":          90,
    "museum":        60,
    "landmark":      45,
    "restaurant":    45,
    "cafe":          30,
    "food":          45,
}
DEFAULT_DURATION = 60  # fallback: 1 hour

# Food/Restaurant category keywords for lunch suggestions
FOOD_KEYWORDS = ['restaurant', 'cafe', 'food', 'fast food', 'pizzeria', 'bar', 'diner']

# Buffer between stops in minutes (travel overhead, short breaks)
STOP_BUFFER = 15

# Radius (km) for "nearby spot suggestion"
SUGGESTION_RADIUS_KM = 10

# Average speed (km/h) per travel mode
TRAVEL_SPEEDS = {
    "driving":    40,   # car/jeep on Laguna roads
    "motorcycle": 35,
    "bus":        25,
    "foot":        5,
    "bike":       18,
}
DEFAULT_SPEED = 40


def parse_fee(value) -> float:
    """
    Safely extract a numeric entrance fee from a free-text field.
    Examples handled:
        '100'                        -> 100.0
        '₱50'                        -> 50.0
        '50 per person'              -> 50.0
        'Free'                       -> 0.0
        'pay only for plants/items'  -> 0.0
        None / ''                    -> 0.0
    """
    import re
    if not value:
        return 0.0
    match = re.search(r'[\d]+(?:\.\d+)?', str(value).replace(',', ''))
    return float(match.group()) if match else 0.0


# ---------------------------------------------------------------------------
# Haversine formula – calculate straight-line distance between two lat/lng
# ---------------------------------------------------------------------------
def haversine(lat1, lng1, lat2, lng2):
    """Return distance in kilometres between two coordinates."""
    try:
        R = 6371  # Earth radius in km
        phi1, phi2 = math.radians(float(lat1)), math.radians(float(lat2))
        dphi = math.radians(float(lat2) - float(lat1))
        dlambda = math.radians(float(lng2) - float(lng1))
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        return 2 * R * math.asin(math.sqrt(a))
    except (TypeError, ValueError):
        return 9999  # treat un-geocoded spots as very far away


def estimate_travel_minutes(dist_km, speed_kmh=DEFAULT_SPEED):
    """Travel time in minutes given a distance and average speed."""
    return max(5, int((dist_km / speed_kmh) * 60))


# ---------------------------------------------------------------------------
# Nearest-Neighbor TSP heuristic
# ---------------------------------------------------------------------------
def nearest_neighbor_sort(start_lat, start_lng, stops):
    """
    Re-order `stops` (list of dicts with 'latitude' and 'longitude') using
    the nearest-neighbor greedy heuristic starting from (start_lat, start_lng).
    Returns a new list in optimized visit order.
    """
    if not stops:
        return []

    unvisited = stops[:]
    ordered = []
    cur_lat, cur_lng = start_lat, start_lng

    while unvisited:
        nearest = min(unvisited, key=lambda s: haversine(cur_lat, cur_lng, s["latitude"], s["longitude"]))
        ordered.append(nearest)
        cur_lat, cur_lng = nearest["latitude"], nearest["longitude"]
        unvisited.remove(nearest)

    return ordered


# ---------------------------------------------------------------------------
# 2-opt improvement – uncross overlapping path segments
# ---------------------------------------------------------------------------
def two_opt(stops, start_lat, start_lng):
    """
    Apply the 2-opt local search to improve the nearest-neighbor solution.
    Repeatedly reverses sub-sequences of the route if doing so reduces the
    total straight-line distance.  Returns the improved list.
    """
    if len(stops) < 3:
        return stops

    def route_distance(route):
        total = haversine(start_lat, start_lng, route[0]["latitude"], route[0]["longitude"])
        for i in range(len(route) - 1):
            total += haversine(
                route[i]["latitude"], route[i]["longitude"],
                route[i + 1]["latitude"], route[i + 1]["longitude"]
            )
        return total

    best = stops[:]
    best_dist = route_distance(best)
    improved = True

    while improved:
        improved = False
        for i in range(len(best) - 1):
            for j in range(i + 2, len(best)):
                # Reverse the segment between i+1 and j (inclusive)
                candidate = best[:i + 1] + best[i + 1:j + 1][::-1] + best[j + 1:]
                candidate_dist = route_distance(candidate)
                if candidate_dist < best_dist - 1e-6:
                    best = candidate
                    best_dist = candidate_dist
                    improved = True
                    break   # restart inner loop after improvement
            if improved:
                break

    return best


# ---------------------------------------------------------------------------
# ETA builder – walks the ordered list and stamps arrival/departure times
# ---------------------------------------------------------------------------
def build_timeline(ordered_stops, start_lat, start_lng, departure_time: datetime,
                   speed_kmh=DEFAULT_SPEED, duration_overrides=None):
    """
    Annotate each stop with estimated_arrival and estimated_departure.
    `duration_overrides` is a dict {str(id): minutes} for user-customised stay times.
    Returns the annotated list.
    """
    if duration_overrides is None:
        duration_overrides = {}

    cur_lat, cur_lng = start_lat, start_lng
    current_time = departure_time

    for stop in ordered_stops:
        dist_km = haversine(cur_lat, cur_lng, stop["latitude"], stop["longitude"])
        travel_min = estimate_travel_minutes(dist_km, speed_kmh)

        arrival = current_time + timedelta(minutes=travel_min)
        category = (stop.get("category") or "").lower()

        # Respect user override, then category default, then global default
        sid = str(stop.get("id", ""))
        if sid in duration_overrides:
            try:
                visit_min = int(duration_overrides[sid])
            except (TypeError, ValueError):
                visit_min = CATEGORY_DURATION.get(category, DEFAULT_DURATION)
        else:
            visit_min = CATEGORY_DURATION.get(category, DEFAULT_DURATION)

        departure = arrival + timedelta(minutes=visit_min)

        stop["distance_from_prev_km"]   = round(dist_km, 2)
        stop["travel_minutes"]           = travel_min
        stop["visit_duration_minutes"]   = visit_min
        stop["estimated_arrival"]        = arrival.strftime("%I:%M %p")
        stop["estimated_departure"]      = departure.strftime("%I:%M %p")

        # Advance for next iteration
        current_time = departure + timedelta(minutes=STOP_BUFFER)
        cur_lat, cur_lng = stop["latitude"], stop["longitude"]

    return ordered_stops


# ---------------------------------------------------------------------------
# Food suggestion helpers
# ---------------------------------------------------------------------------
def is_food_category(category):
    """Check if a category is a food/restaurant type."""
    if not category:
        return False
    cat_lower = str(category).lower()
    return any(keyword in cat_lower for keyword in FOOD_KEYWORDS)


def should_suggest_food(start_time_str: str) -> bool:
    """Check if current trip time is during lunch hours (11am - 1pm)."""
    try:
        hour = int(start_time_str.split(':')[0])
        return 11 <= hour < 13
    except (ValueError, IndexError):
        return False


# ---------------------------------------------------------------------------
# Nearby suggestion logic
# ---------------------------------------------------------------------------
def find_nearby_suggestions(ordered_stops, all_spots, max_suggestions=3, start_time_str=None):
    """
    Given an ordered itinerary, find approved spots that are close to any
    stop in the itinerary but NOT already included.  Returns up to
    `max_suggestions` unique nearby spots, prioritizing food stops during lunch hours.
    """
    selected_ids = {s["id"] for s in ordered_stops}
    suggestions = {}  # id -> (spot, min_dist)

    for stop in ordered_stops:
        for spot in all_spots:
            if spot["id"] in selected_ids:
                continue
            dist = haversine(stop["latitude"], stop["longitude"], spot["latitude"], spot["longitude"])
            if dist <= SUGGESTION_RADIUS_KM:
                if spot["id"] not in suggestions or dist < suggestions[spot["id"]][1]:
                    suggestions[spot["id"]] = (spot, round(dist, 2))

    # Sort by distance ascending
    sorted_suggestions = sorted(suggestions.values(), key=lambda x: x[1])
    
    # If it's lunch time, prioritize food stops
    if start_time_str and should_suggest_food(start_time_str):
        food_suggestions = []
        other_suggestions = []
        
        for s in sorted_suggestions:
            if is_food_category(s[0].get("category")):
                food_suggestions.append(s)
            else:
                other_suggestions.append(s)
        
        # Combine: food first, then others
        sorted_suggestions = food_suggestions + other_suggestions
    
    return [
        {**s[0], "nearest_km": s[1]}
        for s in sorted_suggestions[:max_suggestions]
    ]


# ---------------------------------------------------------------------------
# ROUTE HANDLERS
# ---------------------------------------------------------------------------

def itinerary_page():
    """
    GET /itinerary
    Render the itinerary planner page.  Requires login.
    Passes all approved tourist spots + municipalities for the frontend.
    """
    # if "user" not in session:
    #     flash("Please log in to use the Itinerary Planner.", "error")
    #     return redirect(url_for("login_signup_page"))

    try:
        # Fetch municipalities
        mun_res = supabase.table("municipalities").select("id, name, latitude, longitude").order("name").execute()
        municipalities = mun_res.data or []

        # Fetch approved tourist spots
        spots_res = (
            supabase.table("tourist_spots")
            .select("id, name, category, municipality_id, latitude, longitude, entrance_fees, main_image_url, description, address")
            .eq("status", "approved")
            .order("name")
            .execute()
        )
        spots = spots_res.data or []

        # Attach municipality name to each spot for display
        mun_map = {m["id"]: m["name"] for m in municipalities}
        for spot in spots:
            spot["municipality_name"] = mun_map.get(spot.get("municipality_id"), "Laguna")

    except Exception as e:
        print(f"[ItineraryController] Error fetching data: {e}")
        municipalities = []
        spots = []

    return render_template(
        "views/client/itinerary.html",
        municipalities=municipalities,
        spots=spots,
    )


def get_spots_map_data():
    """
    GET /api/spots/map-data
    Return all approved spots as JSON for the frontend map.
    """
    # if "user" not in session:
    #     return jsonify({"success": False, "error": "Unauthorized"}), 401

    try:
        spots_res = (
            supabase.table("tourist_spots")
            .select("id, name, category, municipality_id, latitude, longitude, entrance_fees, main_image_url, description, address")
            .eq("status", "approved")
            .execute()
        )
        spots = spots_res.data or []

        mun_res = supabase.table("municipalities").select("id, name").execute()
        mun_map = {m["id"]: m["name"] for m in (mun_res.data or [])}

        for spot in spots:
            spot["municipality_name"] = mun_map.get(spot.get("municipality_id"), "Laguna")

        return jsonify({"success": True, "spots": spots})

    except Exception as e:
        print(f"[ItineraryController] get_spots_map_data error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


def optimize_itinerary():
    """
    POST /api/itinerary/optimize
    Body JSON:
        {
            "start_lat":          float,
            "start_lng":          float,
            "start_time":         "HH:MM"  (24-hour),
            "end_time":           "HH:MM"  (optional, 24-hour),
            "date":               "YYYY-MM-DD",
            "travel_mode":        "driving" | "motorcycle" | "bus" | "foot" | "bike",
            "manual_order":       bool,   // if true, skip TSP — just build timeline
            "duration_overrides": { "stop_id": minutes, ... },
            "stops": [
                { "id": "...", "name": "...", "latitude": float, "longitude": float,
                  "category": "...", "entrance_fees": float,
                  "municipality_name": "...", "address": "...",
                  "main_image_url": "..." }
            ]
        }

    Returns:
        {
            "success":               true,
            "ordered_stops":         [...],   # with ETA fields
            "total_distance_km":     float,
            "total_entrance_fee":    float,
            "total_duration_minutes": int,
            "end_datetime":          "HH:MM %p",  // when the trip ends
            "time_warning":          str | null,  // set if trip exceeds end_time
            "travel_mode":           str,
            "suggestions":           [...]        // nearby spots NOT in the list
        }
    """
    # if "user" not in session:
    #     return jsonify({"success": False, "error": "Unauthorized"}), 401

    try:
        data = request.get_json(force=True)

        start_lat         = float(data.get("start_lat")  or 14.2)
        start_lng         = float(data.get("start_lng")  or 121.3)
        start_time        = data.get("start_time", "08:00")
        end_time_str      = data.get("end_time", "")          # optional
        date_str          = data.get("date", datetime.today().strftime("%Y-%m-%d"))
        travel_mode       = data.get("travel_mode", "driving").lower()
        manual_order      = bool(data.get("manual_order", False))
        duration_overrides = {str(k): v for k, v in (data.get("duration_overrides") or {}).items()}
        stops             = data.get("stops", [])

        # Resolve speed from travel mode
        speed_kmh = TRAVEL_SPEEDS.get(travel_mode, DEFAULT_SPEED)

        # Keep only stops that have real numeric lat/lng
        def _has_coords(s):
            try:
                lat = s.get("latitude")
                lng = s.get("longitude")
                if lat is None or lng is None:
                    return False
                float(lat)
                float(lng)
                return True
            except (TypeError, ValueError):
                return False

        valid_stops = [s for s in stops if _has_coords(s)]

        if not valid_stops:
            return jsonify({"success": False, "error": "No valid stops provided (missing lat/lng)."}), 400

        # Parse departure datetime
        try:
            departure_dt = datetime.strptime(f"{date_str} {start_time}", "%Y-%m-%d %H:%M")
        except ValueError:
            departure_dt = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)

        # Parse end datetime (optional)
        end_dt = None
        if end_time_str:
            try:
                end_dt = datetime.strptime(f"{date_str} {end_time_str}", "%Y-%m-%d %H:%M")
            except ValueError:
                end_dt = None

        # --- Step 1: Route ordering ---
        if manual_order:
            # User dragged stops into preferred order — respect it
            ordered = valid_stops
        else:
            ordered = nearest_neighbor_sort(start_lat, start_lng, valid_stops)
            ordered = two_opt(ordered, start_lat, start_lng)

        # --- Step 2: Stamp ETAs ---
        ordered = build_timeline(
            ordered, start_lat, start_lng, departure_dt,
            speed_kmh=speed_kmh, duration_overrides=duration_overrides
        )

        # --- Step 3: Aggregate totals ---
        total_dist = sum(s.get("distance_from_prev_km", 0) for s in ordered)
        total_fee  = sum(parse_fee(s.get("entrance_fees")) for s in ordered)
        total_dur  = sum(
            s.get("visit_duration_minutes", 0) + s.get("travel_minutes", 0)
            for s in ordered
        )

        # Determine actual end time of the trip
        trip_end_dt = departure_dt + timedelta(minutes=total_dur + STOP_BUFFER * len(ordered))
        trip_end_str = trip_end_dt.strftime("%I:%M %p")

        # --- Step 4: Check end time constraint ---
        time_warning = None
        if end_dt is not None:
            if trip_end_dt > end_dt:
                overrun_min = int((trip_end_dt - end_dt).total_seconds() / 60)
                hrs_over = overrun_min // 60
                mins_over = overrun_min % 60
                if hrs_over:
                    time_warning = f"This itinerary exceeds your end time by {hrs_over}h {mins_over}m. Consider removing a stop."
                else:
                    time_warning = f"This itinerary exceeds your end time by {mins_over} minutes. Consider removing a stop."
            else:
                spare_min = int((end_dt - trip_end_dt).total_seconds() / 60)
                # Only surface a positive spare-time note if it's notable
                if spare_min >= 30:
                    time_warning = None   # no warning needed, but info could be shown on front-end

        # --- Step 5: Fetch ALL approved spots for suggestion engine ---
        try:
            all_spots_res = (
                supabase.table("tourist_spots")
                .select("id, name, category, latitude, longitude, entrance_fees, main_image_url, description, address, municipality_id")
                .eq("status", "approved")
                .execute()
            )
            all_spots = all_spots_res.data or []

            mun_res = supabase.table("municipalities").select("id, name").execute()
            mun_map = {m["id"]: m["name"] for m in (mun_res.data or [])}
            for sp in all_spots:
                sp["municipality_name"] = mun_map.get(sp.get("municipality_id"), "Laguna")
        except Exception as db_err:
            print(f"[ItineraryController] suggestion fetch error: {db_err}")
            all_spots = []

        suggestions = find_nearby_suggestions(ordered, all_spots, max_suggestions=5, start_time_str=start_time)

        return jsonify({
            "success":                True,
            "ordered_stops":          ordered,
            "total_distance_km":      round(total_dist, 2),
            "total_entrance_fee":     round(total_fee, 2),
            "total_duration_minutes": total_dur,
            "end_datetime":           trip_end_str,
            "time_warning":           time_warning,
            "travel_mode":            travel_mode,
            "suggestions":            suggestions,
        })

    except Exception as e:
        print(f"[ItineraryController] optimize_itinerary error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
