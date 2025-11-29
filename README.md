#TODO


## Queries
- "Based on my favorite cuisines, tell me the cities where these cuisines originated and suggest top-rated restaurants in those cities."

- "Design a travel route that matches my travel pace, includes 3–4 major Indian cities, explains the best sequence to visit them, and suggests key attractions in each."

- "Find the population and best pizza places in my hometown and my current city"


## Kya ho raha hai

- Analyser Return user ka expanded intent
- Decomposer Divideds taskes to each db, as instructions ki uss DB se kya chahiye
- Federator teeno DB k liye alag hai, vo instructions ko leke excat query dera SQL or API call whatever
- Executor bhi alag hai simply query to execute kar k data ko format kar rahe
- Integrator llm call with intent and data base data se final response bana raha

## Files
- LLM, Places api in apis
- DB in postgress
- db_populate for sample data 
- main to run the complete flow
- app.py in streamlit to see UI and run main


## env must have
- LLM_API_KEY
- MAPS_API_KEY
- DB_HOST
- DB_PASSWORD



## Notes

Last mai clean nahi kiye hai, so bahut unused parts hai steps mai ya files mai.