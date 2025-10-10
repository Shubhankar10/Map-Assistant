from query_manager import QueryAnalyzer
from decomp import Decomposer
from steps import initialize_services,ask_llm
from flow import FLOW
from executor import Execute
from prompter import get_prompt


def main(demo_query):

#Initialize Everything
    initialize_services()

#Query Analyser
    analyzer = QueryAnalyzer()
    selected_task = analyzer.select_task(demo_query)
    print(f"[MAIN] Selected Task: {selected_task}")

    if selected_task == "NoneOfThese":
        return ask_llm(get_prompt("NoneOfThese", user_query=demo_query))
#Decomposer
    decomposer = Decomposer(query=demo_query, task=selected_task)
    context = decomposer.run()

#Get Flow
    flow = FLOW.get(selected_task, [])
    print(f"[MAIN] Flow Steps fetched for '{selected_task}'")


#Federator and Executor and Integrate

    executor = Execute(selected_task=selected_task, flow=flow, context=context, user_query=demo_query)
    final = executor.execute()
    
    print(f"[MAIN] Final Output for {selected_task}: \n {final}")

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
    # demo_query = "I live in Govindpuri, Delhi, and my friend lives in Gurgaon. We are planning to meet for dinner at an Italian restaurant. I cannot travel long distances, and my friend will be using the metro. Please suggest Italian restaurants or cafes that are in a manageable location for both of us"
    
    # demo_query = "hi How are you, What is your name?"
    main(demo_query)