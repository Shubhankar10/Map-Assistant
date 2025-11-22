from query_manager import QueryAnalyzer
from decomp import Decomposer
from steps import initialize_services,ask_llm
from flow import FLOW
from new_executor import NewExecute
from prompter import get_prompt

from raw_decomposer import RawQueryDecomposer
from new_federator import NewFederator

def main(demo_query):

#Initialize Everything
    initialize_services()

#Decomposer
    decomposer = RawQueryDecomposer(query=demo_query)
    context = decomposer.run()
    print(f"[MAIN] Context from Decomposer: {context}")



    sample_schema = {
        # --- user table ---
        "first_name": "string",
        "last_name": "string",
        "email": "string",
        "password_hash": "string",
        "created_at": "datetime",

        # --- details table ---
        "dob": "date",
        "gender": "string",
        "aadhar_number": "string",
        "passport_number": "string",
        "driving_license_number": "string",
        "spoken_languages": "list[string]",
        "understood_languages": "list[string]",
        "native_language": "string",
        "hometown": "string",
        "current_city": "string",
        "address": "string",
        "phone_number": "string",
        "home_lat": "float",
        "home_lng": "float",
        "dietary_preferences": "list[string]",

        # --- preferences table ---
        "budget_min": "float",
        "budget_max": "float",
        "transport_pref": "string",
        "commute_pref": "string",
        "pace": "string",
        "travel_duration_preference": "string",
        "travel_group_preference": "string",
        "preferred_regions": "list[string]",
        "season_preference": "string",
        "accommodation_type": "string",
        "special_needs": "string_or_null",
        "frequent_travel": "boolean",

        # --- interests table (list of interest rows) ---
        "tag": "string",
        "sub_tag": "string",
        "preferred_vacation_type": "string",
        "activity_type": "string",
        "frequency_of_interest": "string",
        "special_notes": "string"
    }



    federator = NewFederator(context, sample_schema)
    output = federator.run()

    print("\n=== FINAL OUTPUT ===")
    print(output)   



#Federator and Executor and Integrate

    executor = NewExecute(context=context, user_query=demo_query)
    final = executor.execute()
    
    print(f"[MAIN] Final Output: \n {final}")

    return final 
    
# Render in Streamlit




if __name__ == "__main__":

    demo_query = """
    Plan a 3-day trip to Jaipur for me. I want a balanced pace: moderate in the mornings and leisurely in the afternoons.
    My interests include history and local cuisine. I will be traveling with my family: 2 adults and 1 child.
    We prefer to use a private car for transport but are okay with walking short distances.
    Our budget is around 15000 INR for the entire trip including food, tickets, and transport.
    I want to make sure we visit the major attractions: Amer Fort, City Palace, Jantar Mantar, Hawa Mahal, and Nahargarh Fort.
    We will be starting from our hotel “Taj Jai Mahal Palace”.
    Please provide detailed day-wise itinerary including approximate visit duration at each spot, best times to visit to avoid crowds, travel times between locations, and suggested meal breaks.
    If possible, recommend a few hidden gems or local eateries near the main attractions.
    Also, suggest options for evening activities or cultural experiences.
    """
    demo_query = "I live in Govindpuri, Delhi, and my friend lives in Gurgaon. We are planning to meet for dinner at an Italian restaurant. Please suggest Italian restaurants or cafes that are in a manageable location for both of us"
    
    # demo_query = "I want to go to a Hotel chain called Dashaprakash in Cannought Place Delhi, how is it, what are it's reviews ? is it considerd good for ambienece and north indian food ?"


    # demo_query = "hi How are you, What is your name?"
    main(demo_query)