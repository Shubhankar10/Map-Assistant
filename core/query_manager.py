#Rujhil vala

# Input User Query, Pass on to Decomposer with just the query and feature

from __future__ import annotations
import re
from typing import Any, Dict, List, Tuple

from core.types import (
    Feature, QueryAnalysis, Classification, Decomposition, RoutedQuery
)
from decompose import get_decomposer  # registry provides the per-feature decomposer


class QueryManager:
    """
    Analyze → Classify → Dispatch.
    Keep this file deterministic (no network) so it's easy to test.
    """

    # -------------------------
    # Keyword banks (tune freely)
    # -------------------------
    KW = {
        "trip_suggestions": {
            "must": ["suggest", "recommend", "ideas", "things to do", "where to go", "day trip", "weekend trip"],
            "boost": ["budget","family","solo","nature","food","heritage"]
        },
        "itinerary": {
            "must": ["itinerary", "day-wise", "plan my day", "schedule", "timeline", "day 1", "day 2", "plan a 2-day", "2-day itinerary"],
            "boost": ["relaxed","packed","morning","evening","lunch","dinner"]
        },
        "reviews": {
            "must": ["reviews", "review", "pros and cons", "summarize reviews", "is it crowded", "is it safe", "ratings", "tips", "feedback"],
            "boost": ["accessibility","wheelchair","queue","wait"]
        },
        "meeting": {
            "must": ["meeting point", "meet", "halfway", "middle point", "between", "equidistant", "fair for both"],
            "boost": ["cafe","coffee","landmark"]
        },
        "route_opt": {
            "must": ["optimize route", "best route", "shortest route", "order to visit", "multiple spots", "sequence", "route for these places", "visit"],
            "boost": ["least walking","fastest","scenic","avoid traffic"]
        },
        "travel_compare": {
            "must": ["flight","flights","train","trains","hotel","hotels","compare","fare","tickets","price","cheapest","budget"],
            "boost": ["from","to","depart","return","dates","under ₹","under rs","under inr"]
        },
    }

    # Naive dictionaries to spot cities/POIs/time hints
    CITY_HINTS = [
        "delhi","new delhi","mumbai","jaipur","bengaluru","bangalore","kolkata",
        "chennai","pune","hyderabad","agra","goa","udaipur","varanasi","amritsar",
        "kochi","cochin","ahmedabad","lucknow","indore","surat","bhopal"
    ]
    TIME_HINTS = ["morning","afternoon","evening","night","today","tomorrow","weekend"]
    POI_HINTS = [
        "fort","temple","museum","park","gate","minar","beach","lake","market","bazaar",
        "cafe","restaurant","palace","monument","zoo","garden","church","mosque"
    ]

    # Regex extractors
    # Support commas in amounts like ₹8,000.50
    MONEY_RE = re.compile(
        r"(₹|rs\.?|inr)\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?|[0-9]+(?:\.[0-9]+)?)",
        re.IGNORECASE
    )
    DAYS_RE  = re.compile(r"(\d+)\s*-\s*(day|days)|(\d+)\s*day", re.IGNORECASE)
    DATE_SPAN_RE = re.compile(
        r"(\d{1,2}\s*[-/]\s*\d{1,2}\s*[A-Za-z]{3,})|(\d{1,2}\s*[A-Za-z]{3}\s*(?:to|-)\s*\d{1,2}\s*[A-Za-z]{3})"
    )

    # ---------- public entrypoint ----------
    def process(self, query: str) -> RoutedQuery:
        """
        Return a RoutedQuery {analysis, classification, decomposition}.
        """
        analysis = self._analyze(query)
        classification = self._classify(analysis)
        decomposition = self._dispatch(classification.feature, analysis)
        return RoutedQuery(analysis=analysis, classification=classification, decomposition=decomposition)

    # ---------- analysis ----------
    def _analyze(self, q: str) -> QueryAnalysis:
        q_clean = " ".join(q.strip().split())
        tokens = [t.lower() for t in re.split(r"[\s,;:.!?]+", q_clean) if t]
        ql = q_clean.lower()

        # money (normalize commas)
        money, currency = None, None
        m = self.MONEY_RE.search(ql)
        if m:
            currency = m.group(1).lower()
            amount = m.group(2).replace(",", "")
            money = float(amount)

        # days
        days = None
        d = self.DAYS_RE.search(q_clean)
        if d:
            days = int(d.group(1) or d.group(3))

        # dates & times
        date_spans = [m.group(0) for m in self.DATE_SPAN_RE.finditer(q_clean)]
        times_of_day = [t for t in self.TIME_HINTS if t in tokens]

        # robust multiword city spotting with word boundaries
        def _has_word(phrase: str) -> bool:
            return re.search(rf"\b{re.escape(phrase.lower())}\b", ql) is not None

        cities = [c for c in self.CITY_HINTS if _has_word(c)]

        # POIs: token-based is fine for single-word hints
        pois = [w for w in tokens if w in self.POI_HINTS]

        # people/group hints
        people: List[str] = []
        if "both" in tokens or "two" in tokens: people.append("2")
        if "three" in tokens: people.append("3")
        if "four" in tokens: people.append("4")
        # numeric form: "3 people", "4 persons", "5 friends"
        num_people = re.search(r"\b(\d+)\s*(people|persons|ppl|friends|guys)\b", ql)
        if num_people:
            people.append(num_people.group(1))

        constraints: Dict[str, Any] = {}
        if money is not None:
            constraints.update({"budget_value": money, "budget_currency": currency})
        if days is not None:
            constraints["days"] = days
        if date_spans:
            constraints["date_spans"] = date_spans

        return QueryAnalysis(
            raw=q_clean,
            tokens=tokens,
            cities=cities,
            pois=pois,
            people=people,
            money=money,
            currency=currency,
            days=days,
            date_spans=date_spans,
            times_of_day=times_of_day,
            constraints=constraints
        )

    # ---------- classification ----------
    def _classify(self, a: QueryAnalysis) -> Classification:
        ql = a.raw.lower()

        def score(must: List[str], boost: List[str]) -> Tuple[float, List[str]]:
            if not any(k in ql for k in must):
                return 0.0, []
            sc, reasons = 0.6, [f"matched: {', '.join([k for k in must if k in ql])}"]
            hits = [b for b in boost if b in ql]
            if hits:
                sc += 0.1 * min(3, len(hits))  # cap boosts
                reasons.append(f"boosts: {', '.join(hits)}")
            return min(sc, 0.95), reasons

        cands: List[Tuple[Feature, float, List[str]]] = []

        s, r = score(**self.KW["trip_suggestions"])
        if s and (a.cities or "things to do" in ql):
            s = min(0.99, s + 0.15); r.append("city/‘things to do’ present")
            cands.append((Feature.SMART_TRIP_SUGGESTIONS, s, r))

        s, r = score(**self.KW["itinerary"])
        if s and (a.days or set(a.times_of_day) & {"morning","evening"}):
            s = min(0.99, s + 0.1); r.append("day/time constraints present")
            cands.append((Feature.ITINERARY_PLANNER, s, r))

        s, r = score(**self.KW["reviews"])
        if s:
            cands.append((Feature.REVIEW_SUMMARIZER, s, r))

        s, r = score(**self.KW["meeting"])
        if s:
            if "between" in a.tokens:
                s = min(0.99, s + 0.1); r.append("contains ‘between’")
            cands.append((Feature.MEETING_POINT, s, r))

        s, r = score(**self.KW["route_opt"])
        if s:
            if len(a.pois) >= 2 or "visit" in a.tokens:
                s = min(0.99, s + 0.1); r.append("multiple POIs/‘visit’")
            cands.append((Feature.ROUTE_OPTIMIZATION, s, r))

        s, r = score(**self.KW["travel_compare"])
        if s:
            if a.money is not None or a.date_spans:
                s = min(0.99, s + 0.1); r.append("budget/dates present")
            cands.append((Feature.TRAVEL_COMPARISON, s, r))

        if not cands:
            return Classification(feature=Feature.OTHER, confidence=0.3, reasons=["no feature keywords matched"])

        cands.sort(key=lambda x: (-x[1], x[0].value))
        feat, conf, reasons = cands[0]
        if len(cands) == 1:
            conf = min(1.0, conf + 0.05)
        return Classification(feature=feat, confidence=round(conf, 2), reasons=reasons)

    # ---------- dispatch ----------
    def _dispatch(self, feature: Feature, a: QueryAnalysis) -> Decomposition:
        """
        Ask the registered decomposer for this feature to build a Plan.
        For now, if nothing registered, return an empty plan with a note.
        """
        decomposer = get_decomposer(feature)
        return decomposer(a)


# quick manual demo
if __name__ == "__main__":
    qm = QueryManager()
    demos = [
        "Suggest a 3-day Jaipur trip with heritage focus and mid budget",
        "Plan a relaxed 2-day itinerary for Delhi with mornings free",
        "Summarize reviews for Amer Fort focusing on crowding and accessibility",
        "Find a fair cafe to meet between Connaught Place and Hauz Khas",
        "Best route to visit Red Fort, India Gate and Qutub Minar with least walking",
        "Compare flights and hotels from Mumbai to Goa 1-4 Oct under ₹8,000",
        "Create a journal entry from my Day 1 notes in Jaipur",
        "We are 3 people meeting halfway between Andheri and Bandra, suggest a cafe"
    ]
    for q in demos:
        r = qm.process(q)
        print(f"\nQ: {q}")
        print(f"Feature → {r.classification.feature.value} (conf {r.classification.confidence})")
        print("Reasons:", "; ".join(r.classification.reasons))
        print("Plan steps:", [s.op for s in r.decomposition.steps])
