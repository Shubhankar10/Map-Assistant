Alright, let’s carefully re-explain **Task 2** (the one you pasted earlier).

---

### Task 2 Statement

> The query (text-based) should span over these data sources.
> Analyse (5%) and decompose (5%)
> federate (3%), execute (2%), integrate and render the query results (5%) in the context asked.

---

### What this means in detail

When you build your project (e.g., the **Map Assistant**), the system must be able to **take one natural language query from the user** and process it across **multiple data sources** (your relational DBs, APIs, and the LLM).

#### Step-by-step breakdown:

1. **Analyse (5%)**

   * Take the raw text query (e.g., *“My friend is in location A, I am in location B, find cafes where both of us travel equally.”*).
   * Understand its intent (trip planning? location search? comparison?).
   * Identify which data sources are relevant (LLM for decomposition, Places API for cafes, Directions API for distance).

2. **Decompose (5%)**

   * Break the query into **smaller subtasks**.
   * Example subtasks:

     * Extract the two input locations.
     * Find the midpoint between A and B.
     * Search for cafes around the midpoint.
     * Calculate travel times for both users.
     * Return cafes where travel time is roughly equal.

   Here, your **QueryAnalyzer pipeline + LLM** will handle this.

3. **Federate (3%)**

   * “Federation” means: gather data from **different, independent sources** in one workflow.
   * Example:

     * User data (from relational DB)
     * Cafes from **Google Places API** or **OpenStreetMap**
     * Distances from **Google Directions API**
     * Contextual reasoning from **LLM**

   The system doesn’t just use one database, but “federates” across them.

4. **Execute (2%)**

   * Run each subtask on the right component.
   * Example:

     * Call `PlacesAPI.find_places()` for cafes
     * Call `DirectionsAPI.get_directions()` for travel times
     * Use LLM to re-rank or summarize the results

5. **Integrate and Render (5%)**

   * Merge results into a **final structured answer** that makes sense to the user.
   * Example output:

     > *“You and your friend can meet at Café X (20 mins each), Café Y (22 mins each), and Café Z (19 mins vs 21 mins). Café X is the closest to both.”*
   * Could be rendered as text, JSON, or on a map UI.

---

### In summary

Task 2 is basically about showing that:

* You can take a **single user query**.
* Break it down (analysis + decomposition).
* Pull data from **multiple databases/APIs** (federation + execution).
* Combine results into **one coherent answer** (integration + rendering).

It maps directly to your **Map Assistant pipeline** idea.

---

Do you want me to also give you a **worked-out example of Task 2 with your Map Assistant** (showing query → subtasks → data sources → final integrated answer), like a flowchart but in text?