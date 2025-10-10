# Map Assistant
## TODO
- Add Fetch from DB Step
- Make the other TASKs
- Report
- Flow Rakhna hai ya nahi decide
- Make MAPS HTML Page
- Default Task banana hai

---

- If number of tables in Schema is more change DB struct to per-table individual class.
(
Small projects / prototypes → one class (your current design) is totally fine.
Large apps / production → per-table classes (often called DAO = Data Access Objects) is the clean convention.
In fact, most frameworks (like Django ORM or SQLAlchemy) use the per-table model approach.
)

---

## Project Overview

The Map Assistant is an intelligent travel planner that integrates two relational databases — one for **user & trip data** and another for **POI, routes, and cached API results** — along with an **LLM layer** for natural language interpretation, summarization, and explanation.

The system provides personalized trip suggestions, builds structured itineraries, aggregates and summarizes reviews, finds balanced meeting points for groups, optimizes multi-spot routes, compares flights/hotels/trains, and supports journaling of travel experiences.

The design separates **deterministic data operations** (SQL, spatial queries, API calls) from **LLM-driven tasks** (parameter extraction, summarization, narration, trade-off explanation).

---

# Key Features

### 1. Smart Trip Suggestions

**What it does:** Generates destination and activity recommendations tailored to user preferences (budget, interests, duration, pace).

**How it works:**

* Fetches user preferences from **DB A (User & Trip Management)**.
* Queries cached POIs by location and category from **DB B (POI Cache & Spatial)**.
* Calls transport/hotel APIs (cached in DB B) for feasibility checks.
* **LLM (DB C)** extracts structured constraints from user queries and presents multiple suggestions with explanations.

**Example LLM prompt:**

```
User: "I want a 3-day trip to Jaipur with heritage focus, budget hotels, and relaxed mornings."
System: Extract {city:"Jaipur", days:3, interests:["heritage"], pace:"relaxed", budget:"mid"}
```

---

### 2. Personalized Itinerary Planner

**What it does:** Builds **day-wise itineraries** including POIs, transport, meals, and hotel stays. Produces multiple ranked options (fastest, cheapest, most scenic).

**How it works:**

* Fetches user trip data from **DB A**.
* Queries POIs, transport times, cached offers from **DB B**.
* Runs routing/optimization engine for feasibility.
* **LLM (DB C)** narrates itineraries and explains tradeoffs.

**Example LLM prompt:**

```
User: "Plan a 2-day relaxed Delhi itinerary with top heritage sites."
LLM Input: {city:"Delhi", days:2, pace:"relaxed", interest:"heritage", transport:"car"}
LLM Output: "Day 1: Red Fort → Jama Masjid → Chandni Chowk food walk. Day 2: India Gate → Humayun's Tomb → Qutub Minar."
```

---

### 3. Review Aggregator & Summarizer

**What it does:** Collects reviews from APIs and produces concise summaries with pros, cons, and practical tips.

**How it works:**

* Reviews cached in **DB B (Reviews table)** with metadata.
* **LLM (DB C)** processes review batches to create sentiment-aware summaries.
* Summaries linked to itineraries in **DB A**.

**Example LLM prompt:**

```
User: "Summarize reviews for Amer Fort focusing on crowding and accessibility."
LLM Output: "Best visited mornings on weekdays, sunset view popular. Crowds heavy on weekends. Limited wheelchair access."
```

---

### 4. Meeting Point Recommender

**What it does:** Suggests fair meeting places (cafes, landmarks) equidistant in travel time for two or more users.

**How it works:**

* Fetch participant locations from **DB A**.
* Query candidate POIs with spatial filters in **DB B**.
* Compute travel times (check RoutesCache in DB B → fallback to API).
* Rank by fairness metrics.
* **LLM (DB C)** presents natural-language explanation of trade-offs.

**Example LLM prompt:**

```
User: "Find a fair cafe between Connaught Place and Hauz Khas."
LLM Input: [Cafe options with travel times per user]
LLM Output: "Cafe 1 (Khan Market) — 22 min each; balanced but pricier. Cafe 2 — slightly uneven but cheaper."
```

---

### 5. Multi-spot Route Optimization & Comparison

**What it does:** Optimizes routes for multiple POIs with different objectives (shortest time, least walking, cheapest, most scenic).

**How it works:**

* User-selected POIs pulled from **DB A (ItineraryEntries)**.
* Travel times fetched from **DB B (RoutesCache)** or API.
* Backend route optimization performed.
* **LLM (DB C)** compares options and explains differences.

**Example LLM prompt:**

```
User: "Plan the best route for Red Fort, India Gate, and Qutub Minar with minimum walking."
LLM Output: "Option 1: More taxi, less walking (1.2 km). Option 2: Faster overall but requires 3 km walking."
```

---

### 6. Flights, Trains & Hotels Comparison

**What it does:** Fetches and compares offers for flights, trains, and hotels, presenting best-fit combinations with user itinerary.

**How it works:**

* Cached offers stored in **DB B** (FlightOffers, TrainOffers, HotelOffers).
* Trip integration stored in **DB A**.
* **LLM (DB C)** summarizes best matches and explains trade-offs (price vs. location).

**Example LLM prompt:**

```
User: "Find Mumbai trip 1–4 Oct under ₹8k flights and ₹3k hotel."
LLM Output: "Morning flight 1 Oct ₹7.5k + Hotel ABC ₹2.7k near Marine Drive. Leaves afternoon free."
```

---

### 7. User Trip Journal

**What it does:** Lets users record and share trip highlights (photos, notes, check-ins). Can auto-generate journal entries from itinerary + reviews + user notes.

**How it works:**

* Journals stored in **DB A (TripJournal table)** linked to itineraries.
* Photos/notes metadata stored securely.
* **LLM (DB C)** converts raw entries into polished narratives (optionally with summaries).

**Example LLM prompt:**

```
User: "Create a journal entry from my Day 1 Jaipur trip notes."
Input: [Amer Fort visit, hot weather, sunset photos, street food dinner]
LLM Output: "Day 1 in Jaipur — Began at Amer Fort in the morning breeze, ended with a colorful street food dinner under the sunset sky."
```

---

# Data Architecture

### A. User & Trip Management DB (Relational DB 1)

Stores **user profiles, preferences, itineraries, journals, and bookings**.

### B. POI / API Cache & Spatial DB (Relational DB 2)

Stores **POIs, reviews, cached routes, transport & hotel offers** with spatial queries via PostGIS.

### C. LLM Layer (Query Breakdown & Web Data Gathering)

Handles **natural language → structured queries**, **summaries**, **narratives**, and **explanations of trade-offs**.

---
