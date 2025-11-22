from typing import List, Dict, Callable, Any
import json
from context import ItineraryPlannerContext
from steps import (
    # Itenarary Planner Steps
    generate_poi_query,
    get_places_for_queries,
    ask_llm,
    add_demo_data,
    extract_data_from_user_profile,
    populate_context_from_user_profile,

    # Meeting Point Planner Steps
    fetch_participant_details,
    geocode_participants,
    calculate_midpoint,
    get_midpoint_area_name,
    generate_meeting_poi_query,
    get_travel_details_for_venues,
    filter_venues_by_travel_time,
    populate_meeting_context_from_user_profile
)

class NewExecute:
    def __init__(self, context: Any, user_query: str):
        self.context = context
        self.user_query = user_query

    def execute(self):
        
        user_id = add_demo_data()
        print("[EXECUTER] Demo Data Added.")
        user_profile = extract_data_from_user_profile(user_id)
        print("[EXECUTER] User Profile Fetched.")
        print(user_profile)
            
        print("[EXECUTER] ", self.context.keys())
        print("[EXECUTER]", user_profile.keys())

        #     populate_context_from_user_profile(self.context,user_profile)
        #     print("[EXECUTER] Context Filled.")

        #     print("[EXECUTER] Making POI Queries for API.")
        #     queries = generate_poi_query(self.context)
        #     # print("--------------------------------------------------------------------------------------")
        #     print(queries)

        #     # Execute
        #     print("[EXECUTER] Getting POIs using API.")
        #     self.context.poi_candidates = get_places_for_queries(queries)
            
        #     #Integrate
        #     print("[EXECUTER] Final LLM Call.")
        #     final = ask_llm("Plan me a detailed itinerary with the following data:\n" + str(self.context) + "\nUser Query:\n" + self.user_query)

        #     return final
        
