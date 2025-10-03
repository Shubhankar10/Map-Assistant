from query_manager import QueryAnalyzer
from decomp import Decomposer
from steps import initialize_services

if __name__ == "__main__":

    demo_query = """
    Plan a 3-day trip to Jaipur for me. I want a balanced pace: moderate in the mornings and leisurely in the afternoons.
    My interests include history, architecture, and local cuisine. I will be traveling with my family: 2 adults and 1 child.
    We prefer to use a private car for transport but are okay with walking short distances.
    Our budget is around 15000 INR for the entire trip including food, tickets, and transport.
    I want to make sure we visit the major attractions: Amer Fort, City Palace, Jantar Mantar, Hawa Mahal, and Nahargarh Fort.
    We will be starting from our hotel “Taj Jai Mahal Palace”.
    Please provide detailed day-wise itinerary including approximate visit duration at each spot, best times to visit to avoid crowds, travel times between locations, and suggested meal breaks.
    If possible, recommend a few hidden gems or local eateries near the main attractions.
    Also, suggest options for evening activities or cultural experiences.
    Finally, provide a concise summary narration explaining the trade-offs and reasoning for the itinerary.
    """


#Initialize Everything
    initialize_services()

#Query Analyser
    analyzer = QueryAnalyzer()
    selected_task = analyzer.select_task(demo_query)
    print(f"[MAIN] Selected Task: {selected_task}")

#Decomposer
    decomposer = Decomposer(query=demo_query, task=selected_task)
    context = decomposer.run()

#Get Flow

#Federator and Executor

#Integrate

