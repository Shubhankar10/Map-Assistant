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

from typing import Optional, List, Dict

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
    flow_key: Optional[str] = None

# Contexts per task
class TripSuggestionContext(BaseContext):
    city: Optional[str]
    days: Optional[int] = 1
    interests: Optional[List[str]] = []
    pace: Optional[str] = "moderate"
    budget: Optional[str] = None

class ItineraryPlannerContext(BaseContext):
    city: str
    days: int
    pace: Optional[str] = "moderate"
    interests: Optional[List[str]] = []
    transport: Optional[str] = None
    budget: Optional[int] = None
    must_see: Optional[List[str]] = []
    start_loc: Optional[str] = None

class ReviewSummarizerContext(BaseContext):
    poi_id: Optional[str]
    poi_name: Optional[str]
    timeframe: Optional[str] = "all_time"
    sentiment_focus: Optional[str] = "overall"

class MeetingPointContext(BaseContext):
    participants: Optional[List[Dict]] = []  # {id?, lat?, lon?, label?}
    preferred_mode: Optional[str] = "walk"
    time_window: Optional[str] = None

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
