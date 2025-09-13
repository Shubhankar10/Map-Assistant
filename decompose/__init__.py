# decompose/__init__.py
"""
Decomposer registry for Map-Assistant.

A 'decomposer' is a function that takes a QueryAnalysis and returns a
Decomposition (an ordered list of PlanSteps to execute for that feature).

Usage in a per-feature module (e.g., decompose/itinerary.py):

    from decompose import register
    from core.types import Feature, QueryAnalysis, Decomposition, PlanStep

    @register(Feature.ITINERARY_PLANNER)
    def build(a: QueryAnalysis) -> Decomposition:
        return Decomposition(
            steps=[
                PlanStep("NL_EXTRACT_ITINERARY_PARAMS", {"text": a.raw}, source="llm"),
                # ...more steps...
            ],
            notes="Build day-wise itinerary"
        )

QueryManager calls get_decomposer(feature) to retrieve the registered function.
"""

from __future__ import annotations
from typing import Callable, Dict
from core.types import Feature, QueryAnalysis, Decomposition

# Type alias: any decomposer takes a QueryAnalysis → returns a Decomposition
Decomposer = Callable[[QueryAnalysis], Decomposition]

# Internal registry: Feature -> decomposer function
_registry: Dict[Feature, Decomposer] = {}


def register(feature: Feature):
    """
    Decorator to register a decomposer for a given feature.

    Example:
        @register(Feature.MEETING_POINT)
        def build(a: QueryAnalysis) -> Decomposition:
            ...
    """
    def _wrap(fn: Decomposer) -> Decomposer:
        _registry[feature] = fn
        return fn
    return _wrap


def get_decomposer(feature: Feature) -> Decomposer:
    """
    Return a registered decomposer if present, else a safe fallback
    that yields an empty plan with a helpful note.
    """
    def _fallback(a: QueryAnalysis) -> Decomposition:
        return Decomposition(steps=[], notes=f"No decomposer registered for {feature.value}")
    return _registry.get(feature, _fallback)


def list_registered() -> Dict[str, str]:
    """
    Debug helper: see which features have decomposers loaded.
    Returns {feature_value: function_qualname}.
    """
    return {f.value: getattr(fn, "__qualname__", getattr(fn, "__name__", "unknown")) for f, fn in _registry.items()}


# --- auto-import decomposers so their @register side-effects run ---
# Add more imports here as you implement them.
from . import meeting_point       # noqa: F401
# from . import itinerary          # noqa: F401
# from . import trip_suggestions   # noqa: F401
# from . import reviews            # noqa: F401
# from . import route_optimization # noqa: F401
# from . import travel_comparison  # noqa: F401

__all__ = ["register", "get_decomposer", "list_registered"]
