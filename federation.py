# Orchestrator 
#This has class with Flow Fetching

"""
Base class to make generic federator which can call different APIs based on context and query type.

Input Context from Decomposer
Fetch Flow for the feature, 

Call each step for  the feature in sequence
Manage context with each step
Return final response

Mainly gather data from different APIs and combine them step by step

Last mai execute bhi toh ho he raha hai, final output bhi toh aajayeg steps complete hone ke baad

Federate kar k steps ko context k saath execute ko pass kar sakte
FLOW mai federate steps and execute steps alag rakh sakte hai, toh pehale federate hoke context build ho jayega phir execute hoke final output ayega
--------------------------------------------------------
Orchestrator class often combines both roles
Federation is about “planning”: what steps, in what sequence, which parameters, which branches.

Execution is about “doing”: actually invoking each step, handling outputs, retries, and updating the Context.

"""


"""
Lastly make a user k liye output from the final context.
"""

from typing import List, Any, Dict, Callable, Optional
import inspect

class Orchestrator:
    """
    Generic Orchestrator to run a sequence of step functions for a selected task.
    It manages context, user query, and function inputs automatically.
    """
    
    def __init__(self, selected_task: str, flow: List[str], context: Any, user_query: str):
        """
        Args:
            selected_task: Name of the task (e.g., "ItineraryPlanner", "MeetingPointPlanner")
            flow: List of step function names as strings
            context: Context object (e.g., Pydantic model or dict)
            user_query: Raw user input query
        """
        self.selected_task = selected_task
        self.flow = flow
        self.context = context
        self.user_query = user_query
        
        # Mapping of function names to actual callables
        self.step_registry: Dict[str, Callable] = {}
    
    def register_steps(self, step_functions: Dict[str, Callable]):
        """
        Register available step functions for the orchestrator.
        Args:
            step_functions: Dict mapping function name string -> callable
        """
        self.step_registry.update(step_functions)
    
    def run(self):
        """
        Execute each step in the flow sequentially.
        Automatically passes required arguments from context or user_query.
        """
        for step_name in self.flow:
            if step_name not in self.step_registry:
                raise ValueError(f"Step function '{step_name}' not registered.")
            
            func = self.step_registry[step_name]
            # Inspect function signature
            sig = inspect.signature(func)
            kwargs = {}
            
            for name, param in sig.parameters.items():
                # Determine what to pass to each parameter
                if name == "context":
                    kwargs[name] = self.context
                elif name == "user_query":
                    kwargs[name] = self.user_query
                elif hasattr(self.context, name):
                    kwargs[name] = getattr(self.context, name)
                else:
                    # If parameter not found, pass None or rely on function default
                    kwargs[name] = None
            
            # Call the function and capture return if it modifies context
            result = func(**kwargs)
            
            # If function returns a dict or Pydantic model, merge/update context
            if result is not None:
                if isinstance(result, dict):
                    for k, v in result.items():
                        setattr(self.context, k, v)
                elif hasattr(result, "__dict__"):  # Pydantic or object
                    for k, v in result.__dict__.items():
                        setattr(self.context, k, v)
        
        return self.context

# Example usage with dummy step functions and context
from orch import Orchestrator
from context import MeetingPointContext

# Define step functions
def extract_meeting_query_context(user_query: str, context):
    # Populate some fields in context from query
    context.participants = [{"label": "Me", "address": "Govindpuri, Delhi"}]
    context.cuisine_type = ["Italian"]
    return context

def geocode_participant_addresses(context):
    # Simulate geocoding
    for p in context.participants:
        p["lat"], p["lon"] = 28.527, 77.267
    return context

def generate_candidate_venues(context):
    # Simulate venue generation
    context.venues = [{"name": "Italian Bistro", "lat": 28.530, "lon": 77.270}]
    return context

# Setup orchestrator
context = MeetingPointContext()
flow = [
    "extract_meeting_query_context",
    "geocode_participant_addresses",
    "generate_candidate_venues"
]
orchestrator = Orchestrator(selected_task="MeetingPointPlanner", flow=flow, context=context, user_query="Demo query")
orchestrator.register_steps({
    "extract_meeting_query_context": extract_meeting_query_context,
    "geocode_participant_addresses": geocode_participant_addresses,
    "generate_candidate_venues": generate_candidate_venues
})

final_context = orchestrator.run()
print(final_context)
