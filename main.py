from steps import initialize_services,ask_llm
from prompter import get_prompt
from steps_new import print_json

from A_query_manager import QueryAnalyzer
from B_decomposer import Decomposer
from federation import run as federation_run
from execution import run as execution_run
from steps_new import print_json

def main(demo_query):

#Initialize Everything
    initialize_services()

#Query Analyser
    analyzer = QueryAnalyzer()
    intent = analyzer.run(user_query = demo_query)
    print("User Intent")
    print_json(intent)
#Decomposer
    decomposer = Decomposer()
    instructions = decomposer.run_with_raw_query(user_query = demo_query)
    
    print("Instructions ")
    print_json(instructions)

#Federator 
    user_id = "cf96c65d-2bbe-4384-82b5-118badd2892f"
    plan = federation_run(instructions, user_id)

    print("\nFEDERATION PLAN")
    print_json(plan)

# Execute plan 
    result = execution_run(plan)
    print("\nEXECUTION RESULT")
    print_json(result)


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


    
    demo_query = (
        "List languages I can speak, along with Indian states and countries "
        "where they're native. Also, suggest top tourist places in state capitals."
    )

    # demo_query =  "Based on my favorite cuisines, tell me the cities where these cuisines are most popular and suggest top-rated restaurants in those cities."


    main(demo_query)