import requests
import os

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # Make sure your API key is in your environment

def get_place_details(lat, lon, radius=500):
    """
    Given latitude and longitude, return details of the place at that location.
    
    Args:
        lat (float): Latitude of the location
        lon (float): Longitude of the location
        radius (int): Search radius in meters (default 50m)
    
    Returns:
        dict: Place details including name, address, place_id, types, etc.
    """
    
    # Step 1: Nearby Search to get place_id
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

# Example usage:
if __name__ == "__main__":
    lat = 26.9240458
    lon = 75.8267144
    place_info = get_place_details(lat, lon)
    print(place_info)
