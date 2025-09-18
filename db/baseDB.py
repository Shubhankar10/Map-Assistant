# db_manager.py
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Optional, Any, Dict, List, Tuple


class PostgresDB:
    def __init__(self, host: str, dbname: str, user: str, password: str, port: int = 5432):
        self.host = host
        self.dbname = dbname
        self.user = user
        self.password = password
        self.port = port
        self.conn: Optional[psycopg2.extensions.connection] = None
        self.cursor: Optional[RealDictCursor] = None

    # ---------------- Connection ---------------- #
    def connect(self, schema: Optional[str] = None):
        """
        Connect to the database. Optionally set search_path to `schema`.
        If schema is None, default 'public' schema will be used.
        """
        try:
            self.conn = psycopg2.connect(
                host=self.host, dbname=self.dbname, user=self.user, password=self.password, port=self.port
            )
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            if schema:
                # safe param: schema name should be validated if user input in prod
                self.cursor.execute(f"SET search_path TO {schema};")
                print(f"📂 Schema set to: {schema}")
            print("✅ Database connected successfully")
        except Exception as e:
            print("❌ Connection failed:", e)
            raise

    def close(self):
        """Close cursor and connection."""
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
            print("🔒 Connection closed")
        except Exception as e:
            print("❌ Error on close:", e)

    @contextmanager
    def transaction(self):
        """
        Context manager to run multiple operations in one transaction.
        Usage:
            with db.transaction():
                db.add_user(...)
                db.add_trip(...)
        """
        if not self.conn:
            raise RuntimeError("Not connected")
        try:
            yield
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    # ---------------- Generic Executor ---------------- #
    def execute_query(self, query: str, values: Optional[Tuple[Any, ...]] = None,
                      fetchone: bool = False, fetchall: bool = False) -> Any:
        """
        Generic executor for queries.
        - If fetchone=True -> returns dict or None
        - If fetchall=True -> returns list[dict] or []
        - Otherwise returns cursor.rowcount for DML (UPDATE/DELETE)
        """
        if not self.cursor:
            raise RuntimeError("DB cursor not initialized. Call connect() first.")
        try:
            self.cursor.execute(query, values or ())
            # fetch before commit (so RETURNING works)
            result = None
            if fetchone:
                result = self.cursor.fetchone()
            elif fetchall:
                result = self.cursor.fetchall()
            # commit after fetch
            self.conn.commit()
            if fetchone or fetchall:
                return result
            return self.cursor.rowcount
        except Exception as e:
            # rollback and bubble up error as helpful message
            if self.conn:
                self.conn.rollback()
            print("❌ Query failed:", e)
            raise

    # ------------------- USERS ------------------- #
    def add_user(self, name: str, email: str, password_hash: str, timezone: Optional[str] = None) -> Dict:
        q = """
            INSERT INTO users (name, email, password_hash, timezone)
            VALUES (%s, %s, %s, %s) RETURNING *;
        """
        return self.execute_query(q, (name, email, password_hash, timezone), fetchone=True)

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        return self.execute_query("SELECT * FROM users WHERE user_id = %s;", (user_id,), fetchone=True)

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        return self.execute_query("SELECT * FROM users WHERE email = %s;", (email,), fetchone=True)

    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        return self.execute_query("SELECT * FROM users ORDER BY created_at DESC LIMIT %s OFFSET %s;", (limit, offset), fetchall=True)

    def update_user(self, user_id: int, fields: Dict[str, Any]) -> int:
        """
        Update user columns provided in `fields` dict. Returns affected rowcount.
        Example: update_user(3, {"name": "New", "timezone": "Asia/Kolkata"})
        """
        if not fields:
            return 0
        set_clause = ", ".join([f"{k} = %s" for k in fields.keys()])
        values = tuple(fields.values()) + (user_id,)
        query = f"UPDATE users SET {set_clause} WHERE user_id = %s;"
        return self.execute_query(query, values)

    def delete_user(self, user_id: int) -> int:
        return self.execute_query("DELETE FROM users WHERE user_id = %s;", (user_id,))

    # ------------------- USER PREFERENCES ------------------- #
    def add_user_pref(self, user_id: int, budget_min: Optional[int], budget_max: Optional[int],
                      transport_pref: Optional[str], pace: Optional[str]) -> Dict:
        q = """
            INSERT INTO user_preferences (user_id, budget_min, budget_max, transport_pref, pace)
            VALUES (%s, %s, %s, %s, %s) RETURNING *;
        """
        return self.execute_query(q, (user_id, budget_min, budget_max, transport_pref, pace), fetchone=True)

    def get_pref_by_id(self, pref_id: int) -> Optional[Dict]:
        return self.execute_query("SELECT * FROM user_preferences WHERE pref_id = %s;", (pref_id,), fetchone=True)

    def get_prefs_by_user(self, user_id: int) -> List[Dict]:
        return self.execute_query("SELECT * FROM user_preferences WHERE user_id = %s;", (user_id,), fetchall=True)

    def update_pref(self, pref_id: int, fields: Dict[str, Any]) -> int:
        if not fields:
            return 0
        set_clause = ", ".join([f"{k} = %s" for k in fields.keys()])
        values = tuple(fields.values()) + (pref_id,)
        query = f"UPDATE user_preferences SET {set_clause} WHERE pref_id = %s;"
        return self.execute_query(query, values)

    def delete_pref(self, pref_id: int) -> int:
        return self.execute_query("DELETE FROM user_preferences WHERE pref_id = %s;", (pref_id,))

    # ------------------- USER INTERESTS ------------------- #
    def add_interest(self, user_id: int, tag: str) -> Dict:
        q = "INSERT INTO user_interests (user_id, tag) VALUES (%s, %s) RETURNING *;"
        return self.execute_query(q, (user_id, tag), fetchone=True)

    def get_interest_by_id(self, interest_id: int) -> Optional[Dict]:
        return self.execute_query("SELECT * FROM user_interests WHERE interest_id = %s;", (interest_id,), fetchone=True)

    def get_interests_by_user(self, user_id: int) -> List[Dict]:
        return self.execute_query("SELECT * FROM user_interests WHERE user_id = %s ORDER BY interest_id;", (user_id,), fetchall=True)

    def update_interest(self, interest_id: int, tag: str) -> int:
        return self.execute_query("UPDATE user_interests SET tag = %s WHERE interest_id = %s;", (tag, interest_id))

    def delete_interest(self, interest_id: int) -> int:
        return self.execute_query("DELETE FROM user_interests WHERE interest_id = %s;", (interest_id,))

    # ------------------- TRIPS ------------------- #
    def add_trip(self, user_id: int, title: Optional[str], city: Optional[str],
                 start_date: Optional[str], end_date: Optional[str], status: str = "draft") -> Dict:
        q = """
            INSERT INTO trips (user_id, title, city, start_date, end_date, status)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING *;
        """
        return self.execute_query(q, (user_id, title, city, start_date, end_date, status), fetchone=True)

    def get_trip_by_id(self, trip_id: int) -> Optional[Dict]:
        return self.execute_query("SELECT * FROM trips WHERE trip_id = %s;", (trip_id,), fetchone=True)

    def get_trips_by_user(self, user_id: int) -> List[Dict]:
        return self.execute_query("SELECT * FROM trips WHERE user_id = %s ORDER BY start_date;", (user_id,), fetchall=True)

    def get_all_trips(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        return self.execute_query("SELECT * FROM trips ORDER BY created_at DESC LIMIT %s OFFSET %s;", (limit, offset), fetchall=True)

    def update_trip(self, trip_id: int, fields: Dict[str, Any]) -> int:
        if not fields:
            return 0
        set_clause = ", ".join([f"{k} = %s" for k in fields.keys()])
        values = tuple(fields.values()) + (trip_id,)
        query = f"UPDATE trips SET {set_clause} WHERE trip_id = %s;"
        return self.execute_query(query, values)

    def delete_trip(self, trip_id: int) -> int:
        return self.execute_query("DELETE FROM trips WHERE trip_id = %s;", (trip_id,))

    def get_trips_in_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        q = "SELECT * FROM trips WHERE start_date >= %s AND end_date <= %s ORDER BY start_date;"
        return self.execute_query(q, (start_date, end_date), fetchall=True)

    def get_recent_trips(self, limit: int = 10) -> List[Dict]:
        return self.execute_query("SELECT * FROM trips ORDER BY created_at DESC LIMIT %s;", (limit,), fetchall=True)

    def search_trips_by_city(self, city: str) -> List[Dict]:
        return self.execute_query("SELECT * FROM trips WHERE city ILIKE %s ORDER BY start_date;", (f"%{city}%",), fetchall=True)

    # ------------------- ITINERARIES ------------------- #
    def add_itinerary(self, trip_id: int, day: int, order_index: int,
                      poi_name: str, poi_address: Optional[str],
                      start_time: Optional[str], end_time: Optional[str],
                      notes: Optional[str]) -> Dict:
        q = """
            INSERT INTO itineraries (trip_id, day, order_index, poi_name, poi_address, start_time, end_time, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *;
        """
        return self.execute_query(q, (trip_id, day, order_index, poi_name, poi_address, start_time, end_time, notes), fetchone=True)

    def get_itinerary_by_id(self, itinerary_id: int) -> Optional[Dict]:
        return self.execute_query("SELECT * FROM itineraries WHERE itinerary_id = %s;", (itinerary_id,), fetchone=True)

    def get_itineraries_by_trip(self, trip_id: int) -> List[Dict]:
        return self.execute_query("SELECT * FROM itineraries WHERE trip_id = %s ORDER BY day, order_index;", (trip_id,), fetchall=True)

    def get_itineraries_by_trip_and_day(self, trip_id: int, day: int) -> List[Dict]:
        return self.execute_query("SELECT * FROM itineraries WHERE trip_id = %s AND day = %s ORDER BY order_index;", (trip_id, day), fetchall=True)

    def update_itinerary(self, itinerary_id: int, fields: Dict[str, Any]) -> int:
        if not fields:
            return 0
        set_clause = ", ".join([f"{k} = %s" for k in fields.keys()])
        values = tuple(fields.values()) + (itinerary_id,)
        query = f"UPDATE itineraries SET {set_clause} WHERE itinerary_id = %s;"
        return self.execute_query(query, values)

    def delete_itinerary(self, itinerary_id: int) -> int:
        return self.execute_query("DELETE FROM itineraries WHERE itinerary_id = %s;", (itinerary_id,))

    # ------------------- TRIP JOURNALS ------------------- #
    def add_journal(self, trip_id: int, day: Optional[int], entry_text: str, photos: Optional[str] = None) -> Dict:
        q = """
            INSERT INTO trip_journals (trip_id, day, entry_text, photos)
            VALUES (%s, %s, %s, %s) RETURNING *;
        """
        return self.execute_query(q, (trip_id, day, entry_text, photos), fetchone=True)

    def get_journal_by_id(self, journal_id: int) -> Optional[Dict]:
        return self.execute_query("SELECT * FROM trip_journals WHERE journal_id = %s;", (journal_id,), fetchone=True)

    def get_journals_by_trip(self, trip_id: int) -> List[Dict]:
        return self.execute_query("SELECT * FROM trip_journals WHERE trip_id = %s ORDER BY created_at;", (trip_id,), fetchall=True)

    def get_journals_by_user(self, user_id: int) -> List[Dict]:
        # Join journals -> trips to filter by user owner
        q = """
            SELECT j.* FROM trip_journals j
            JOIN trips t ON j.trip_id = t.trip_id
            WHERE t.user_id = %s
            ORDER BY j.created_at;
        """
        return self.execute_query(q, (user_id,), fetchall=True)

    def update_journal(self, journal_id: int, fields: Dict[str, Any]) -> int:
        if not fields:
            return 0
        set_clause = ", ".join([f"{k} = %s" for k in fields.keys()])
        values = tuple(fields.values()) + (journal_id,)
        query = f"UPDATE trip_journals SET {set_clause} WHERE journal_id = %s;"
        return self.execute_query(query, values)

    def delete_journal(self, journal_id: int) -> int:
        return self.execute_query("DELETE FROM trip_journals WHERE journal_id = %s;", (journal_id,))

    # ------------------- Composite / DB-level fetches ------------------- #
    def get_user_full_profile(self, user_id: int) -> Dict:
        """
        Returns a combined object:
        {
            "user": {...},
            "preferences": [...],
            "interests": [...],
            "trips": [...]
        }
        """
        user = self.get_user_by_id(user_id)
        prefs = self.get_prefs_by_user(user_id)
        interests = self.get_interests_by_user(user_id)
        trips = self.get_trips_by_user(user_id)
        return {"user": user, "preferences": prefs, "interests": interests, "trips": trips}

    def get_trip_full_details(self, trip_id: int) -> Dict:
        """
        Returns:
        {
            "trip": {...},
            "itineraries": [...],
            "journals": [...]
        }
        """
        trip = self.get_trip_by_id(trip_id)
        itineraries = self.get_itineraries_by_trip(trip_id)
        journals = self.get_journals_by_trip(trip_id)
        return {"trip": trip, "itineraries": itineraries, "journals": journals}

    def get_trips_with_keyword(self, keyword: str, limit: int = 50) -> List[Dict]:
        q = "SELECT * FROM trips WHERE title ILIKE %s OR city ILIKE %s ORDER BY created_at DESC LIMIT %s;"
        w = f"%{keyword}%"
        return self.execute_query(q, (w, w, limit), fetchall=True)

    # ------------------- Utility ------------------- #
    def count_rows(self, table_name: str) -> int:
        q = f"SELECT COUNT(*) as cnt FROM {table_name};"
        res = self.execute_query(q, fetchone=True)
        return int(res['cnt']) if res else 0

    # ------------------- Clear ------------------- #
    def clear_all(self):
        """
        Delete all rows from every table in the schema.
        Preserves table structure.
        ⚠️ Irreversible operation.
        """
        if not self.cursor:
            raise RuntimeError("DB cursor not initialized. Call connect() first.")

        try:
            tables = ["trip_journals", "itineraries", "trips",
                    "user_interests", "user_preferences", "users"]
            for t in tables:
                self.cursor.execute(f"TRUNCATE TABLE {t} RESTART IDENTITY CASCADE;")
            self.conn.commit()
            print("🧹 All tables cleared successfully.")
        except Exception as e:
            self.conn.rollback()
            print("❌ Failed to clear all tables:", e)
            raise
