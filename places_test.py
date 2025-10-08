from typing import Dict, List, Any
from steps import generate_poi_query,get_places_for_queries,filter_pois

if __name__ == "__main__":
    
    itinerary_data = {
        "city":"Jaipur",
        "travel_duration": "3",
        "pace": "moderate",
        "interests": ["history", "architecture", "local cuisine"],
        "must_see": ["Amer Fort", "City Palace", "Jantar Mantar", "Hawa Mahal", "Nahargarh Fort"],
        "activity_type": ["cultural", "historical"],
    }

    queries = generate_poi_query(itinerary_data)

    for q in queries:
        print(q)
    
    pois = get_places_for_queries(queries)
    print(f"[IN TEST]Total POIs fetched: {len(pois)}")
    # for p in pois:
    #     print(p)
    #     print()

    # filterd = filter_pois(pois)
    # print(f"[IN TEST]Total POIs after filtering: {len(filterd)}")
    
    # for p in filterd:
    #     print(p)
    #     print()

    
