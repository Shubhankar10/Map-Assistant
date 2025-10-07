from apis.llm_api import LLMClient
from main_dbconnect import initalize_db
from apis.places_api import GooglePlacesClient
from db.baseDB import PostgresDB

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


def fetch_user_preferences(user_id: str):
    
    _ensure_db_client()

    print("[Steps : fetch_user_preferences] Fetching user preferences...")
    # Simulate fetching user preferences
    print("USer ID:", user_id)
    user_preferences = _db_client.get_prefs_by_user(user_id)
    print("[Steps : fetch_user_preferences] User preferences fetched.")
    
    return user_preferences


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


# 2️⃣ Function: Reverse lookup from coordinates → name + details
def reverse_lookup(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    _ensure_client(_places_api_client)

    results = _places_api_client.search_nearby(lat=lat, lon=lon, radius=50)  # small radius for precision
    if not results:
        return None

    first = results[0]
    place_id = first.get("place_id") or first.get("id")
    if not place_id:
        return first

    details = _places_api_client.get_place_details(place_id)
    return details or first


# 3️⃣ Function: Search nearby using a place name (not lat/lon)
def search_nearby_by_name(client,place_name: str,radius: int = 1000,place_type: Optional[str] = None,limit: int = 10) -> List[Dict[str, Any]]:
    _ensure_client(client)

    coords = get_location_for_place(client, place_name)
    if not coords:
        print(f"[WARN] Could not resolve location for '{place_name}'")
        return []

    lat, lon = coords
    results = client.search_nearby(lat=lat, lon=lon, radius=radius, place_type=place_type)
    if not isinstance(results, list):
        results = results.get("results", []) if isinstance(results, dict) else []

    return results[:limit]

initialize_services()
ask_llm("Hello, how are you?")
