# core/types.py
"""
Shared data contracts for Map-Assistant.

These dataclasses and enums are used across:
- Query analysis (parse user text → structure)
- Classification (which feature?)
- Decomposition (which steps to run?)
- Execution/Integration/Rendering (downstream stages)

Edit here first when you need a new field or a new Feature.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Feature(Enum):
    """
    The six core features (from README) plus OTHER as a fallback.
    Keep the string values stable; they’re used in logs/JSON.
    """
    SMART_TRIP_SUGGESTIONS = "smart_trip_suggestions"           # #1
    ITINERARY_PLANNER      = "personalized_itinerary_planner"   # #2
    REVIEW_SUMMARIZER      = "review_aggregator_summarizer"     # #3
    MEETING_POINT          = "meeting_point_recommender"        # #4
    ROUTE_OPTIMIZATION     = "multi_spot_route_optimization"    # #5
    TRAVEL_COMPARISON      = "flights_trains_hotels_comparison" # #6
    OTHER                  = "other"                            # fallback


@dataclass
class QueryAnalysis:
    """
    Output of the analyzer stage:
    - tokens: lowercased tokens from the raw query
    - cities/pois: naive detections to help routing
    - people: simple group-size hints (e.g., ["2"])
    - money/currency: budget like ₹5000
    - days/date_spans/times_of_day: time constraints
    - constraints: bag for anything structured we parse
    """
    raw: str
    tokens: List[str]
    cities: List[str] = field(default_factory=list)
    pois: List[str] = field(default_factory=list)
    people: List[str] = field(default_factory=list)

    money: Optional[float] = None
    currency: Optional[str] = None

    days: Optional[int] = None
    date_spans: List[str] = field(default_factory=list)
    times_of_day: List[str] = field(default_factory=list)

    constraints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Classification:
    """
    Result of routing/classification:
    - feature: which Feature we think this is
    - confidence: 0..1 score (rule-based or hybrid)
    - reasons: human-readable strings for audit/debug
    """
    feature: Feature
    confidence: float
    reasons: List[str]


@dataclass
class PlanStep:
    """
    A single operation the system should perform.
    Examples:
      PlanStep("FETCH_POI_CANDIDATES", {"city":"Jaipur"}, source="pois_db")
      PlanStep("OPTIMIZE_ORDER", {"objective":"least_walking"}, source="engine")

    Conventions:
    - op: UPPER_SNAKE verbs to be explicit
    - args: JSON-serializable dict (keep it small & clear)
    - source: where this step is executed ('llm', 'pois_db', 'engine', 'routing_api', etc.)
    """
    op: str
    args: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None


@dataclass
class Decomposition:
    """
    An ordered list of PlanSteps (the logical plan).
    Notes can carry high-level intent or caveats.
    """
    steps: List[PlanStep]
    notes: str = ""


@dataclass
class RoutedQuery:
    """
    The bundle returned by QueryManager.process():
    - analysis: QueryAnalysis
    - classification: Classification
    - decomposition: Decomposition (plan)
    """
    analysis: QueryAnalysis
    classification: Classification
    decomposition: Decomposition


__all__ = [
    "Feature",
    "QueryAnalysis",
    "Classification",
    "PlanStep",
    "Decomposition",
    "RoutedQuery",
]
