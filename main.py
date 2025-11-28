from integrator import generate_final_response
from steps import initialize_services,ask_llm
from prompter import get_prompt
from steps_new import print_json

from A_query_manager import QueryAnalyzer
from B_decomposer import Decomposer

from C_federator_DB import FederatorDB
from C_federator_places import FederatorPlaces
from C_federator_LLM import FederatorLLM

from steps import run_sql,extract_values

from RD_executor_DB import ExecutorDB
from D_executor_places import ExecutorPlaces
from steps_new import print_json

def main(demo_query):

#Initialize Everything
    initialize_services()

#Query Analyser
    analyzer = QueryAnalyzer()
    intent = analyzer.run(user_query = demo_query)
    print("ANALYSED QUERY")
    print_json(intent)

#Decomposer
    decomposer = Decomposer()
    instructions = decomposer.run_with_raw_query(user_query = demo_query)
    
    print("DECOMPOSER ")
    print_json(instructions)

    db_data = {
        "db_user" : "",
        "db_places" : "",
        "db_llm" : ""
    }

# User DB

#Federator 
    user_id = "147d19b5-3277-4519-a4b0-080042709b14"
    
    federator = FederatorDB(task=instructions["db_user"], user_id=user_id)
    sql = federator.run()
    print("GENERATED SQL")
    # plan = federation_run(instructions, user_id)

    print_json(sql)
    print("SQL RESPONSE")
    # sql = "SELECT spoken_languages,native_language FROM user_details WHERE user_id = '22bb4f93-26a1-4bcd-8c27-5ef7b078d679';"


    sql_output = run_sql(sql,"one")
    db_values = extract_values(sql_output)

    print(db_values)
    db_data["db_user"] = db_values
 

# # LLM DB
#Federator
    data = db_data["db_user"]
    federator = FederatorLLM(db_llm=instructions["db_llm"],data=data)

    db_data["db_llm"] = federator.run()



# # Places API
    print(instructions["db_places"])
    data = db_data["db_llm"]
#Federator
    federator = FederatorPlaces(db_places = instructions["db_places"], data = data)

    poi_queries = federator.run()
    print("[Main] Got POI Queries : ", poi_queries)
#Executor
    executor = ExecutorPlaces(poi_queries)
    places_output = executor.run()

    print("[Main] Extracted Places")
    for p in places_output:
        print(f"#{p.get('name')}")
    print(places_output)

    db_data["db_places"] = places_output
    print(db_data)

    final_answer = generate_final_response(db_data, intent, demo_query)

    with open("final_answer.txt", "w", encoding="utf-8") as f:
        f.write(final_answer)

    print("Saved to final_answer.txt")
if __name__ == "__main__":

    # demo_query = """
    # Plan a 3-day trip to Jaipur for me. I want a balanced pace: moderate in the mornings and leisurely in the afternoons.
    # My interests include history and local cuisine. I will be traveling with my family: 2 adults and 1 child.
    # We prefer to use a private car for transport but are okay with walking short distances.
    # Our budget is around 15000 INR for the entire trip including food, tickets, and transport.
    # I want to make sure we visit the major attractions: Amer Fort, City Palace, Jantar Mantar, Hawa Mahal, and Nahargarh Fort.
    # We will be starting from our hotel “Taj Jai Mahal Palace”.
    # Please provide detailed day-wise itinerary including approximate visit duration at each spot, best times to visit to avoid crowds, travel times between locations, and suggested meal breaks.
    # If possible, recommend a few hidden gems or local eateries near the main attractions.
    # Also, suggest options for evening activities or cultural experiences.
    # """


    
    # demo_query = "Design a travel route that matches my travel pace, includes 3 to 4 major Indian cities, explains the best sequence to visit them, and suggests key attractions in each."

    demo_query =  "Based on my favorite cuisines, tell me the cities where these cuisines are most popular and suggest top-rated restaurants in those cities."
    demo_query = "Find the population and best pizza places in my hometown and my current city"
    demo_query = "List languages I can speak, along with Indian states and countries where they're native. Also, suggest top tourist places in state capitals."

    main(demo_query)