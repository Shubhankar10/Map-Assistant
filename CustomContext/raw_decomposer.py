# raw_query_decomposer.py
import json
import re
from typing import Dict

from steps import ask_llm


class RawQueryDecomposer:
    def __init__(self, query: str):
        print("[RawQueryDecomposer] Initializing...")
        self.query = query
        self.prompt = self.build_prompt()

    def build_prompt(self) -> str:
        """
        Builds the inline prompt for the LLM.
        """
        return f"""
You are a task understanding engine. 
Given the user's raw natural-language query, analyze it deeply and produce a clean JSON object.

Your goals:
1. Determine the exact task the user is asking for.  
2. Extract all relevant details required to complete the task.  
3. Include additional fields that are important for completing the task, 
   even if the user did not explicitly provide them.  
4. Mark any missing but important values as null.  
5. Identify and list all mandatory fields required for the task.
6. Return only the empty JSON object without any filled detials.

Your JSON MUST contain these generic mandatory fields:
- task_type          (string)
- original_query     (string)
- user_intent        (string summary)
- mandatory_fields   (list)
- details            (object with extracted + inferred fields)

Rules:
- If a field is important for the user’s task but is NOT present in the query, include it with value null.
- Do NOT include any extra text outside the JSON.
- Always return strict, valid JSON.
- Make sure the determine the task accurately and include only relevant fields for that task.

User Query:
\"\"\"{self.query}\"\"\"
"""

    def extract_json(self, llm_response: str) -> Dict:
        """
        Safely extracts JSON object from LLM response using regex.
        """
        match = re.search(r'\{.*\}', llm_response, flags=re.DOTALL)
        if not match:
            raise ValueError(
                f"[Error] Could not extract JSON from LLM response:\n{llm_response}"
            )

        cleaned = match.group(0)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"[Error] JSON decode failed: {e}\nLLM response:\n{llm_response}"
            )

    def run(self) -> Dict:
        """
        Sends the inline prompt to the LLM, extracts JSON, and returns it.
        """
        print("[RawQueryDecomposer] Sending prompt to LLM...")
        llm_response = ask_llm(self.prompt)

        print("[RawQueryDecomposer] LLM response received. Extracting JSON...")
        context = self.extract_json(llm_response)

        print("[RawQueryDecomposer] Final JSON context prepared.\n")
        return context


if __name__ == "__main__":
    demo_query = "Plan a 2 day itinerary in Jaipur covering Amer Fort and City Palace with a budget of 5000 INR."
    
    # demo_query = "I live in Govindpuri, Delhi, and my friend lives in Gurgaon. We are planning to meet for dinner at an Italian restaurant. Please suggest Italian restaurants or cafes that are in a manageable location for both of us, I'll be travelling by Cab and my friend by metro"
    
    # demo_query = "I want to go to a Hotel chain called Dashaprakash in Cannought Place Delhi, how is it, what are it's reviews ? is it considerd good for ambienece and north indian food ?"

    decomposer = RawQueryDecomposer(query=demo_query)
    context = decomposer.run()

    print("\n[Final Context Returned]")
    print(json.dumps(context, indent=2))
