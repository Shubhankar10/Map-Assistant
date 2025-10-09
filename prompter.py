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
