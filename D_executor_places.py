# executor_places.py
from apis.places_api import GooglePlacesClient
from steps import get_places_for_queries,extract_data_from_api_response


class ExecutorPlaces:
    def __init__(self, queries: list):
        self.queries = queries


    # def run(self):
    #     print("\n[ExecutorPlaces] Starting execution...\n")
    #     print("[ExecutorPlaces] Received Queries:")
    #     print("\n[ExecutorPlaces] Queries: ", self.queries)
    #     print("\n[ExecutorPlaces] Fetching places from API...\n")

    #     places = get_places_for_queries(self.queries)

    #     print("\n=========== EXECUTED PLACE RESULTS ===========\n")
    #     for idx, place in enumerate(places, start=1):
    #         print(f"#{idx}: {place.get('name', 'Unknown')}")
    #         print(f"   Address   : {place.get('address', 'N/A')}")
    #         print(f"   Place ID  : {place.get('place_id', '')}")
    #         print(f"   Types     : {', '.join(place.get('types', []))}")
    #         loc = place.get("location", {})
    #         print(f"   Location  : lat={loc.get('latitude')}  lng={loc.get('longitude')}")
    #         print(f"   Rating    : {place.get('rating', 'N/A')}")
    #         print(f"   Review    : {place.get('review', 'No reviews')}")
    #         print("-------------------------------------------------\n")

    #     print(f"[ExecutorPlaces] Total Places Returned: {len(places)}\n")
    #     print("[ExecutorPlaces] Execution completed.\n")

    #     return places
    def extract_place_data(self,place: dict) -> dict:

        name = place.get("name", "Unknown Place")
        address = place.get("address", "Address not available")
        place_id = place.get("place_id", "")
        types = place.get("types", [])
        location = place.get("location", {})
        rating = place.get("rating", None)

        # Review summary handling (API format: {'text': "...", 'languageCode': "en"})
        review_obj = place.get("review", {})
        review_text = (
            review_obj[0].get("text") if isinstance(review_obj, list) and review_obj else
            review_obj.get("text") if isinstance(review_obj, dict) else
            "No reviews available"
        )

        extracted = {
            "name": name,
            "address": address,
            "place_id": place_id,
            "types": types,
            "lat": location.get("latitude"),
            "lng": location.get("longitude"),
            "rating": rating,
            "review": review_text
        }

        return extracted

    def run(self):
        print("\n[ExecutorPlaces] Starting execution...\n")

        # Ensure queries are valid list of strings
        print("[ExecutorPlaces] Queries:", self.queries)

        print("\n[ExecutorPlaces] Fetching places from API...\n")

        # Fetch raw places from the Places API wrapper
        raw_places = get_places_for_queries(self.queries)

        print(raw_places)
        print(f"\n[ExecutorPlaces] Raw API returned {len(raw_places)} places.")
        print("[ExecutorPlaces] Extracting relevant fields...\n")

        extracted_results = []
        seen_ids = set()
        seen_names = set()

        for place in raw_places:
            extracted = self.extract_place_data(place)

            place_id = extracted.get("place_id", "").strip()
            name = extracted.get("name", "").strip()

            # Skip invalid or nameless entries
            if not name:
                continue

            # Deduplicate by place_id and name
            dedupe_key = (place_id, name.lower())
            if dedupe_key in seen_ids or name.lower() in seen_names:
                continue

            seen_ids.add(dedupe_key)
            seen_names.add(name.lower())
            extracted_results.append(extracted)

        # # Print nicely formatted results
        # print("\n=========== FINAL UNIQUE EXTRACTED PLACES ===========\n")
        # for idx, p in enumerate(extracted_results, start=1):
        #     print(f"#{idx}: {p.get('name')}")
        #     print(f"   Address   : {p.get('address')}")
        #     print(f"   Place ID  : {p.get('place_id')}")
        #     print(f"   Types     : {', '.join(p.get('types', []))}")
        #     loc = p.get("location", {})
        #     print(f"   Location  : lat={loc.get('latitude')}  lng={loc.get('longitude')}")
        #     print(f"   Rating    : {p.get('rating')}")
        #     print(f"   Review    : {p.get('review')}")
        #     print("-------------------------------------------------------\n")

        # # print(extracted_results)
        # print(f"[ExecutorPlaces] Total unique extracted places: {len(extracted_results)}")
        # print("[ExecutorPlaces] Execution completed.\n")

        return extracted_results



# -----------------------------------------------------------
# MAIN FUNCTION (TESTING)
# -----------------------------------------------------------
if __name__ == "__main__":


    sample_queries = [
        "Top tourist places in Jaipur",
        "Nearby cafes to India Gate",
        "Popular attractions in Mumbai"
    ]

    executor = ExecutorPlaces(sample_queries)
    output = executor.run()

    print("\n=== FINAL EXECUTION OUTPUT ===")
    for item in output:
        print(item)
