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

    # ---------------- Generic Executor ---------------- #
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

    # ------------------- USERS ------------------- #
    def add_user(self, first_name: str, last_name: Optional[str], email: str, password_hash: str) -> Dict:
        """
        Inserts a new user into the users table and returns the created record.
        """
        query = """
            INSERT INTO users (first_name, last_name, email, password_hash)
            VALUES (%s, %s, %s, %s)
            RETURNING *;
        """
        return self.execute_query(query, (first_name, last_name, email, password_hash), fetch='one')

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """
        Fetch a single user record by UUID.
        """
        query = "SELECT * FROM users WHERE user_id = %s;"
        return self.execute_query(query, (user_id,), fetch='one')

    def delete_user(self, user_id: str) -> int:
        """
        Delete a user by UUID. Returns the number of rows deleted.
        """
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


    # ------------------- TRIP ------------------- #
    def add_trip(
            self, 
        user_id: str,
        title: str,
        city: Optional[str] = None,
        country: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        status: Optional[str] = "draft",
        description: Optional[str] = None,
        trip_type: Optional[str] = None,
        total_budget: Optional[float] = None,
        transport_mode_to_city: Optional[str] = None,
        accommodation_type: Optional[str] = None,
        tags: Optional[dict] = None,
        rating: Optional[float] = None,
        favorite_locations: Optional[dict] = None,
    ) -> Dict:
        """
        Inserts a new record into the trips table and returns the created record.
        """
        tags_json = json.dumps(tags) if tags else None
        favorite_locations_json = json.dumps(favorite_locations) if favorite_locations else None

        query = """
            INSERT INTO trips (
                user_id, title, city, country, start_date, end_date, status,
                description, trip_type, total_budget, transport_mode_to_city,
                accommodation_type, tags, rating, favorite_locations
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *;
        """

        return self.execute_query(
            query,
            (
                user_id, title, city, country, start_date, end_date, status,
                description, trip_type, total_budget, transport_mode_to_city,
                accommodation_type, tags_json, rating, favorite_locations_json
            ),
            fetch='one'
        )

    def get_trip_by_id(self, trip_id: str) -> Optional[Dict]:
        """
        Fetch a single trip record by trip_id UUID.
        """
        query = "SELECT * FROM trips WHERE trip_id = %s;"
        return self.execute_query(query, (trip_id,), fetch='one')

    def delete_trip(self, trip_id: str) -> int:
        """
        Delete a trip record by trip_id. Returns the number of rows deleted.
        """
        query = "DELETE FROM trips WHERE trip_id = %s;"
        return self.execute_query(query, (trip_id,))



    # ==============================
    # TRIP JOURNALS FUNCTIONS
    # ==============================

    def add_trip_journal(
        self, 
        trip_id: str,
        day: Optional[int] = None,
        entry_text: Optional[str] = None,
        location: Optional[dict] = None,
        tags: Optional[dict] = None,
        expenses: Optional[dict] = None,
        visited_places: Optional[dict] = None,
        recommended_for_next_time: Optional[str] = None,
        mood: Optional[str] = None,
        travel_companions: Optional[dict] = None,
        transportation_used: Optional[dict] = None,
        summary_generated: Optional[str] = None,
        recommendations_generated: Optional[str] = None,
    ) -> Dict:
        """
        Inserts a new record into the trip_journals table and returns the created record.
        """

        # ✅ Convert all dict fields to JSON strings
        location_json = json.dumps(location) if location else None
        tags_json = json.dumps(tags) if tags else None
        expenses_json = json.dumps(expenses) if expenses else None
        visited_places_json = json.dumps(visited_places) if visited_places else None
        travel_companions_json = json.dumps(travel_companions) if travel_companions else None
        transportation_used_json = json.dumps(transportation_used) if transportation_used else None

        query = """
            INSERT INTO trip_journals (
                trip_id, day, entry_text, location, tags, expenses, visited_places,
                recommended_for_next_time, mood, travel_companions, transportation_used,
                summary_generated, recommendations_generated
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *;
        """

        return self.execute_query(
            query,
            (
                trip_id, day, entry_text, location_json, tags_json, expenses_json,
                visited_places_json, recommended_for_next_time, mood, travel_companions_json,
                transportation_used_json, summary_generated, recommendations_generated
            ),
            fetch='one'
        )

    def get_trip_journals_by_trip_id(self, trip_id: str) -> List[Dict]:
        """
        Fetch all trip_journals records for a given trip UUID.
        """
        query = "SELECT * FROM trip_journals WHERE trip_id = %s;"
        return self.execute_query(query, (trip_id,), fetch='all')

    def delete_trip_journal(self, journal_id: str) -> int:
        """
        Delete a trip_journals record by journal_id. Returns the number of rows deleted.
        """
        query = "DELETE FROM trip_journals WHERE journal_id = %s;"
        return self.execute_query(query, (journal_id,))


    # ==============================
    # ITINERARIES FUNCTIONS
    # ==============================
    def add_itinerary(
            self, 
            trip_id: str,
            days: int,
            pois: Optional[dict] = None
        ) -> Dict:
        """
        Inserts a new record into the itineraries table and returns the created record.
        """
        query = """
            INSERT INTO itineraries (
                trip_id, days, pois
            )
            VALUES (%s, %s, %s)
            RETURNING *;
        """
        return self.execute_query(
            query,
            (trip_id, days, pois),
            fetch='one'
        )

    def get_itineraries_by_trip_id(self, trip_id: str) -> List[Dict]:
        """
        Fetch all itineraries records for a given trip UUID.
        """
        query = "SELECT * FROM itineraries WHERE trip_id = %s;"
        return self.execute_query(query, (trip_id,), fetch='all')

    def delete_itinerary(self, itinerary_id: str) -> int:
        """
        Delete an itineraries record by itinerary_id. Returns the number of rows deleted.
        """
        query = "DELETE FROM itineraries WHERE itinerary_id = %s;"
        return self.execute_query(query, (itinerary_id,))


    # ------------------- Composite / DB-level fetches ------------------- #
    def get_user_full_profile(self,user_id: str) -> Dict:
        """
        Returns a combined object for a user with all related data:
        {
            "user": {...},                # users table
            "details": {...},             # user_details table
            "preferences": {...},         # travel_preferences table
            "interests": [...],           # user_interests table
            "trips": [                    # trips table, each with itineraries and journals
                {
                    "trip": {...},
                    "itineraries": [...],
                    "journals": [...]
                },
                ...
            ]
        }
        """
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