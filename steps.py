from apis.llm_api import LLMClient
from main_dbconnect import initalize_db
from apis.places_api import GooglePlacesClient
from db.baseDB import PostgresDB
from typing import Dict, List, Any
from dotenv import load_dotenv  
import os
load_dotenv()

# Global variables to hold initialized clients
_llm_client = None
_places_api_client = None
_db_client = None



_db_client = None

def _ensure_db_client():
    global _db_client
    if _db_client is None:
        from main_dbconnect import initalize_db 
        _db_client = initalize_db()

def initialize_services():
    global _llm_client, _places_api_client, _db_client

    print("[Initializer] Initializing all services...")

    # Initialize LLM
    #Jab bhi new LLM client use karna ho to ye line copy karna bas
    _llm_client = LLMClient(api_key=os.getenv("LLM_API_KEY"))
    print("[Initializer] LLMClient initialized.")

    # TODO: Initialize your API client(s)


    # TODO: Initialize your DB client
    # _db_client = initalize_db()

    print("[Initializer] All services initialized successfully.")


def ask_llm(query: str) -> str:
    
    global _llm_client
    if _llm_client is None:
        raise RuntimeError("LLMClient not initialized. Call initialize_services() first.")

    print("[Steps : ask_llm] Sending query to LLM...")
    response = _llm_client.query(query)
    print("[Steps : ask_llm] LLM response received.")
    return response

    user_preferences = db.get_prefs_by_user(user_id)

#DB STEPS --------------------------------------------------------------------------------------------------
def fetch_user_preferences(user_id: str):
    
    _ensure_db_client()

    print("[Steps : fetch_user_preferences] Fetching user preferences...")
    # Simulate fetching user preferences
    print("USer ID:", user_id)
    user_preferences = _db_client.get_prefs_by_user(user_id)
    print("[Steps : fetch_user_preferences] User preferences fetched.")
    
    return user_preferences


#API STEPS --------------------------------------------------------------------------------------------------





def generate_poi_query(itinerary_data: dict) -> Dict[str, List[str]]:
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

# def get_places_for_queries(queries: List[str]) -> List[str]:
#     _places_api_client = GooglePlacesClient(api_key=os.getenv("MAPS_API_KEY"))

#     # all_places: Dict[str, List[Dict[str, Any]]] = {}
#     all_places = []

#     count = 0
#     for q in queries:
#         print(f"[Steps : get_places_for_queries] Searching places for query {count+1}: '{q}'")
#         count += 1
#         places = _places_api_client.text_search(q)
#         for p in places:
#             print("Extracting place data for:", p.get("displayName", {}).get("text", "Unknown"))
#             all_places.append(extract_data_from_api_response(p))

#         print(f"[Steps : get_places_for_queries] Found {len(places)} places for query: '{q}'")
#     return all_places

from typing import List, Dict, Any
import os

def get_places_for_queries(queries: List[str]) -> List[Dict[str, Any]]:
    _places_api_client = GooglePlacesClient(api_key=os.getenv("MAPS_API_KEY"))
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


def filter_pois(pois: List[Dict[str, Any]]) -> List[str]:
    
    seen_names = set()
    unique_pois = []

    for poi in pois:
        name = poi.get("name", "").strip()
        if not name:
            continue  # skip POIs without a valid name
        if name not in seen_names:
            seen_names.add(name)
            unique_pois.append(poi)

    return unique_pois

# steps_places.py
from typing import Optional, Dict, Any, List, Tuple

# from places_client import GooglePlacesClient  # Import your real client

def _ensure_client(client):
    global _places_api_client
    if _places_api_client is None:
        _places_api_client = GooglePlacesClient(api_key=os.getenv("MAPS_API_KEY"))


# 1️⃣ Function: Get lat/lon for a place name (e.g. "Hawa Mahal Jaipur")
def get_location_for_place(place_name: str) -> Optional[Tuple[float, float]]:
    
    _places_api_client = GooglePlacesClient(api_key=os.getenv("MAPS_API_KEY"))

    _ensure_client(_places_api_client)
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

