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

'MeetingPointPlanner': [

    # 2️⃣ Fetch participant details from DB
    'fetch_participant_details',         

    # 3️⃣ Geocode addresses (if needed)
    'geocode_participant_addresses',     # Convert textual addresses into coordinates for calculations

    # 6️⃣ Calculate optimal midpoint
    'calculate_optimal_midpoint',        # Compute central or weighted midpoint location between participants


    # 4️⃣ Generate candidate venues
    'generate_candidate_venues',         # Query Google Places API based on cuisine_type, venue_type, budget, open_now

    # 5️⃣ Pre-filter candidate venues
    'pre_filter_venues',                 # Remove venues that don't satisfy time_window, max_travel_time, accessibility, or distance constraints


    # 8️⃣ Generate response
    'generate_narration',                # Optional: create human-readable explanation / suggestions for selected venues

    # # 9️⃣ Return final result
    'return_response'                    # Return selected venues, midpoint info, and structured data
],

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


