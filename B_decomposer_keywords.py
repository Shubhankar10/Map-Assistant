import re
import json

class Decomposer:

    def __init__(self):
        # Keyword heuristics for DB classification
        self.db_user_keywords = [
            "user", "my", "me", "profile", "account", "saved", "preferences"
        ]

        self.db_places_keywords = [
            "place", "places", "poi", "tourist", "restaurant", "hotel",
            "attraction", "nearby", "near me", "city", "capital"
        ]

        self.db_llm_keywords = [
            "identify", "determine", "find out", "countries", "states",
            "origin", "native", "capital", "relationships", "mapping"
        ]

    def classify(self, text: str) -> str:
        t = text.lower()

        # DB_USER
        if any(kw in t for kw in self.db_user_keywords):
            return "db_user"

        # DB_PLACES
        if any(kw in t for kw in self.db_places_keywords):
            return "db_places"

        # DB_LLM
        if any(kw in t for kw in self.db_llm_keywords):
            return "db_llm"

        # Default fallback: reasoning
        return "db_llm"

    def decompose(self, intent_json: dict) -> dict:

        output = { "db_user": [], "db_places": [], "db_llm": [] }

        # Process entities_requested
        for entity in intent_json.get("entities_requested", []):
            desc = entity.get("description", "")
            target_db = self.classify(desc)

            # Use placeholder-friendly normalized task
            task = f"{desc} (requires resolving {{placeholders}})"

            output[target_db].append(task)

        # Process implicit tasks
        for task in intent_json.get("implicit_tasks", []):
            target_db = self.classify(task)
            output[target_db].append(task)

        # Deduplicate
        for k in output:
            output[k] = list(dict.fromkeys(output[k]))

        return output



intent_json = {
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


# Run the test
if __name__ == "__main__":
    decomposer = Decomposer()
    result = decomposer.decompose(intent_json)

    print("\n=== FINAL DECOMPOSED DB TASKS ===\n")
    print(json.dumps(result, indent=4))
