# execution.py
import json
from typing import Dict, Any, List
from steps import initialize_db_client


class ExecutorDB:
    def __init__(self):
        self._db = None

    # Initialize DB once
    def _ensure_db(self):
        if self._db is None:
            self._db = initialize_db_client()

    # Execute SQL safely
    def _db_query(self, sql: str):
        self._ensure_db()
        db = self._db

        # Try common DB client methods
        for name in ["execute", "query", "fetch_all", "fetchall", "run", "select"]:
            fn = getattr(db, name, None)
            if callable(fn):
                try:
                    return fn(sql)
                except TypeError:
                    try:
                        return fn(sql, None)
                    except:
                        continue
                except:
                    continue

        # Raw connection fallback
        conn = getattr(db, "conn", None) or getattr(db, "connection", None)
        if conn:
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            if cur.description:
                cols = [d[0] for d in cur.description]
                return [dict(zip(cols, r)) for r in rows]
            return rows

        raise RuntimeError("DB query method not found in DB client.")

    # Run db_user SQL tasks
    def _execute_db_user(self, db_user_sql: List[Dict[str, str]]):
        results = []

        for item in db_user_sql:
            sql = item["sql"]
            task = item["task"]
    
            print(f"[Execution] Running SQL for: {task}")
            try:
                rows = self._db_query(sql)

                # Convert rows to a simple string value
                values = []
                if isinstance(rows, list):
                    for r in rows:
                        if isinstance(r, dict):
                            for v in r.values():
                                # flatten arrays/lists
                                if isinstance(v, (list, tuple)):
                                    values.extend([str(x) for x in v])
                                else:
                                    values.append(str(v))
                        else:
                            # tuple or scalar
                            if isinstance(r, (list, tuple)):
                                values.extend([str(x) for x in r])
                            else:
                                values.append(str(r))

                # Remove duplicates and join
                deduped = list(dict.fromkeys(values))
                value_string = ", ".join(deduped)

                results.append({
                    "task": task,
                    "sql": sql,
                    "rows": rows,
                    "value_string": value_string
                })

            except Exception as e:
                results.append({
                    "task": task,
                    "sql": sql,
                    "error": str(e)
                })

        return results

    # Main entry-point
    def run(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        print("[Execution] Starting minimal execution engine...")

        db_user_plan = plan.get("db_user_sql", [])

        result = {
            "db_user_results": self._execute_db_user(db_user_plan)
        }

        print("[Execution] Done.")
        return result


def run(plan: Dict[str, Any]) -> Dict[str, Any]:
    engine = ExecutorDB()
    return engine.run(plan)
