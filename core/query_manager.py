# Konse class ko kaha call karna hai       
from apis.llm_interface import LLMClient
import os

class QueryAnalyzer:
    """
    Pipeline to analyze user queries and break them into subtasks using LLM.
    """

    def __init__(self):
        print("[QueryAnalyzer] Initializing...")
        self.llm = LLMClient()

    def decompose_query(self, user_query: str):
        """
        Send the user query to the LLM to generate subtasks.
        """
        print(f"[QueryAnalyzer] Received query: {user_query}")

        prompt = f"""
        You are a query decomposition assistant.
        The user gave this query:
        "{user_query}"

        Break it down into a clear, ordered list of subtasks that a travel assistant system 
        should perform to answer the query. 
        Only output the subtasks in sequence.
        """

        response = self.llm.query(prompt)

        print("\n[QueryAnalyzer] Subtasks generated:\n")
        print(response)
        return response


if __name__ == "__main__":
    # Hardcoded demo query
    demo_query = "My friend is in location A and I am in location B, find cafes where both of us travel roughly equal distance."


    analyzer = QueryAnalyzer()
    analyzer.decompose_query(demo_query)
