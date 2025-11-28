# federator_db.py
import os
import re
from typing import Optional
from steps import ask_llm


SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "Schema.md")


class FederatorDB:
    def __init__(self, task: str, user_id: str, schema_path: Optional[str] = None):
        """
        task: A single db_user instruction (string)
        user_id: UUID of user
        """
        self.task = task
        self.user_id = user_id
        self.schema_path = schema_path or SCHEMA_PATH
        self.schema_text = self._load_schema()

    # -------------------------------------------------------
    # Load schema markdown
    # -------------------------------------------------------
    def _load_schema(self) -> str:
        try:
            with open(self.schema_path, "r", encoding="utf-8") as f:
                return f.read()
        except:
            return "-- ERROR: Schema.md missing."

    # -------------------------------------------------------
    # Build SQL prompt
    # -------------------------------------------------------
    def _build_prompt(self) -> str:
        return f"""
You are an expert PostgreSQL query generator.

### TASK
Convert the following natural-language request into EXACTLY ONE SQL SELECT query:

"{self.task}"

### CONSTRAINTS
- Use ONLY the tables/columns from the schema.
- MUST filter using: user_id = '{self.user_id}'
- MUST end the SQL with a semicolon.
- NO explanations.
- NO markdown.
- NO code fences.
- Output ONLY the SQL query.

### DATABASE SCHEMA
{self.schema_text}
"""

    # -------------------------------------------------------
    # Clean SQL returned by LLM
    # -------------------------------------------------------
    @staticmethod
    def _clean_sql(raw: str) -> str:
        if not raw:
            return ""

        sql = raw.strip()

        # Remove ```sql blocks if present
        m = re.search(r'```(?:sql)?\s*([\s\S]*?)```', sql, re.I)
        if m:
            sql = m.group(1).strip()

        sql = re.sub(r"^\s*SQL:\s*", "", sql, flags=re.I)
        sql = sql.replace("```", "").strip()

        # Ensure single semicolon at end
        if ";" in sql:
            sql = sql.split(";", 1)[0].strip()
        sql = sql + ";"

        return sql

    # -------------------------------------------------------
    # Validate SQL correctness (simple heuristic checks)
    # -------------------------------------------------------
    @staticmethod
    def _check_sql(sql: str) -> bool:
        if not sql.lower().startswith("select"):
            return False
        if " from " not in sql.lower():
            return False
        if "user_id" not in sql.lower():
            return False
        if not sql.endswith(";"):
            return False
        return True

    # -------------------------------------------------------
    # Run → Build prompt → LLM → Clean SQL → Validate → Return SQL
    # -------------------------------------------------------
    def run(self) -> str:
        prompt = self._build_prompt()
        raw = ask_llm(prompt)
        cleaned = self._clean_sql(raw)

        if not self._check_sql(cleaned):
            raise ValueError(f"Invalid SQL generated:\n{cleaned}")

        return cleaned


# -------------------------------------------------------
# MAIN TEST
# -------------------------------------------------------
if __name__ == "__main__":

    demo_task = "Fetch my gender."
    demo_user_id = "22bb4f93-26a1-4bcd-8c27-5ef7b078d679"

    federator = FederatorDB(task=demo_task, user_id=demo_user_id)
    sql = federator.run()

    print("\n=== FINAL SQL ===")
    print(sql)
