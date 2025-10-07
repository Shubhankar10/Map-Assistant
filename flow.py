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

    # Get Data from DB where context is none.
    
# Input Conext, DB
#     Jo jo none hai, uss ko DB se fetch karna hai 
# Output Context

    # Get POIs from API according to user query
# Input Conext, DB
    #Interest k hisab se POIs ki query generate karni hai
    # Query Execute
    # POIs update in context
# Output Context

    # Pass the context to LLM for itinerary generation

#DB

#     fetch_user_preferences,
# fetch_user_interests,
# #API    
#     generate_poi_query, #input context
#     fetch_pois,
#     pre_filter_pois,
# #LLM    
#     generate_itineraries,
# #API    
#     validate_routes,
# #LLM    
#     optimize_itinerary,
#     score_and_rank,    
#     generate_narration,
#     return_response
]
}