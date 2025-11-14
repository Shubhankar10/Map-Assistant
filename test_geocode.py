# test_geocode.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("MAPS_API_KEY")

lat = 28.497467
lon = 77.145285
base_url = "https://maps.googleapis.com/maps/api/geocode/json"
params = {
    "latlng": f"{lat},{lon}",
    "key": API_KEY,
    "result_type": "political|sublocality|locality",
}

try:
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()
    
    print("--- API RESPONSE ---")
    print(data)
    
    if data.get("status") == "OK" and data.get("results"):
        print("\n--- SUCCESS! ---")
        print(f"Address: {data['results'][0]['formatted_address']}")
    else:
        print("\n--- TEST FAILED! ---")
        print(f"Status: {data.get('status')}")
        print(f"Error: {data.get('error_message')}")

except requests.RequestException as e:
    print(f"HTTP Error: {e}")