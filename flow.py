"""

Store Flow for each Feature




Input is Context

Fetch User Preferences
Generate POI Query
Fetch POIs
Pre-filter POIs
LLM-Assisted Routing
Validate & Refine Routing
Optimization
Score & Rank Plans
Generate Narration & Explanation from context
Return Response




"""
FLOW = {
'ItineraryPlanner':[
#DB
    'fetch_user_preferences', 
    fetch_user_interests,

#API    
    generate_poi_query,
    fetch_pois,
    # pre_filter_pois,
#LLM    
    generate_itineraries,
#API    
    validate_routes,
#LLM    
    optimize_itinerary,
    score_and_rank,    
    generate_narration,
    return_response
]
}