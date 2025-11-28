from steps import ask_llm
from D_executor_places import ExecutorPlaces

class FederatorPlaces:
    def __init__(self, db_places: list, data : str):
        self.data = data
        self.db_places = db_places

    def build_prompt(self):
        prompt = f"""
You are an API Query Generator for Google Places API.

### INPUT
High-level instructions describing what places need to be fetched:
{self.db_places} + "{self.data}"

### YOUR TASK
Convert each instruction into **direct, minimal, and executable Google Places API query strings.**

### RULES
- Output ONLY a JSON list of strings. No explanation.
- Each string must be a clean, direct Google Places query.
- Avoid repetition. Combine logically when possible.
- Use standard Places API-friendly phrasing:
    - "Top tourist places in <city>"
    - "Popular attractions in <city>"
    - "Nearby cafes to <landmark>"
    - "Famous monuments in <city>"
- Keep queries short, precise, and ready for API calls.

### OUTPUT FORMAT Example
[
  "Top tourist places in Jaipur",
  "Famous attractions in Mumbai"
]

"""
        return prompt

    # -----------------------------------------------------------
    # Run (calls LLM once)
    # -----------------------------------------------------------
    def run(self):
        prompt = self.build_prompt()
        response = ask_llm(prompt)
        print("[FederatorPlaces] Queries Made")

        if isinstance(response, str):
            try:
                import json
                response = json.loads(response)
            except Exception:
                raise ValueError("LLM returned invalid JSON. Expected a list of strings.")

        if not isinstance(response, list):
            raise TypeError(f"FederatorPlaces.run() expected List[str] but got: {type(response)}")

        cleaned = [str(item).strip() for item in response if item]

        return cleaned


if __name__ == "__main__":

    # Given input for Federator
    federator_input = {
        "db_user": [
            "Retrieve the list of languages I can speak."
        ],
        "db_llm": [
            "For each language retrieved from the user profile, find the Indian states where it is natively spoken.",
            "For each language retrieved from the user profile, find the countries where it is an official or native language.",
            "Identify the capital city for each Indian state found in the previous step."
        ],
        "db_places": [
            "For each capital city identified by the LLM, find the top tourist places and attractions. cities : Hyderabad"
            # "List Cities where Haldirams has an outlet"
        ]
    }



    federator = FederatorPlaces(
        db_places = federator_input["db_places"],
    )

    final_queries = federator.run()

    print("\n=== FINAL QUERY LIST ===")
    print(final_queries)
    print(type(final_queries))

    executor = ExecutorPlaces(final_queries)
    output = executor.run()

    print(output)
