from apis.llm_api import LLMClient
from apis.places_api import GooglePlacesClient
from db.baseDB import PostgresDB
from typing import Dict, List, Any,Optional, Tuple

from uuid import uuid4


# Move to init ---------------------------------------------------------------------------
from dotenv import load_dotenv  
import os
load_dotenv()

# Global variables to hold initialized clients
_llm_client = None
_places_api_client = None
_db_client = None


# Port
DB_HOST = "10.144.192.33"  
DB_NAME = "map_assistant" 
DB_USER = "postgres"
DB_PASSWORD = "1214" 
DB_SCHEMA = "public"

# Shubhankar Local
# DB_HOST = "localhost"
# DB_NAME = "Try"
# DB_USER = "postgres"
# DB_PASSWORD = "jojo"
# DB_SCHEMA = "mapassitant"

def initialize_llm_client():
    global _llm_client
    _llm_client = LLMClient(api_key=os.getenv("LLM_API_KEY"))
    return _llm_client

def initialize_places_client():
    global _places_api_client
    _places_api_client = GooglePlacesClient(api_key=os.getenv("MAPS_API_KEY"))
    return _places_api_client

def initialize_db_client():
    global _db_client
    _db_client = PostgresDB(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    _db_client.connect(schema=DB_SCHEMA)
    print("[Steps] CONNECTED TO HOST.")
    return _db_client

def initialize_services():
    global _llm_client, _places_api_client, _db_client

    initialize_llm_client()
    print("[Initializer] LLMClient initialized.")

    initialize_places_client()
    print("[Initializer] GooglePlacesClient initialized.")

    initialize_db_client()
    print("[Initializer] PostgresDB client initialized.")

    print("[Initializer] All services initialized successfully.\n")




#LLM STEPS --------------------------------------------------------------------------------------------------

def ask_llm(query: str) -> str:
    global _llm_client
    if _llm_client is None:
        initialize_llm_client()

    print("[Steps : ask_llm] Sending query to LLM...")
    response = _llm_client.query(query)
    print("[Steps : ask_llm] LLM response received.")
    return response

    user_preferences = db.get_prefs_by_user(user_id)



#DB STEPS --------------------------------------------------------------------------------------------------

def add_demo_data():
    if _db_client is None:
        initialize_db_client()
    _db_client.clear_all()
    new_user = _db_client.add_user(
        first_name="Rohan",
        last_name="Sharma",
        email="rohan.sharma@studentemail.com",
        password_hash="hashed_password_here"
    )
    user_id = new_user['user_id']

    user_details = _db_client.add_user_details(
        user_id=user_id,
        dob="2001-08-20",
        gender="Male",
        aadhar_number="1111-2222-3333",
        passport_number="P1234567",
        driving_license_number="DL9876543210",
        spoken_languages=["English", "Hindi"],
        understood_languages=["English", "Hindi"],
        native_language="Hindi",
        hometown="Delhi",
        current_city="Delhi",
        address="45 Student Hostel, Delhi University",
        phone_number="+911234567891",
        home_lat=28.6139,
        home_lng=77.2090,
        dietary_preferences=["Vegetarian", "No Spicy"]
    )

    travel_pref = _db_client.add_travel_preference(
        user_id=user_id,
        budget_min=500.00,
        budget_max=3000.00,
        transport_pref="Train",
        commute_pref="Public Transport",
        pace="Relaxed",
        travel_duration_preference="2-5 days",
        travel_group_preference="Solo/Group",
        preferred_regions=["Rajasthan", "Uttar Pradesh", "Madhya Pradesh"],
        season_preference="Winter",
        accommodation_type="Hostel/Guesthouse",
        special_needs=None,
        frequent_travel=True
    )

    interests = [
        {
            "tag": "Culture",
            "sub_tag": "Heritage Sites",
            "preferred_vacation_type": "City Break",
            "activity_type": "Sightseeing",
            "frequency_of_interest": "Often",
            "special_notes": "Likes historical monuments"
        },
        {
            "tag": "Food",
            "sub_tag": "Street Food",
            "preferred_vacation_type": "City Break",
            "activity_type": "Culinary Tour",
            "frequency_of_interest": "Sometimes",
            "special_notes": "Prefers vegetarian options"
        }
    ]

    for interest in interests:
        _db_client.add_user_interest(
            user_id=user_id,
            tag=interest["tag"],
            sub_tag=interest["sub_tag"],
            preferred_vacation_type=interest["preferred_vacation_type"],
            activity_type=interest["activity_type"],
            frequency_of_interest=interest["frequency_of_interest"],
            special_notes=interest["special_notes"]
        )

    print(f"Demo data added for user_id: {user_id}")
    return user_id

def extract_data_from_user_profile(user_id : str):
    if _db_client is None:
        initialize_db_client()
    user_profile = _db_client.get_full_profile(user_id)
    return user_profile

def populate_context_from_user_profile(context, user_profile: dict):
    """
    Fill missing fields in ItineraryPlannerContext using the provided user_profile.
    
    Args:
        context: ItineraryPlannerContext object with some fields possibly empty or None.
        user_profile: Dictionary containing 'user', 'details', 'preferences', 'interests'.
        
    Returns:
        context: Updated ItineraryPlannerContext object with missing fields filled from profile.
    """
    # 1️⃣ Normalize user profile (convert Decimals and other types)
    details = user_profile.get("details") or {}
    preferences = user_profile.get("preferences") or {}
    interests_list = user_profile.get("interests") or []

    # Flatten interests to just strings (tags + sub_tags)
    interests_from_profile = []
    for interest in interests_list:
        tag = interest.get("tag")
        sub_tag = interest.get("sub_tag")
        if tag:
            interests_from_profile.append(tag)
        if sub_tag:
            interests_from_profile.append(sub_tag)

    # 2️⃣ Fill context fields sequentially if empty or None
    if not context.city and details.get("current_city"):
        context.city = details.get("current_city")

    if not context.travel_duration and preferences.get("travel_duration_preference"):
        # Extract numeric days from string like "2-5 days", use average
        duration_str = preferences.get("travel_duration_preference")
        try:
            parts = [int(s) for s in duration_str.split() if s.isdigit()]
            if len(parts) == 2:
                context.travel_duration = sum(parts) // 2
            elif len(parts) == 1:
                context.travel_duration = parts[0]
        except Exception:
            context.travel_duration = 3  # default if parsing fails

    if not context.pace and preferences.get("pace"):
        context.pace = preferences.get("pace").lower()

    if not context.interests:
        context.interests = list(set(context.interests or [] + interests_from_profile))

    if not context.dietary_preferences and details.get("dietary_preferences"):
        context.dietary_preferences = details.get("dietary_preferences")

    if not context.special_needs and preferences.get("special_needs"):
        context.special_needs = [preferences.get("special_needs")] if preferences.get("special_needs") else []

    if not context.transport_pref and preferences.get("transport_pref"):
        context.transport_pref = preferences.get("transport_pref")

    if not context.commute_pref and preferences.get("commute_pref"):
        context.commute_pref = preferences.get("commute_pref")

    if not context.budget_max and preferences.get("budget_max"):
        context.budget_max = int(preferences.get("budget_max"))

    if not context.accommodation_type and preferences.get("accommodation_type"):
        context.accommodation_type = preferences.get("accommodation_type")

    if not context.activity_type and interests_list:
        # pick first activity_type from interests
        first_activity = interests_list[0].get("activity_type")
        if first_activity:
            context.activity_type = first_activity

    if not context.preferred_vacation_type and interests_list:
        first_vacation_type = interests_list[0].get("preferred_vacation_type")
        if first_vacation_type:
            context.preferred_vacation_type = first_vacation_type

    return context

#API STEPS --------------------------------------------------------------------------------------------------

def generate_poi_query(itinerary_data: Any) -> Dict[str, List[str]]:
    
    if _places_api_client is None:
        initialize_places_client()

    city = itinerary_data.get("city")
    travel_duration = itinerary_data.get("travel_duration")
    pace = itinerary_data.get("pace")
    interests = itinerary_data.get("interests")
    must_see = itinerary_data.get("must_see")
    activity_type = itinerary_data.get("activity_type")

    poi_per_day = 4 if pace == "fast" else 3 if pace == "moderate" else 2
    target_pois = travel_duration * poi_per_day
    
    if not city:
        raise ValueError("City is required to generate POI queries.")

    poi_queries: List[str] = []
    poi_queries.append(f"Top tourist attractions and Famous landmarks in {city}")
    if interests:
        for interest in interests:
            base = f"Best places for tourists to enjoy {interest} of the {city}".strip()
            poi_queries.append(base)

    if activity_type:
        for act in activity_type:
            base = f"Popular {act} places in {city}".strip()
            poi_queries.append(base)

    if must_see:
        for place in must_see:
            base = f"Details about {place} in {city}, and nearby POIs".strip()
            poi_queries.append(base)


    # def expand_with_llm(q: str) -> List[str]:
    #     llm_prompt = (
    #         "Create 2 concise text-search queries for Google Places "
    #         f"that capture the same intent as: \"{q}\". "
    #         "Return them as plain text, each on a separate line."
    #     )
    #     initialize_services()
    #     resp = ask_llm(llm_prompt)
    #     print("LLM response for query expansion:", resp)
    #     if not resp:
    #         return [q]

    #     if isinstance(resp, list):
    #         variations = [r.strip() for r in resp if r and r.strip()]
    #     else:
    #         variations = [line.strip() for line in str(resp).splitlines() if line.strip()]
    #     print("Extracted variations:", variations)
    #     return variations[:2] or [q]

        #Search nearby fucntion, Abhi milna mushkil hai
        # if coords:
        #     lat, lon = coords
        #     poi_queries.extend(expand_with_llm(f"Popular {interest} near {lat},{lon} within {radius_m}m"))


    # Trim to a reasonable number of queries to avoid excessive API traffic
    # max_initial_queries = min(12, max(6, int(target_pois / 2)))
    # deduped_poi_queries = deduped_poi_queries[:max_initial_queries]

    #Later, for POI queries, we can use the search_nearby function with coords to get food and other details

    return poi_queries


def extract_data_from_api_response(place):
    extracted_data = {
        "name": place.get("displayName", {}).get("text", "Unknown Place"),
        "address": place.get("shortFormattedAddress", "Address not available"),
        "place_id": place.get("id", ""),
        "types": place.get("types", []),
        "location": place.get("location", {"latitude": None, "longitude": None}),
        "review": place.get("reviewSummary", {}).get("text", "No reviews available"),
        "rating": place.get("rating", 0.0),
        #Add maps url later, for UI
    }
    # print("Extracted Data:", extracted_data)
    return extracted_data


def get_places_for_queries(queries: List[str]) -> List[Dict[str, Any]]:
    
    if _places_api_client is None:
        initialize_places_client()

    all_places = []
    seen_names = set()

    for count, q in enumerate(queries, start=1):
        print(f"[Steps : get_places_for_queries] Searching places for query {count}: '{q}'")
        places = _places_api_client.text_search(q)
        
        for p in places:
            extracted = extract_data_from_api_response(p)
            name = extracted.get("name", "").strip()
            if not name:
                continue 
            if name not in seen_names:
                seen_names.add(name)
                all_places.append(extracted)
                # print("Added unique place:", name)

        # print(f"[Steps : get_places_for_queries] Found {len(places)} places for query: '{q}'")

    print(f"[Steps : get_places_for_queries] Total unique places collected: {len(all_places)}")
    return all_places


def get_location_for_place(place_name: str) -> Optional[Tuple[float, float]]:
    
    if _places_api_client is None:
        initialize_places_client()

    if not place_name.strip():
        raise ValueError("place_name cannot be empty")

    results = _places_api_client.text_search(place_name)
     # no json.loads needed
    place_data = results[0]
    # print("Place data:", place_data)
    location_data = place_data.get("location")
    lat = location_data.get("latitude")
    lon = location_data.get("longitude")
    print("Location data:", location_data.get("latitude"))

    # if isinstance(location_data, list):
    #     print(location_data[:5])
    # elif isinstance(location_data, str):
    #     print("\n".join(location_data.splitlines()[:5]))
    # else:
    #     print(location_data)


    # with open("places.txt", "w") as f:
    #     f.write(str(results))

    # print("Results from text_search:", results)
    if not results:
        return None

    # first = results[0]
    # loc = first.get("geometry", {}).get("location")
    # if not loc:
    #     return None

    # lat, lon = loc.get("lat"), loc.get("lng")
    print("Extracted lat/lon:", lat, lon)
    return (lat, lon)

