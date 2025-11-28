import json
from steps import ask_llm
from steps_new import clean_llm_json
from prompter import get_prompt

class Decomposer:
    
    def run(self, intent_json: str) -> dict:
        
        intent_json_str = json.dumps(intent_json, indent=2)

        prompt = get_prompt("Decomposer3", intent_json=intent_json_str)

        llm_response = ask_llm(prompt)
        llm_response = clean_llm_json(llm_response)

        try:
            data = json.loads(llm_response)
        except Exception as e:
            raise ValueError(f"LLM returned invalid JSON: {llm_response}") from e

        return data
    def run_with_raw_query(self, user_query: str) -> dict:
        
        prompt = get_prompt("Decomposer2", user_query=user_query)

        llm_response = ask_llm(prompt)
        llm_response = clean_llm_json(llm_response)

        try:
            data = json.loads(llm_response)
        except Exception as e:
            raise ValueError(f"LLM returned invalid JSON: {llm_response}") from e

        return data



if __name__ == "__main__":

    # Your example user query
    user_query = (
        "List languages I can speak, along with Indian states and countries "
        "where they're native. Also, suggest top tourist places in state capitals."
    )
    # user_query = "Find the population and best pizza places in my hometown and my current city"

    user_intent = {
            "intent_summary": "The user wants to retrieve their spoken languages along with the Indian states and countries where those languages are native, and also receive suggestions for top tourist places in Indian state capitals.",
            "entities_requested": [
                {
                    "type": "user_languages",
                    "description": "The languages that the user can speak"
                },
                {
                    "type": "language_native_indian_states",
                    "description": "Indian states where each language is natively spoken"
                },
                {
                    "type": "language_native_countries",
                    "description": "Countries where each language is natively spoken"
                },
                {
                    "type": "indian_state_capitals_tourist_places",
                    "description": "Top tourist places in the capitals of Indian states"
                }
            ],
            "implicit_tasks": [
                "Identify the user's spoken languages.",
                "For each language, determine the Indian states where it is considered a native language.",
                "For each language, determine the countries where it is considered a native language.",
                "Retrieve a list of Indian state capitals.",
                "For each Indian state capital, suggest top tourist places."
            ]
        }

    qm = Decomposer()
    result = qm.run_with_raw_query(user_query)
    # result = qm.run(user_intent)

    print("Breakdown:\n")
    print(json.dumps(result, indent=4))
