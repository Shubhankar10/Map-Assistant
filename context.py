"""

BaseContext class for managing general context in the application.
Child Context classes can extend this to add specific context handling.

"""
# Keep context class here
# Set of values needed ton pass in each step like JSON


"""
raw : user query
tokens : tokenized words from the query
cities : list of cities mentioned in the query  
pois : points of interest mentioned in the query
people : list of people mentioned in the query
money : budget mentioned in the query
currency : currency mentioned in the query
days : number of days mentioned in the query
date_spans : list of date spans mentioned in the query
times_of_day : list of times of day mentioned in the query
constraints : any other constraints mentioned in the query

feature : which feature we think this is
confidence : confidence score (0..1)
reasons : human-readable strings for audit/debug
op : operation to be performed (e.g., "FETCH_POI_CANDIDATES")
args : arguments for the operation (JSON-serializable dict)
source : where this step is executed ('llm', 'pois_db', 'engine', 'routing_api', etc.)

from database
user personal preferences
tags


"""

from typing import Optional, List, Dict, Any

try:
    from pydantic import BaseModel, Field
    PydanticBase = BaseModel
except ImportError:
    from dataclasses import dataclass
    PydanticBase = object

# Base
class BaseContext(PydanticBase):
    request_id: Optional[str] = None
    user_id: Optional[str] = None

# Contexts per task
class TripSuggestionContext(BaseContext):
    city: Optional[str]
    days: Optional[int] = 1
    interests: Optional[List[str]] = []
    pace: Optional[str] = "moderate"
    budget: Optional[str] = None

class ItineraryPlannerContext(BaseModel):
    # --- Core trip info ---
    city: str   #Query
    travel_duration: int  # Query
    pace: Optional[str] = "moderate"  # Query : relaxed | moderate | fast

    # --- User preferences ---
    interests: Optional[List[str]] = [] #Query, else DB
    dietary_preferences: Optional[List[str]] = [] # DB
    special_needs: Optional[List[str]] = [] # DB

    # --- Budget & logistics ---
    transport_pref: Optional[str] = None    #DB           # e.g. "train", "flight"
    commute_pref: Optional[str] = None  #DB        # e.g. "walkable", "short drives"
    budget_max: Optional[int] = None    #DB          # in local currency
    accommodation_type: Optional[str] = None    #DB  # e.g. "hotel", "hostel", "villa"

    # --- Activity and location ---
    must_see: Optional[List[str]] = []        # must-visit sites
    start_loc: Optional[str] = None           # starting point, e.g. "airport" or hotel name
    activity_type: Optional[str] = None       # e.g. "sightseeing", "adventure"
    preferred_vacation_type: Optional[str] = None  # e.g. "family", "romantic", "solo"

    # --- Metadata ---
    tag: Optional[str] = None                 # primary tag for categorization
    sub_tag: Optional[str] = None             # sub-category
    special_notes: Optional[str] = None       # any custom notes / constraints

    #APIs POIs
    # poi_candidates: Optional[Dict[str, List[Dict]]] = {} #Make this type later
    
    poi_candidates: Optional[List[Dict[str, Any]]] = {}

# must_see,activity_type,interests,travel_duration,pace,city

class ReviewSummarizerContext(BaseContext):
    poi_id: Optional[str]
    poi_name: Optional[str]
    timeframe: Optional[str] = "all_time"
    sentiment_focus: Optional[str] = "overall"

from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class MeetingPointContext(BaseModel):
    """
    Context model for planning a meeting point between multiple participants.
    Stores participant locations, preferences, constraints, and other metadata.
    """

    # --- Participants ---
    participants: List[Dict] = Field(default_factory=list)
    # Each participant dict can include:
    #   id: Optional[str] = unique identifier
    #   label: Optional[str] = "Me", "Friend", etc.
    #   lat: Optional[float]
    #   lon: Optional[float]
    #   address: Optional[str] = textual address
    #   avoid_long_distance: Optional[bool] = None  # participant-specific

    # --- Transportation and commute preferences ---
    preferred_mode: Optional[str] = "walk"  # "walk", "metro", "car", "bike"
    max_travel_time_minutes: Optional[int] = None  # optional limit per participant
    accessibility_needs: Optional[List[str]] = Field(default_factory=list)
    # e.g., "wheelchair", "avoid stairs"

    # --- Meeting place preferences ---
    cuisine_type: Optional[List[str]] = Field(default_factory=list)  # e.g., ["Italian", "Cafe"]
    venue_type: Optional[List[str]] = Field(default_factory=list)   # e.g., ["restaurant", "cafe"]
    budget_max_per_person: Optional[int] = None
    open_now: Optional[bool] = True
    time_window: Optional[str] = None  # e.g., "7 PM - 9 PM"

    # --- Constraints for optimization ---
    central_location_priority: Optional[bool] = True  # prefer midpoint locations

    # --- Metadata / extra info ---
    tag: Optional[str] = None
    sub_tag: Optional[str] = None
    special_notes: Optional[str] = None


class RouteOptimizerContext(BaseContext):
    origin: Dict  # {lat, lon, label?}
    destinations: List[Dict]  # [{lat, lon, label?}, ...]
    constraints: Optional[Dict] = {}

class TripJournalContext(BaseContext):
    user_id: Optional[str]
    trip_id: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    tags: Optional[List[str]] = []

