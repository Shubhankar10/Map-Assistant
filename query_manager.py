from prompter import get_prompt
from steps import ask_llm

class QueryAnalyzer:

    TASKS = [
        "TripSuggestion",
        "ItineraryPlanner",
        "ReviewSummarizer",
        "MeetingPointPlanner",
        "RouteOptimizer",
        "TripJournalManager",
        "NoneOfThese"
    ]

    def __init__(self):
        print("[QueryAnalyzer] Initializing...")

    def select_task(self, user_query: str) -> str:
        print(f"[QueryAnalyzer] Received query.")

        prompt = get_prompt("query_analyser", user_query=user_query, tasks=', '.join(self.TASKS))
        print(f"[QueryAnalyzer] Modified prompt. Sending to LLM...")

        response = ask_llm(prompt).strip()
        print(f"[QueryAnalyzer] LLM response received.")

        # Set Default to TripSuggestion if unexpected output
        if response not in self.TASKS:
            print(f"[QueryAnalyzer] Warning: LLM returned unexpected task '{response}', defaulting to TripSuggestion.")
            response = "TripSuggestion"

        print(f"[QueryAnalyzer] Selected task: {response}")
        return response
    


if __name__ == "__main__":
    demo_query = "Me and My Freind want to meet in delhi, suggest some cafes."

    analyzer = QueryAnalyzer()
    selected_task = analyzer.select_task(demo_query)

