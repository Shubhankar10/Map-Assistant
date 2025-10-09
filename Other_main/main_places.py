from apis.places_api import GooglePlacesClient



from steps import (get_location_for_place,extract_data_from_apiresponse)
# from places_client import GooglePlacesClient

from dotenv import load_dotenv
import os
load_dotenv()

def main_old():
    client = GooglePlacesClient(api_key=os.getenv("MAPS_API_KEY"))

    # Example 1: Find cafes near Connaught Place (Delhi)
    # cafes = client.search_nearby(lat=28.6315, lon=77.2167, radius=800, place_type="cafe")
    # print("Nearby Cafes:", cafes[:1])  # just show 2 results

    # Example 2: Text search
    pizza_places = client.text_search("Best Tourist Places in Jaipur")
    # print("Pizza Search:", pizza_places.get('display_name'))
    print(len(pizza_places))
    for place in pizza_places:
        print(place["displayName"]["text"])
        print()
        extract_data_from_apiresponse(place)
    # with open("places.txt", "w", encoding="utf-8") as f:
    #     f.write(str(pizza_places))
    # import json
    # with open("places.txt", "w", encoding="utf-8") as f:
    #     json.dump(pizza_places, f, ensure_ascii=False, indent=2)
    



    # Example 3: Place details
    # if cafes:
    #     place_id = cafes[0]["id"]
    #     details = client.get_place_details(place_id)
    #     # print("Details of first cafe:", details)


def main():
    # 1) Get coordinates for a landmark
    coords = get_location_for_place("Hawa Mahal Jaipur")
    print("Hawa Mahal coords:", coords)

    # 2) Reverse lookup
    if coords:
        details = reverse_lookup(lat=coords[0], lon=coords[1])
        print("Reverse lookup details:", {
            "name": details.get("name"),
            "address": details.get("formatted_address")
        })

    # # 3) Search nearby (by place name)
    # nearby = search_nearby_by_name(client, "Hawa Mahal Jaipur", place_type="restaurant", radius=800)
    # print("Restaurants near Hawa Mahal:", [r["name"] for r in nearby[:3]])


if __name__ == "__main__":
    # main()
    main_old()