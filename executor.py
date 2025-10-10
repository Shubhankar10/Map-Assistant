from typing import List, Dict, Callable, Any
from context import ItineraryPlannerContext
from steps import (
    generate_poi_query,
    get_places_for_queries,
    ask_llm
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

            # Execute
            # resp = execute_sql(sql)

            # map_to_context(context,db_resp)


            # API DB
            # Federate
            queries = generate_poi_query(itinerary_data)
            print("--------------------------------------------------------------------------------------")
            print(queries)
            # Execute
            # self.context.poi_candidates = get_places_for_queries(queries)
            
            #Integrate
            # final = ask_llm("Plan me a detailed itinerary with the following data:\n" + str(self.context) + "\nUser Query:\n" + self.user_query)
            final = ""
            return final
        

        elif self.selected_task == "MeetingPointPlanner":
            # Implement execution logic for MeetingPointPlanner
            pass
