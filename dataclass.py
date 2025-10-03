# Keep context class here
# Set of values needed ton pass in each step like JSON


"""
raw : user query
tokens : tokenized words from the query
cities : list of cities mentioned in the query  
pois : points of interest mentioned in the query
people : list of people mentioned in the query
money : budget mentioned in the query
currency : currency mentioned in the query
days : number of days mentioned in the query
date_spans : list of date spans mentioned in the query
times_of_day : list of times of day mentioned in the query
constraints : any other constraints mentioned in the query

feature : which feature we think this is
confidence : confidence score (0..1)
reasons : human-readable strings for audit/debug
op : operation to be performed (e.g., "FETCH_POI_CANDIDATES")
args : arguments for the operation (JSON-serializable dict)
source : where this step is executed ('llm', 'pois_db', 'engine', 'routing_api', etc.)

from database
user personal preferences
tags


"""