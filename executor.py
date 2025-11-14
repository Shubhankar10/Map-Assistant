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

class Execute:
    def __init__(self, selected_task: str, flow: List[str], context: Any, user_query: str):
        """
        Initialize the executor with the selected task, flow, context, and user query.
        Args:
            selected_task: Name of the selected task (e.g., "MeetingPointPlanner")
            flow: List of step function names as strings
            context: Context object (e.g., Pydantic model or dict)      
        """
        self.selected_task = selected_task
        self.flow = flow
        self.context = context
        self.user_query = user_query

    def execute(self):
        
        if self.selected_task == "ItineraryPlanner":
            itinerary_data = {
                "city": self.context.city,
                "travel_duration": self.context.travel_duration,
                "pace": self.context.pace,
                "interests": self.context.interests,
                "must_see": self.context.must_see,
                "activity_type": self.context.activity_type,
            }
            print("[MAIN] Itinerary Data prepared.")
            
            # User DB
            # Federate
            user_id = add_demo_data()
            print("[EXECUTER] Demo Data Added.")
            user_profile = extract_data_from_user_profile(user_id)
            print("[EXECUTER] User Profile Fetched.")

            # Execute
            populate_context_from_user_profile(self.context,user_profile)
            print("[EXECUTER] Context Filled.")


            # API DB
            # Federate
            
            print("[EXECUTER] Making POI Queries for API.")
            queries = generate_poi_query(itinerary_data)
            # print("--------------------------------------------------------------------------------------")
            print(queries)

            # Execute
            print("[EXECUTER] Getting POIs using API.")
            self.context.poi_candidates = get_places_for_queries(queries)
            
            #Integrate
            print("[EXECUTER] Final LLM Call.")
            final = ask_llm("Plan me a detailed itinerary with the following data:\n" + str(self.context) + "\nUser Query:\n" + self.user_query)

            return final
        

        elif self.selected_task == "MeetingPointPlanner":
            print("[EXECUTER] Starting MeetingPointPlanner workflow.")

            # --- THIS BLOCK NOW MATCHES THE ITINERARYPLANNER ---
            # Step 1: User DB (Federate)
            user_id = add_demo_data()
            print("[EXECUTER] Demo Data Added.")
            user_profile = extract_data_from_user_profile(user_id)
            print("[EXECUTER] User Profile Fetched.")
            
            # Step 1a: Fill participant "Me" address from DB
            fetch_participant_details(self.context, user_profile) # <-- Pass user_profile
            print("[EXECUTER] Fetched participant details.")

            # Step 1b: Fill context preferences (cuisine, budget) from DB
            populate_meeting_context_from_user_profile(self.context, user_profile) # <-- CALL NEW FUNCTION
            print("[EXECUTER] Context Filled.")
            # --- END OF UPDATED DB LOGIC ---
            
            # Step 2: Geocoding (Execute)
            geocode_participants(self.context)
            print("[EXECUTER] Geocoded participant addresses.")

            # Step 3: Calculate Midpoint (Execute)
            midpoint = calculate_midpoint(self.context.participants)
            if not midpoint:
                return "I couldn't find the locations for the participants. Please provide their starting addresses."
            print("[EXECUTER] Calculated search midpoint.")

            print("[EXECUTER] Finding name of midpoint area...")
            midpoint_area_name = get_midpoint_area_name(midpoint)
            print(f"[EXECUTER] Midpoint area is: {midpoint_area_name}")
            
            # Step 4: API DB (Federate)
            print("[EXECUTER] Making POI Queries for API.")
            queries = generate_meeting_poi_query(self.context, midpoint, midpoint_area_name) # <-- PASS IT HERE
            print(queries)

            # Step 5: API DB (Execute)
            print("[EXECUTER] Getting POIs using API.")
            poi_candidates = get_places_for_queries(queries)
            if not poi_candidates:
                return "I found a central spot, but couldn't find any venues that match your criteria (like cuisine or venue type) nearby."

            # Step 6: Data Enrichment (Execute)
            print("[EXECUTER] Annotating venues with travel times.")
            annotated_venues = get_travel_details_for_venues(poi_candidates, self.context)

            # Step 7: Filtering (Execute)
            print("[EXECUTER] Filtering venues by constraints...")
            filtered_venues = filter_venues_by_travel_time(annotated_venues, self.context)
            if not filtered_venues:
                return "I found some venues, but unfortunately, none of them fit your travel time constraints for all participants."

            # Step 8: Integration (Final LLM Call)
            print("[EXECUTER] Final LLM Call.")
            
            final_context_data = self.context.model_dump()
            final_context_data['filtered_venues_with_travel'] = filtered_venues
            final_context_data['midpoint_area_name'] = midpoint_area_name

            # Using your new prompt
            final_prompt = (
                f"You are an expert meeting planner. Your goal is to find the best 7-8 meeting points from the 'filtered_venues_with_travel' list. The calculated central meeting area is near **{midpoint_area_name}**.\n" 
                "Follow these rules to make your recommendation:\n\n"
                "1.  **Check for Constraints:** First, check the 'Full Context & Candidates' for any participant constraints (like 'avoid_long_distance: true' or 'max_travel_time_minutes'). Always prioritize suggestions that respect these hard constraints.\n"
                "2.  **Prioritize Fairness (Default):** If no specific constraints are given (like in this query), your **primary goal** is to find the venue with the most **equal and fair travel time** for all participants. Find the spot where the travel times are closest to each other.\n"
                "3.  **Explain Your Choice:** For each suggestion, clearly explain *why* you chose it. Show the travel time and mode for *each* participant (e.g., 'I recommend Venue A because it's a great compromise: 30 mins drive for Me and 35 mins by metro for your Friend.').\n\n"
                
                f"--- User Query:\n{self.user_query}\n\n"
                f"--- Full Context & Candidates:\n{json.dumps(final_context_data, indent=2)}\n\n"
            )
            
            final = ask_llm(final_prompt)
            return final