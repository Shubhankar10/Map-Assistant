def get_prompt(key: str, **kwargs) -> str:
    template = PROMPT_TEMPLATES.get(key)
    if not template:
        raise ValueError(f"Prompt key '{key}' not found.")
    return template.format(**kwargs)



PROMPT_TEMPLATES = {
    "summarize": "You are a helpful assistant. Summarize the following text:\n",

    "qa": "You are an expert in {domain}. Answer the following question in detail:\n",

    "translate": "You are a professional translator. Translate the following text from {source_lang} to {target_lang}:\n",

    "creative_story": "You are a creative storyteller. Continue the story based on the following:\n",



    "query_analyser": "You are a travel assistant task selector.A user gave this query: {user_query} Choose **exactly one** task from the following list that best fits the user's intent: {tasks} Only output the **task name**. Do not include any explanations or extra text.",
    
    

    "sql": """
You are given a PostgreSQL schema (below).  
Generate **only one valid SQL SELECT query** using the schema and a JSON context.

**Rules**
1. Output **only** the SQL query — no explanations.  
2. Query must be valid PostgreSQL.  
3. Select and join only tables/columns from the schema.  
4. Always filter by `"user_id"` from the JSON. If missing, return: `user_id missing`.  
5. Select only columns listed in JSON. If none given, select a minimal meaningful set.  
6. Use explicit JOINs via foreign keys.  
7. Use `ILIKE` for text matches.  
8. For text arrays → `&& ARRAY[...]::text[]` (overlap) or `= ANY(ARRAY[...])` (single match).  
9. For numeric/date ranges → use `>=`, `<=`, or `BETWEEN`.  
10. Multiple filter values → match any (`IN`, `ILIKE OR`, or array overlap).  
11. Respect `"order_by"`, `"limit"`, `"offset"` if present.  
12. Use aggregates/grouping if requested.  
13. Escape strings properly.  
14. End query with a semicolon.

**Schema**
Tables:

user_details(user_id UUID PK, dob DATE, gender VARCHAR(20), aadhar_number VARCHAR(20),
passport_number VARCHAR(20), driving_license_number VARCHAR(20),
spoken_languages TEXT[], understood_languages TEXT[], native_language VARCHAR(50),
hometown VARCHAR(100), current_city VARCHAR(100), address TEXT, phone_number VARCHAR(20),
home_lat DECIMAL(9,6), home_lng DECIMAL(9,6), dietary_preferences TEXT[],
FK user_id → users.user_id)

travel_preferences(pref_id UUID PK, user_id UUID FK→users.user_id,
budget_min NUMERIC(10,2), budget_max NUMERIC(10,2), transport_pref VARCHAR(50),
commute_pref VARCHAR(50), pace VARCHAR(20), travel_duration_preference VARCHAR(50),
travel_group_preference VARCHAR(50), preferred_regions TEXT[], season_preference VARCHAR(50),
accommodation_type VARCHAR(50), special_needs TEXT, frequent_travel BOOLEAN)

user_interests(interest_id UUID PK, user_id UUID FK→users.user_id,
tag VARCHAR(100), sub_tag VARCHAR(100), preferred_vacation_type VARCHAR(50),
activity_type VARCHAR(100), frequency_of_interest VARCHAR(50), special_notes TEXT)


**JSON context**
{context}
{user_id}

**Output**
Return a single SQL query following the above rules.

    """,

"sql2": """

There are 3 tables  : user_details,user_interests,travel_preferences, each has a user_id attribute.
Write a PostgresSQL query, where user_id = {user_id}
It should be a simple query, just get all all row values for each table with that user_id, nothing else.

**Output**
Return a single SQL query following the above rules.
""",

    "TripSuggestion": """
    You are an assistant that extracts structured trip suggestion parameters.
    Output JSON: {"city": str, "days": int, "interests": [str], "pace": "slow|moderate|fast", "budget": str|int|null}
    User query:
    "{query}"
    Return ONLY JSON.
    """, 


    "ItineraryPlanner": """
        Extract itinerary planning parameters from the user query.
        Output JSON matching the ItineraryPlannerContext model:

        {{
            "city": str,                      
            "travel_duration": int,          
            "pace": str,                    
            "interests": [str],               
            "dietary_preferences": [str],    
            "special_needs": [str],           
            "transport_pref": str|null,      
            "commute_pref": str|null,         
            "budget_max": int|null,           
            "accommodation_type": str|null,   
            "must_see": [str],                
            "start_loc": str|null,        
            "activity_type": str|null,        
            "preferred_vacation_type": str|null,  
            "tag": str|null,                  
            "sub_tag": str|null,              
            "special_notes": str|null         
        }}

        User query:
        "{query}"

        Return ONLY JSON. Do not add explanations or extra text.
        """,


    "NoneOfThese": """
    You are a map assistant. The user's query does not fit into any predefined category. 
    Respond directly and naturally to the user's query: {{user_query}} — do not include any introductory or meta statements before your answer. 
    After providing your full response, conclude with a short statement such as:
    "I can also assist you more precisely with map-related tasks, like planning trips and routes."
    """,


    "ReviewSummarizer": """
    Extract target for review summarization.
    Output JSON: {"poi_id": str|null, "poi_name": str|null, "timeframe": str, "sentiment_focus": "overall|positive|negative"}
    User query:
    "{query}"
    Return ONLY JSON.
    """,


    "MeetingPointPlanner": """
    Extract all relevant participants, constraints, and preferences from the user query for planning a meeting point.  
    Output JSON matching the MeetingPointContext model.

    JSON Format:
    {{
        "participants": [
            {{
                "id": str|null,          # optional unique identifier for participant
                "label": str|null,       # e.g., "Me", "Friend", "Colleague"
                "lat": float|null,       # optional, if known
                "lon": float|null,       # optional, if known
                "address": str|null      # optional textual address
                "avoid_long_distance": bool|null,                 # true if someone cannot travel far
            }}
        ],
        "preferred_mode": "walk|drive|transit|metro|null",  # primary travel mode for participants
        "max_travel_time_minutes": int|null,                # optional travel time limit per participant
        "accessibility_needs": [str],                      # e.g., ["wheelchair"], empty if none
        "cuisine_type": [str],                              # e.g., ["Italian", "Chinese"], empty if unspecified
        "venue_type": [str],                                # e.g., ["restaurant", "cafe"], empty if unspecified
        "budget_max_per_person": int|null,                 # optional
        "open_now": bool|null,                             # optional, default true if unspecified
        "time_window": str|null,                           # e.g., "7 PM - 9 PM"
        "central_location_priority": bool|null,           # true if preference to meet at midpoint
        "tag": str|null,
        "sub_tag": str|null,
        "special_notes": str|null
    }}

    User query:
    "{query}"

    Instructions:
    - Extract all participants and assign IDs or labels where possible.  
    - Determine participant constraints and travel preferences.  
    - Determine venue preferences (cuisine, type, budget, open_now).  
    - Extract time_window if specified.
    - Identify constraints such as avoid_long_distance or accessibility_needs.
    - Return ONLY JSON; do not include explanations or extra text.
    """,


    "RouteOptimizer": """
    Extract origin and destinations for route optimization.
    Output JSON: {"origin": {"lat": float, "lon": float, "label": str|null}, "destinations": [{"lat": float, "lon": float, "label": str|null}],
    "constraints": {}}
    User query:
    "{query}"
    Return ONLY JSON.
    """,


    "TripJournalManager": """
    Extract trip journal parameters.
    Output JSON: {"user_id": str|null, "trip_id": str|null, "start_date": str|null, "end_date": str|null, "tags": [str]}
    User query:
    "{query}"
    Return ONLY JSON.
    """,
}
