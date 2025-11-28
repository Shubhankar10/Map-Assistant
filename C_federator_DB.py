# federation.py
import os
import re
import json
from typing import Dict, Any, List, Optional

from steps import ask_llm
from steps_new import clean_llm_json

# Paths
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "Schema.md")
OUT_PLAN_PATH = os.path.join(os.getcwd(), "last_sql_plan.json")

SQL_PROMPT_TEMPLATE = """
You are an expert PostgreSQL query generator.

### TASK
Convert the following natural-language instruction into ONE single valid SQL SELECT query.

### RULES
- Return ONLY the SQL query.
- Use ONLY the tables and columns present in the schema.
- Always filter with: user_id = '{user_id}'
- Use explicit SELECT columns when possible.
- Use correct JOINs based on schema foreign keys.
- End the query with a semicolon.

### DATABASE SCHEMA
{schema}

### NATURAL LANGUAGE REQUEST
"{task}"

### OUTPUT
SQL query only.
"""


LLM_PROMPT_TEMPLATE = """
You are a Knowledge Extraction LLM.

TASK:
{task}

INSTRUCTIONS:
1. The user has provided data for placeholders (if any).
2. Replace placeholders conceptually and provide the ACTUAL REAL-WORLD DATA requested.
3. Do NOT provide a schema. Provide the list of answers.

EXAMPLE:
If task is "Capital of <state>" and input is "Texas", output: {{"result": ["Austin"]}}

OUTPUT FORMAT (JSON):
{{
  "task": "{task}",
  "results": ["item1", "item2", ...]
}}
"""


# # db_places query template snippets (we'll combine into text-search queries)
# PLACES_QUERY_SNIPPETS = {
#     "restaurant_by_cuisine_in_city": "Top-rated restaurants serving {cuisine} in {city}",
#     "popular_cuisine_in_city": "Cities where {cuisine} is most popular",
#     "top_attractions_in_city": "Top tourist attractions in {city}",
# }


class FederatorDB:
    def __init__(self, schema_path: Optional[str] = None):
        self.schema_path = schema_path or SCHEMA_PATH
        self.schema_text = self._load_schema(self.schema_path)

    def _load_schema(self, path: str) -> str:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return "-- Schema file missing."

    def _clean_sql_from_response(self, response: str) -> str:
        if response is None:
            return ""

        m = re.search(r'```(?:sql)?\s*([\s\S]*?)\s*```', response, re.IGNORECASE)
        if m:
            sql = m.group(1).strip()
        else:
            sql = response.strip()

        sql = re.sub(r'^\s*SQL:\s*', '', sql, flags=re.IGNORECASE)
        sql = sql.replace("```", "").replace("`", "").strip()

        if ";" in sql:
            sql = sql.split(";", 1)[0].strip() + ";"
        else:
            sql = sql + ";"

        return sql

    def _nl_to_sql(self, task: str, user_id: str) -> str:
        prompt = self.SQL_PROMPT_TEMPLATE.format(schema=self.schema_text, task=task, user_id=user_id)
        prompt += (
            "\n\nIMPORTANT:\n"
            "Return ONLY the SQL statement.\n"
            "Do NOT wrap SQL in ``` code fences.\n"
            "Do NOT include any explanations or text outside the SQL.\n"
        )
        raw = self.ask_llm(prompt)
        sql = self._clean_sql_from_response(raw)
        return sql

    def _process_db_user(self, tasks: List[str], user_id: str) -> List[Dict[str, str]]:
        out = []
        for t in tasks:
            sql = self._nl_to_sql(t, user_id)
            out.append({"task": t, "sql": sql})
        return out


    def run(self, decomposed: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        print("\n[Federator][DB] Run")
        result = {
            "db_user_sql": []
        }

        db_user_tasks = decomposed.get("db_user", [])
        if db_user_tasks:
            print(f"[Federator] Processing {len(db_user_tasks)} db_user task(s)...")
            try:
                db_user_plan = self._process_db_user(db_user_tasks, user_id)
                for item in db_user_plan:
                    print(f"[Federator] SQL for task: {item['task']}\n{item['sql']}\n")
                result["db_user_sql"] = db_user_plan
            except Exception as e:
                print(f"[Federator] ERROR processing db_user tasks: {e}")
        else:
            print("[Federator] No db_user tasks to process.")

        print("[Federator] run() complete.\n")
        return result



# -------------------- Module-level wrapper --------------------

def run(decomposed_json: Dict[str, Any], user_id: str):
    federator = FederatorDB()
    return federator.run(decomposed_json, user_id)



# -------------------- main() for quick testing --------------------

def main():
    demo_instructions = {
        "db_user": [
            "Retrieve my favorite cuisines.",
            # "Retrieve the list of languages the user is familiar with."
        ],
        "db_llm": [
            "For the cuisines <favorite_cuisines>, determine the cities where each cuisine is most popular.",
            # "Identify languages widely spoken in <states>."
        ],
        "db_places": [
            "Find top-rated restaurants in <cities> that serve <favorite_cuisines>.",
            # "List top tourist attractions in <cities>."
        ]
    }

    demo_user_id = "REPLACE_WITH_REAL_USER_ID"

    print("[Federator:main] Running federator on demo instructions...")
    plan = run(demo_instructions, demo_user_id)

    print("\n[Final plan (summary)]:")
    print(json.dumps(plan, indent=2))


if __name__ == "__main__":
    main()
