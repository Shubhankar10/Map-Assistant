"""

BaseContext class for managing general context in the application.
Child Context classes can extend this to add specific context handling.

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
