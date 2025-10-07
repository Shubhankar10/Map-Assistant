import requests
import os
from steps import ask_llm,initialize_services

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # Make sure your API key is in your environment

def get_place_details(lat, lon, radius=500):
    nearby_url = (
        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        f"?location={lat},{lon}&radius={radius}&key={GOOGLE_API_KEY}"
    )
    
    nearby_resp = requests.get(nearby_url)
    nearby_data = nearby_resp.json()
    
    if not nearby_data.get('results'):
        return {"error": "No places found near this location."}
    
    # Take the first place found
    place_id = nearby_data['results'][0]['place_id']
    
    # Step 2: Place Details API to get detailed info
    details_url = (
        f"https://maps.googleapis.com/maps/api/place/details/json"
        f"?place_id={place_id}&key={GOOGLE_API_KEY}"
    )
    
    details_resp = requests.get(details_url)
    details_data = details_resp.json()
    
    if details_data.get('status') != 'OK':
        return {"error": "Unable to fetch place details."}
    
    return details_data['result']


from typing import Dict, List, Any

def generate_poi_query(context: Dict[str, Any], use_llm: bool = True) -> Dict[str, List[str]]:
    city = context.get("city", "").strip()
    interests = context.get("interests", []) or ["tourist attractions"]
    days = int(context.get("days", 1) or 1)
    travel_mode = context.get("travel_mode", "walking")
    radius_m = int(context.get("radius_m", 2000))
    poi_per_day = int(context.get("poi_per_day", 4))
    coords = context.get("coords")

    target_pois = days * poi_per_day

    def expand_with_llm(q: str) -> List[str]:
        llm_prompt = (
            "Create 2 concise text-search queries for Google Places "
            f"that capture the same intent as: \"{q}\". "
            "Return them as plain text, each on a separate line."
        )
        initialize_services()
        resp = ask_llm(llm_prompt)
        print("LLM response for query expansion:", resp)
        if not resp:
            return [q]

        if isinstance(resp, list):
            variations = [r.strip() for r in resp if r and r.strip()]
        else:
            variations = [line.strip() for line in str(resp).splitlines() if line.strip()]
        print("Extracted variations:", variations)
        return variations[:2] or [q]

    poi_queries: List[str] = []
    # Base POI queries: one per interest + some general queries
    poi_queries.append(f"Top tourist attractions and Famous landmarks in {city}")
    for interest in interests:
        base = f"Best {interest} in {city}".strip()
        poi_queries.append(expand_with_llm(base))

        #Search nearby fucntion, Abhi milna mushkil hai
        if coords:
            lat, lon = coords
            poi_queries.extend(expand_with_llm(f"Popular {interest} near {lat},{lon} within {radius_m}m"))


    # Trim to a reasonable number of queries to avoid excessive API traffic
    # max_initial_queries = min(12, max(6, int(target_pois / 2)))
    # deduped_poi_queries = deduped_poi_queries[:max_initial_queries]

    #Later, for POI queries, we can use the search_nearby function with coords to get food and other details

    return poi_queries

if __name__ == "__main__":
    # lat = 26.9240458
    # lon = 75.8267144
    # place_info = get_place_details(lat, lon)
    # print(place_info)
    print(generate_poi_query({"city": "Jaipur", "interests": ["historical landmark", "museum"], "days": 3, "travel_mode": "walking", "radius_m": 2000, "poi_per_day": 4, "neighbourhood": "Old City"}))
    
