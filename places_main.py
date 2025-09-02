import requests
from typing import List, Optional
from apis.places_api import GooglePlacesClient


from dotenv import load_dotenv
import os
load_dotenv()

def main():
    # Replace with your actual API key
    client = GooglePlacesClient(api_key=os.getenv("MAPS_API_KEY"))

    # Example 1: Find cafes near Connaught Place (Delhi)
    cafes = client.search_nearby(lat=28.6315, lon=77.2167, radius=800, place_type="cafe")
    print("Nearby Cafes:", cafes[:2])  # just show 2 results

    # Example 2: Text search
    pizza_places = client.text_search("best pizza in Bangalore")
    print("Pizza Search:", pizza_places[:2])

    # Example 3: Place details
    if cafes:
        place_id = cafes[0]["id"]
        details = client.get_place_details(place_id)
        print("Details of first cafe:", details)


if __name__ == "__main__":
    main()