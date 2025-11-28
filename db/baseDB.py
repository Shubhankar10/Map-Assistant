# db_manager.py
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Optional, Any, Dict, List, Tuple
import json


class PostgresDB:
    def __init__(self, host: str, dbname: str, user: str, password: str, port: int = 5432):
        self.host = host
        self.dbname = dbname
        self.user = user
        self.password = password
        self.port = port
        self.conn: Optional[psycopg2.extensions.connection] = None
        self.cursor: Optional[RealDictCursor] = None

    def test(self):
        print("Working fine inside class.")

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
                print(f"[DB] Schema set to: {schema}")
            print("[DB] Database connected successfully")
        except Exception as e:
            print("[DB] Connection failed:", e)
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

    def execute_query(self, query: str, values: Optional[Tuple[Any, ...]] = None, fetch: str = None):
        """
        Simplified query executor.
        - fetch='one'  → returns single row (dict)
        - fetch='all'  → returns list of rows (list[dict])
        - fetch=None   → executes DML (INSERT/UPDATE/DELETE) and returns affected rowcount
        """
        if not self.cursor:
            raise RuntimeError("❌ DB not connected. Call connect() first.")
        try:
            self.cursor.execute(query, values or ())
            result = None

            if fetch == "one":
                result = self.cursor.fetchone()
            elif fetch == "all":
                result = self.cursor.fetchall()

            self.conn.commit()
            return result if fetch else self.cursor.rowcount

        except Exception as e:
            self.conn.rollback()
            print(f"Database Error: {e}")
            raise

    def add_user(self, first_name: str, last_name: Optional[str], email: str, password_hash: str) -> Dict:
        query = """
            INSERT INTO users (first_name, last_name, email, password_hash)
            VALUES (%s, %s, %s, %s)
            RETURNING *;
        """
        return self.execute_query(query, (first_name, last_name, email, password_hash), fetch='one')

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        query = "SELECT * FROM users WHERE user_id = %s;"
        return self.execute_query(query, (user_id,), fetch='one')

    def delete_user(self, user_id: str) -> int:
        query = "DELETE FROM users WHERE user_id = %s;"
        return self.execute_query(query, (user_id,))

    # ------------------- USER DETAIL ------------------- #

    def add_user_details(
            self,
        user_id: str,
        dob: Optional[str] = None,
        gender: Optional[str] = None,
        aadhar_number: Optional[str] = None,
        passport_number: Optional[str] = None,
        driving_license_number: Optional[str] = None,
        spoken_languages: Optional[List[str]] = None,
        understood_languages: Optional[List[str]] = None,
        native_language: Optional[str] = None,
        hometown: Optional[str] = None,
        current_city: Optional[str] = None,
        address: Optional[str] = None,
        phone_number: Optional[str] = None,
        home_lat: Optional[float] = None,
        home_lng: Optional[float] = None,
        dietary_preferences: Optional[List[str]] = None,
    ) -> Dict:
        """
        Inserts a new record into the user_details table and returns the created record.
        """
        query = """
            INSERT INTO user_details (
                user_id, dob, gender, aadhar_number, passport_number,
                driving_license_number, spoken_languages, understood_languages,
                native_language, hometown, current_city, address, phone_number,
                home_lat, home_lng, dietary_preferences
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *;
        """
        return self.execute_query(
            query,
            (
                user_id, dob, gender, aadhar_number, passport_number,
                driving_license_number, spoken_languages, understood_languages,
                native_language, hometown, current_city, address, phone_number,
                home_lat, home_lng, dietary_preferences
            ),
            fetch='one'
        )

    def get_user_details_by_id(self,user_id: str) -> Optional[Dict]:
        """
        Fetch a single user_details record by UUID.
        """
        query = "SELECT * FROM user_details WHERE user_id = %s;"
        return self.execute_query(query, (user_id,), fetch='one')

    def delete_user_details(self, user_id: str) -> int:
        """
        Delete a user_details record by UUID. Returns the number of rows deleted.
        """
        query = "DELETE FROM user_details WHERE user_id = %s;"
        return self.execute_query(query, (user_id,))


    # ------------------- USER INTERESTS ------------------- #
    def add_user_interest(
            self, 
        user_id: str,
        tag: Optional[str] = None,
        sub_tag: Optional[str] = None,
        preferred_vacation_type: Optional[str] = None,
        activity_type: Optional[str] = None,
        frequency_of_interest: Optional[str] = None,
        special_notes: Optional[str] = None,
    ) -> Dict:
        """
        Inserts a new record into the user_interests table and returns the created record.
        """
        query = """
            INSERT INTO user_interests (
                user_id, tag, sub_tag, preferred_vacation_type,
                activity_type, frequency_of_interest, special_notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *;
        """
        return self.execute_query(
            query,
            (
                user_id, tag, sub_tag, preferred_vacation_type,
                activity_type, frequency_of_interest, special_notes
            ),
            fetch='one'
        )

    def get_user_interests_by_user_id(self, user_id: str) -> List[Dict]:
        """
        Fetch all user_interests records for a given user UUID.
        """
        query = "SELECT * FROM user_interests WHERE user_id = %s;"
        return self.execute_query(query, (user_id,), fetch='all')

    def delete_user_interest(self, interest_id: str) -> int:
        """
        Delete a user_interests record by interest_id. Returns the number of rows deleted.
        """
        query = "DELETE FROM user_interests WHERE interest_id = %s;"
        return self.execute_query(query, (interest_id,))

    # ------------------- TRAVEL PREF ------------------- #
    def add_travel_preference(
            self, 
        user_id: str,
        budget_min: Optional[float] = None,
        budget_max: Optional[float] = None,
        transport_pref: Optional[str] = None,
        commute_pref: Optional[str] = None,
        pace: Optional[str] = None,
        travel_duration_preference: Optional[str] = None,
        travel_group_preference: Optional[str] = None,
        preferred_regions: Optional[List[str]] = None,
        season_preference: Optional[str] = None,
        accommodation_type: Optional[str] = None,
        special_needs: Optional[str] = None,
        frequent_travel: Optional[bool] = False,
    ) -> Dict:
        """
        Inserts a new record into the travel_preferences table and returns the created record.
        """
        query = """
            INSERT INTO travel_preferences (
                user_id, budget_min, budget_max, transport_pref, commute_pref,
                pace, travel_duration_preference, travel_group_preference,
                preferred_regions, season_preference, accommodation_type,
                special_needs, frequent_travel
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *;
        """
        return self.execute_query(
            query,
            (
                user_id, budget_min, budget_max, transport_pref, commute_pref,
                pace, travel_duration_preference, travel_group_preference,
                preferred_regions, season_preference, accommodation_type,
                special_needs, frequent_travel
            ),
            fetch='one'
        )

    def get_travel_preference_by_user_id(self, user_id: str) -> Optional[Dict]:
        """
        Fetch a single travel_preferences record by user UUID.
        """
        query = "SELECT * FROM travel_preferences WHERE user_id = %s;"
        return self.execute_query(query, (user_id,), fetch='one')

    def delete_travel_preference(self, user_id: str) -> int:
        """
        Delete a travel_preferences record by user UUID. Returns the number of rows deleted.
        """
        query = "DELETE FROM travel_preferences WHERE user_id = %s;"
        return self.execute_query(query, (user_id,))


    # ------------------- Composite / DB-level fetches ------------------- #
    def get_full_profile(self,user_id: str) -> Dict:
        print("[DB] Fetching Combined User Profile")
        # Fetch main user
        user = self.get_user_by_id(user_id)
        details = self.get_user_details_by_id(user_id)
        preferences = self.get_travel_preference_by_user_id(user_id)
        interests = self.get_user_interests_by_user_id(user_id)
        
        # Fetch trips and their nested itineraries and journals
        # trips_list = []
        # trips = self.get_trips_by_user(user_id)  # assumes function returning list of trips for user
        # for trip in trips:
        #     trip_id = trip['trip_id']
        #     itineraries = self.get_itineraries_by_trip_id(trip_id)
        #     journals = self.get_trip_journals_by_trip_id(trip_id)
        #     trips_list.append({
        #         "trip": trip,
        #         "itineraries": itineraries,
        #         "journals": journals
        #     })
        
        return {
            "user": user,
            "details": details,
            "preferences": preferences,
            "interests": interests,
            # "trips": trips_list
        }

    # ------------------- Utility ------------------- #
    def count_rows(self, table_name: str) -> int:
        q = f"SELECT COUNT(*) as cnt FROM {table_name};"
        res = self.execute_query(q, fetchone=True)
        return int(res['cnt']) if res else 0

    # ------------------- Clear ------------------- #
    def clear_all(self):
        """
        Delete all rows from every table in the new schema.
        Preserves table structure.
        ⚠ Irreversible operation.
        """
        if not self.cursor:
            raise RuntimeError("DB cursor not initialized. Call connect() first.")

        try:
            # Order matters: dependent tables first, then parent (users)
            tables = [
                "user_interests",
                "travel_preferences",
                "user_details",
                "users"
            ]
            for t in tables:
                self.cursor.execute(f"TRUNCATE TABLE {t} RESTART IDENTITY CASCADE;")
            self.conn.commit()
            print("🧹 All tables cleared successfully.")
        except Exception as e:
            self.conn.rollback()
            print("❌ Failed to clear all tables:", e)
            raise