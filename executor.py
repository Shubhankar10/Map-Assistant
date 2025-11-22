from typing import List, Dict, Callable, Any
from context import ItineraryPlannerContext
from steps import (
    generate_poi_query,
    get_places_for_queries,
    ask_llm,
    add_demo_data,
    extract_data_from_user_profile,
    populate_context_from_user_profile
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
            # Implement execution logic for MeetingPointPlanner
            pass
