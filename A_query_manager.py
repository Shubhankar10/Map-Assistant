import json
from steps import ask_llm

from steps_new import clean_llm_json

class QueryAnalyzer:


    def _build_prompt(self, user_query: str) -> str:
        """
        Builds a prompt to expand the user's question into a structured,
        database-agnostic intent breakdown.
        """

        return f"""
You are an Intent Analysis AI.

Your job is to take the user's query and expand it into a structured JSON
representing what the user *actually* wants. This is NOT about deciding
which database will be used. Only identify the meaning and requested data.

### Required Output Format  
Return STRICT JSON with this structure:

{{
  "intent_summary": "A short summary explaining what the user wants overall",

  "entities_requested": [
    {{
      "type": "short_machine_label",
      "description": "Human-readable description"
    }}
  ],

  "implicit_tasks": [
    "List of detailed atomic tasks required to fulfill the user's query"
  ]
}}

### Rules  
- Do NOT mention any databases (DB1, DB2, etc.).  
- Do NOT create execution steps; only describe intended data.  
- Keep tasks atomic, independent, and NOT chained.  
- If needed data is unknown, describe it generically (e.g., "user's languages").  
- Output MUST be valid JSON. No markdown.

### USER QUERY
\"\"\"{user_query}\"\"\"
"""

    def run(self, user_query: str) -> dict:
        """
        Sends prompt to LLM and returns a parsed JSON dictionary.
        Raises ValueError if LLM output is not valid JSON.
        """

        prompt = self._build_prompt(user_query)
        llm_response = ask_llm(prompt)
        llm_response = clean_llm_json(llm_response)

        try:
            parsed = json.loads(llm_response)
        except Exception as e:
            raise ValueError(f"LLM returned invalid JSON: {llm_response}") from e

        return parsed



if __name__ == "__main__":

    # Your example user query
    user_query = (
        "List languages I can speak, along with Indian states and countries "
        "where they're native. Also, suggest top tourist places in state capitals."
    )

    qm = QueryAnalyzer()
    result = qm.run(user_query)


    print("Breakdown:\n")
    print(json.dumps(result, indent=4))
    
