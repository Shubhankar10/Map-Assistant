# decompose/meeting_point.py
from __future__ import annotations
from core.types import PlanStep, Decomposition, QueryAnalysis, Feature
from decompose import register


@register(Feature.MEETING_POINT)
def build(a: QueryAnalysis) -> Decomposition:
    """
    Build a logical plan for 'Find a fair cafe halfway between A and B' style queries.

    This returns *what to do*, not the execution. An executor will later:
      - call an LLM to resolve the two party locations to coordinates,
      - query POIs near the geometric midpoint,
      - compute travel times for each party,
      - rank candidates by a fairness metric (minimax),
      - explain tradeoffs via LLM.

    Inputs we use from QueryAnalysis:
      - a.raw: the original text (LLM needs this for parsing place names)
      - a.pois: hints like 'cafe'
      - a.people: simple hints like ["2"] (optional)
    """
    poi_types = ["cafe", "coffee", "bakery", "tea", "restaurant"]
# If the query already mentioned a specific POI type (e.g., 'cafe'), prioritize it.
    if a.pois:
        poi_types = list(dict.fromkeys(a.pois + poi_types))  # keep order, uniq

    steps = [
        # 1) Turn the free-text locations ('between X and Y') into normalized coordinates.
        PlanStep(
            "EXTRACT_LOCATIONS_FOR_PARTIES",
            {"text": a.raw, "max_parties": 2},  # you can extend to 3+ later
            source="llm"
        ),

        # 2) Use DB of POIs (cached from OSM/places) to fetch candidates near midpoint / both areas.
        PlanStep(
            "CANDIDATE_POIS_MIDPOINT",
            {
                "poi_types": poi_types,
                "radius_m": 2500,            # start conservative; tune later
                "max_results": 30,           # fetch enough for ranking
                "dedupe_by_name": True
            },
            source="pois_db"
        ),

        # 3) Compute travel times for each party to each candidate (cache-first).
        PlanStep(
            "TRAVEL_TIMES_PER_PARTY",
            {
                "modes": ["driving", "transit", "walking"],  # executor can downselect
                "timeout_s": 8
            },
            source="routing_api"
        ),

        # 4) Rank by fairness (minimax of party times), tie-break by mean time then rating.
        PlanStep(
            "FAIRNESS_RANK",
            {
                "metric": "minimax",
                "tie_breakers": ["mean_time", "poi_rating_desc"],
                "top_k": 5
            },
            source="engine"
        ),

        # 5) Ask LLM to explain the tradeoffs (no new facts, just reasoning).
        PlanStep(
            "EXPLAIN_TRADEOFFS",
            {
                "style": "concise",
                "include_metrics": ["you_min", "friend_min", "delta", "mode"]
            },
            source="llm"
        ),
    ]

    return Decomposition(steps=steps, notes="Find equidistant, fair meeting options")
